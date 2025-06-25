from illuminator.builder import ModelConstructor
import pandapower as pp
import pandas as pd
import time as tee
import numpy as np
import pandapower as pp
import pandapower.networks as nw
import pandapower.plotting as plot
import matplotlib.pyplot as plt
colors = ["b", "g", "r", "c", "y"]

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
            'max_congested_all': 0,
            'independence': 0,
            'execution_time': 0,
            'incoming': 0,
            'outgoing': 0
            }
    
    # define other attributes
    time_step_size=1
    time=None

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the analyzer/controller model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the...
        """
        super().__init__(**kwargs)
        self.peripherals = self._model.parameters.get('peripherals')
        self.stations = self.parameters['stations']
        self.ps_connections = self.parameters['ps_connections']
        self.ss_connections = self.parameters['ss_connections']
        self.lines_file_path = self.parameters['lines_file_path']
        #self.time_resolution = 1800

        # Build graph here !!!
        self.net = pp.create_empty_network()

        # Buses
        for station, kv in self.stations.items():
            pp.create_bus(self.net, vn_kv=kv, name=station)

        # Lines and Transformers
        self.lines_df = pd.read_csv(self.lines_file_path, decimal='.')

        self.transformers_from_stations = {}

        for line_id, connection in self.ss_connections.items():
            text, id = line_id.split('_')
            id = int(id)
            line = self.lines_df[self.lines_df['line_id'] == id]
            print(line['tf'])
            max_i_ka = line['capacity'] # Capacity in kA
            if line['tf'].iloc[0] == 0:
                from_bus = pp.get_element_index(self.net, 'bus', connection[0])
                to_bus = pp.get_element_index(self.net, 'bus', connection[1])
                #pp.create_line(self.net, from_bus, to_bus, length_km=line['length_km'], std_type='149-AL1/24-ST1A 110.0', max_loading_percent=50, name=line_id)
                pp.create_line_from_parameters(self.net, from_bus, to_bus, length_km=line['length_km'], r_ohm_per_km=0, x_ohm_per_km=line['X_per_km'], c_nf_per_km=0,
                                           r0_ohm_per_km=0, x0_ohm_per_km=0, c0_nf_per_km=0, max_i_ka=max_i_ka, name=line_id, max_loading_percent=100)
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
                #pp.create_transformer(self.net, hv_bus, lv_bus, std_type="100 MVA 220/110 kV", max_loading_percent=50, name=line_id)
                pp.create_transformer_from_parameters(self.net, hv_bus, lv_bus, sn_mva=max_i_ka*line['prim_kv_rating'], vn_hv_kv=kvs[high_station], vn_lv_kv=kvs[low_station], vkr_percent=0, vk_percent=vk_percent, pfe_kw=0,
                                                     i0_percent=0, vector_group='Dyn', vk0_percent=0, vkr0_percent=0, mag0_percent=0, mag0_rx=0, si0_hv_partial=0, name=line_id, max_loading_percent=100)
        #self.net.line.to_csv('lines.csv')
        # Peripherals
        ncps = ['PV', 'Wind', 'Load'] # Excluding nuclear, because that one gets special treatment
        for name, specs in self.peripherals.items():
            bus_index = pp.get_element_index(self.net, 'bus', specs['station'])
            if specs['type'] in ncps:
                pp.create_load(self.net, bus_index, p_mw=10, controllable=False, name=name) # Negative load is generation
            elif specs['type'] == 'Nuclear':
                pp.create_load(self.net, bus_index, p_mw=specs['rated_pow'], controllable=False, name=name)
            elif specs['type'] == 'Fossil':
                fossil = pp.create_gen(self.net, bus_index, p_mw=10, min_p_mw=0, max_p_mw=specs['rated_pow'], vm_pu=1.0, controllable=True, name=name)
                if specs['fos_type'] == 'coal':
                    pp.create_poly_cost(self.net, fossil, 'gen', cp1_eur_per_mw=specs['coal_emission_rate'])
                elif specs['fos_type'] == 'gas':
                    pp.create_poly_cost(self.net, fossil, 'gen', cp1_eur_per_mw=specs['gas_emission_rate'])
                else:
                    pp.create_poly_cost(self.net, fossil, 'gen', cp1_eur_per_mw=specs['bio_emission_rate'])
            elif specs['type'] == 'GridConnection':
                power_limit = specs['connection_capacity']
                connection = pp.create_ext_grid(self.net, bus_index, min_p_mw=-power_limit, max_p_mw=power_limit, name=name)
                pp.create_pwl_cost(self.net, connection, 'ext_grid', [[-100000,0,0],[0,100000,100000]])
                #pp.create_poly_cost(self.net, connection, 'ext_grid', cp1_eur_per_mw=10)
            """
            elif specs['type'] == 'Battery':
                power_limit = specs['max_p']
                min_p_mw = max(-power_limit, -specs['soc_init']*specs['max_energy']/(1800.0/3600.0))
                max_p_mw = min(power_limit, (1-specs['soc_init'])*specs['max_energy']/(1800.0/3600.0))
                battery = pp.create_storage(self.net, bus_index, p_mw=10, max_e_mwh=specs['max_energy'], min_e_mwh=0, soc_percent=specs['soc_init'], min_p_mw=min_p_mw, max_p_mw=max_p_mw, controllable=True, in_service=True, name=name) # Update Battery_v3.py!!!!!!!!!!!!!!!!!
                pp.create_poly_cost(self.net, battery, 'storage', cp1_eur_per_mw=0)
            elif specs['type'] == 'LoadEV':
                ev = pp.create_load(self.net, bus_index, p_mw=10, min_p_mw=0, max_p_mw=1000, vm_pu=1.0, controllable=True, name=name)
                pp.create_poly_cost(self.net, ev, 'load', cp1_eur_per_mw=1000)
            elif specs['type'] == 'LoadHeatpump':
                hp = pp.create_load(self.net, bus_index, p_mw=10, min_p_mw=0, max_p_mw=1000, vm_pu=1.0, controllable=True, name=name)
                pp.create_poly_cost(self.net, hp, 'load', cp1_eur_per_mw=1000)
            """
                
        
        #self.net.gen.to_csv('gens.csv')
        #self.max_congested = ['None', -1]
        """
        plot.create_generic_coordinates(self.net, respect_switches=False)
        sizes = plot.get_collection_sizes(self.net)
        bc = plot.create_bus_collection(self.net, self.net.bus.index, size=sizes['bus'], color='b', zorder=10)
        tlc, tpc = plot.create_trafo_collection(self.net, self.net.trafo.index, color="g", size=sizes['trafo'])
        lcd = plot.create_line_collection(self.net, self.net.line.index, color="grey", linewidths=0.5, use_bus_geodata=True)
        sc = plot.create_bus_collection(self.net, self.net.ext_grid.bus.values, patch_type="rect", size=sizes['ext_grid'], color="y", zorder=11)
        plot.draw_collections([lcd, bc, tlc, tpc, sc], figsize=(8,6))
        plt.savefig('network.png')
        """

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
        start = tee.time()

        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time

        ncp_powers = input_data['ncp_powers']
        results = self.control_and_analyze(ncp_powers)

        end = tee.time()

        execution_time = end - start

        results['execution_time'] = execution_time

        self.set_states(results)

        # return the time of the next step (time until current information is valid)
        return time + self._model.time_step_size
    


    def control_and_analyze(self, ncp_powers) -> dict:
        total_power = 0
        total_load = 0
        total_supply_from_grid = 0
        
        blacklist = ['PV', 'Wind']
        for element in ncp_powers:
            name = list(element.keys())[0]
            if self.peripherals[name]['type'] not in blacklist:
                ncp_index = pp.get_element_index(self.net, 'load', name)
                self.net.load.at[ncp_index, 'p_mw'] = -element[name]
                if name == 'PV1':
                    incoming = self.net.load.at[ncp_index, 'p_mw']
                if self.peripherals[name]['type'] == 'Load':
                    total_load += -element[name]
                total_power += element[name]
            else:
                ncp_index = pp.get_element_index(self.net, 'load', name)
                self.net.load.at[ncp_index, 'p_mw'] = 0


        pp.rundcopp(self.net, delta=1e-16)

        cp_powers = {}
        tl_powers = {}
        SoCs = {}
        outgoing = 0

        generator_outputs = []
        for name, specs in self.peripherals.items():
            if specs['type'] == 'Fossil':
                fos_index = pp.get_element_index(self.net, 'gen', name)
                fos_results = self.net.res_gen.at[fos_index, 'p_mw']
                if name == 'FossilCoal1':
                    outgoing = fos_results
                cp_powers.setdefault(specs['station'], {})[name] = fos_results
                generator_outputs.append(fos_results)
                total_power += fos_results
            elif specs['type'] == 'GridConnection':
                grid_index = pp.get_element_index(self.net, 'ext_grid', name)
                grid_results = self.net.res_ext_grid.at[grid_index, 'p_mw']
                cp_powers.setdefault(specs['station'], {})[name] = grid_results
                total_supply_from_grid += grid_results
                total_power += grid_results
            elif specs['type'] == 'Battery': # Manually adjust SoC
                bat_index = pp.get_element_index(self.net, 'storage', name)
                bat_results = self.net.res_storage.at[bat_index, 'p_mw']
                cp_powers.setdefault(specs['station'], {})[name] = bat_results
                max_e = specs['max_energy']
                power_limit = specs['max_p']
                soc_old = self.net.storage.at[bat_index, 'soc_percent']
                soc_new = soc_old + bat_results*self.time_resolution/3600 / max_e
                min_p_mw = max(-power_limit, -soc_new*max_e/(self.time_resolution/3600))
                max_p_mw = min(power_limit, (1-soc_new)*max_e/(self.time_resolution/3600))
                self.net.storage.at[bat_index, 'min_p_mw'] = min_p_mw
                self.net.storage.at[bat_index, 'max_p_mw'] = max_p_mw
            elif specs['type'] == 'LoadEV':
                EV_index = pp.get_element_index(self.net, 'load', name)
                EV_results = self.net.res_load.at[EV_index, 'p_mw']
                cp_powers.setdefault(specs['station'], {})[name] = EV_results
            elif specs['type'] == 'LoadHeatpump':
                HP_index = pp.get_element_index(self.net, 'load', name)
                HP_results = self.net.res_load.at[HP_index, 'p_mw']
                cp_powers.setdefault(specs['station'], {})[name] = HP_results
            else:
                pass

        

        for station in self.stations.keys():
            cp_powers.setdefault(station, {})['key'] = 'value'

        independence = total_supply_from_grid/total_load
        int_max_congested = ['None', -1]
        one_l_congestion = 0

        for line_id, connection in self.ss_connections.items():
            text, id = line_id.split('_')
            id = int(id)
            line = self.lines_df[self.lines_df['line_id'] == id]
            if line['tf'].iloc[0] == 0:
                line_index = pp.get_element_index(self.net, 'line', line_id)
                line_results = self.net.res_line.iloc[line_index]
                tl_powers.setdefault(connection[0], {})[line_id] = line_results['p_from_mw']
                congestion = abs(line_results['p_from_mw']) / (self.net.line.at[line_index, 'max_i_ka'] * self.stations[connection[0]])
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

        for station in self.stations.keys():
            tl_powers.setdefault(station, {})['key'] = 'value'

        max_all = int_max_congested[1]
        #if max_all > self.max_congested[1]:
            #self.max_congested = int_max_congested

        self.net.load.to_csv('res_load.csv')
        self.net.res_line.to_csv('res_line.csv')
        self.net.res_bus.to_csv('res_bus.csv')
        self.net.res_trafo.to_csv('res_trafo.csv')
        self.net.res_gen.to_csv('res_gen.csv')
        with open("res_cost.txt", "w") as text_file:
            text_file.write("Cost: %s" % int(self.net.res_cost))

        re_params = {'cp_powers': cp_powers, 'tl_powers': tl_powers, 'one_l_congestion': one_l_congestion, 'max_congested_all': max_all, 'independence': independence, 'incoming': 0, 'outgoing': outgoing} # Also battery SoC

        return re_params

        
