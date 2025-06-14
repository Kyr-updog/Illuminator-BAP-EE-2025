from illuminator.builder import ModelConstructor
import pandapower as pp
import pandas as pd
import time

# construct the model
class PandaController(ModelConstructor):
    # Define the model parameters, inputs, outputs, and states
    parameters={'peripherals': {},
                'stations': {},                    
                'ps_connections': {},
                'ss_connections': {},
                'lines_file_path': 'line_specs.csv' # File contains line ID's with their reactances and capacities
                }
    inputs={'ncp_powers': {}
            }
    outputs={} # No outputs
    states={'cp_powers': {},
            'tl_powers': {},
            'one_l_congestion': 0,
            'max_congested': None,
            'max_congested_all': 0,
            'independence': 0,
            'execution_time': 0
            }
    
    # define other attributes
    time_step_size=1
    time=None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the analyzer/controller model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the...
        """
        super().__init__(**kwargs)
        self.peripherals = self.parameters['peripherals']
        self.stations = self.parameters['stations']
        self.ps_connections = self.parameters['ps_connections']
        self.ss_connections = self.parameters['ss_connections']
        self.lines_file_path = self.parameters['lines_file_path']

        # Build graph here !!!
        self.net = pp.create_empty_network()

        # Buses
        for station, kv in self.stations:
            pp.create_bus(self.net, vn_kv=kv, name=station)

        # Lines and Transformers
        self.lines_df = pd.read_csv(self.lines_file_path, decimal='.')

        self.transformers_from_stations = {}

        for line_id, connection in self.ss_connections:
            line = self.lines_df[f'line_{self.lines_df['line_id']}' == line_id]
            max_i_ka = (line['capacity'])/line['prim_kv_rating'] # Capacity in MW
            if line['tf'] == 0:
                from_bus = pp.get_element_index(self.net, 'bus', connection[0])
                to_bus = pp.get_element_index(self.net, 'bus', connection[1])
                pp.create_line_from_parameters(self.net, from_bus, to_bus, length_km=line['length_km'], r_ohm_per_km=0, x_ohm_per_km=line['X_per_km'], c_nf_per_km=0,
                                           r0_ohm_per_km=0, x0_ohm_per_km=0, c0_nf_per_km=0, max_i_ka=max_i_ka, name=line_id, max_loading_percent=100, parallel=line['parallel'])
            else:
                kvs = {}
                kvs[connection[0]] = self.stations[connection[0]]
                kvs[connection[1]] = self.stations[connection[1]]
                high_station = max(kvs, key=kvs.get)
                if high_station == connection[0]:
                    self.transformers_from_stations[line_id] = 'high'
                else:
                    self.transformers_from_stations[line_id] = 'low'
                low_station = min(kvs, key=kvs.get)
                hv_bus = pp.get_element_index(self.net, 'bus', high_station)
                lv_bus = pp.get_element_index(self.net, 'bus', low_station)
                X_ohm = line['length_km'] * line['X_per_km']
                vk = X_ohm * 1000*max_i_ka
                vk_percent = 100 * vk/(1000*line['prim_kv_rating'])
                pp.create_transformer_from_parameters(self.net, hv_bus, lv_bus, sn_mva=line['capacity'], vn_hv_kv=kvs[high_station], vn_lv_kv=kvs[low_station], vkr_percent=0, vk_percent=vk_percent, pfe_kw=0,
                                                      i0_percent=0, vector_group='Dyn', vk0_percent=0, vkr0_percent=0, mag0_percent=0, mag0_rx=0, si0_hv_partial=0, name=line_id, max_loading_percent=100, parallel=line['parallel'])

        # Peripherals
        ncps = ['PV', 'Wind', 'Load'] # Excluding nuclear, because that one gets special treatment
        for name, specs in self.peripherals:
            bus_index = pp.get_element_index(self.net, 'bus', specs['station'])
            if specs['type'] == ncps:
                pp.create_load(self.net, bus_index, p_mw=10, controllable=False, name=name) # Negative load is generation
            elif specs['type'] == 'Nuclear':
                pp.create_load(self.net, bus_index, p_mw=specs['rated_pow'], controllable=False, name=name)
            elif specs['type'] == 'Fossil':
                fossil = pp.create_gen(self.net, bus_index, p_mw=10, min_p_mw=0, max_p_mw=specs['rated_pow'], controllable=True, name=name)
                pp.create_poly_cost(self.net, fossil, 'gen', cp1_eur_per_mw=specs['emission_rate'])
            elif specs['type'] == 'GridConnection':
                power_limit = specs['connection_capacity']
                connection = pp.create_ext_grid(self.net, bus_index, min_p_mw=-power_limit, max_p_mw=power_limit, name=name)
                pp.create_poly_cost(self.net, connection, 'ext_grid', cp1_eur_per_mw=1000)
            elif specs['type'] == 'Battery':
                power_limit = specs['max_p']
                battery = pp.create_storage(self.net, bus_index, p_mw=10, max_e_mwh=specs['max_energy'], soc_percent=specs['init_soc'], min_p_mw=-power_limit, max_p_mw=power_limit, controllable=True, in_service=True, name=name) # Update Battery_v3.py!!!!!!!!!!!!!!!!!
                pp.create_poly_cost(self.net, battery, 'storage', cp1_eur_per_mw=0)
            else:
                pass

            self.max_congested = ['None', -1]

    # define step function
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.
        Args:
            time (float): Current simulation time in seconds
            inputs (dict): Dictionary containing input values:
                -
            max_advance (int, optional): Maximum time to advance in seconds. Defaults to 1.
        Returns:
            float: Next simulation time in seconds
        """
        start = time.time()

        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time

        ncp_powers = input_data['ncp_powers']

        results = self.control_and_analyze(ncp_powers)

        end = time.time()

        execution_time = end - start

        results['execution_time'] = execution_time

        self.set_states(results)

        # return the time of the next step (time until current information is valid)
        return time + self._model.time_step_size
    


    def control_and_analyze(self, ncp_powers) -> dict:

        total_load = 0
        total_supply_from_grid = 0

        for element in ncp_powers:
            name = list(element.keys())[0]
            if self.peripherals[name]['type'] != 'Nuclear':
                ncp_index = pp.get_element_index(self.net, 'load', name)
                self.net.load.at[ncp_index, 'pm_w'] = -element[name]
                if self.peripherals[name]['type'] == 'Load':
                    total_load += -element[name]
            else:
                pass

        pp.rundcopp(self.net, delta=1e-16)

        cp_powers = {}
        tl_powers = {}
        SoCs = {}


        for name, specs in self.peripherals:
            if specs['type'] == 'Fossil':
                fos_index = pp.get_element_index(self.net, 'gen', name)
                fos_results = self.net.res_gen.iloc[fos_index]
                cp_powers.setdefault(specs['station'], {})[name] = fos_results['p_mw']
            elif specs['type'] == 'GridConnection':
                grid_index = pp.get_element_index(self.net, 'ext_grid', name)
                grid_results = self.net.res_ext_grid.iloc[grid_index]
                cp_powers.setdefault(specs['station'], {})[name] = grid_results['p_mw']
                total_supply_from_grid += grid_results['p_mw']
            elif specs['type'] == 'Battery': # Manually adjust SoC
                bat_index = pp.get_element_index(self.net, 'storage', name)
                bat_results = self.net.res_storage.iloc[bat_index]
                cp_powers.setdefault(specs['station'], {})[name] = bat_results['p_mw']
            else:
                pass

        independence = total_supply_from_grid/total_load

        int_max_congested = ['None', -1]

        for line_id, connection in self.ss_connections:
            line = self.lines_df[f'line_{self.lines_df['line_id']}' == line_id]
            if line['tf'] == 0:
                line_index = pp.get_element_index(self.net, 'line', line_id)
                line_results = self.net.res_line.iloc[line_index]
                tl_powers.setdefault(connection[0], {})[line_id] = line_results['p_from_mw']
                congestion = abs(line_results['p_from_mw']) / (self.net.line.at[line_index, 'max_i_ka'] * self.stations[connection[0]]['kv'])
            else:
                trafo_index = pp.get_element_index(self.net, 'trafo', line_id)
                trafo_results = self.net.res_trafo.iloc[trafo_index]
                if self.transformers_from_stations[line_id] == 'high':
                    tl_powers.setdefault(connection[0], {})[line_id] = trafo_results['p_hv_mw']
                    congestion = abs(trafo_results['p_hv_mw']) / self.net.trafo.at[trafo_index, 'sn_mva']
                else:
                    tl_powers.setdefault(connection[0], {})[line_id] = trafo_results['p_lv_mw']
                    congestion = abs(trafo_results['p_lv_mw']) / self.net.trafo.at[trafo_index, 'sn_mva']
            if line_id == 'line_1':
                one_l_congestion = congestion
            if congestion > int_max_congested[1]:
                int_max_congested = [line_id, congestion]

        max_all = int_max_congested[1]
        if max_all > self.max_congested[1]:
            self.max_congested = int_max_congested

        re_params = {'cp_powers': cp_powers, 'tl_powers': tl_powers, 'one_l_congestion': one_l_congestion, 'max_congested': self.max_congested[0], 'max_congested_all': max_all, 'independence': independence} # Also battery SoC

        return re_params

        