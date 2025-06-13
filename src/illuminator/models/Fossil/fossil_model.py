from illuminator.builder import ModelConstructor

# construct the model
class Fossil(ModelConstructor):
    # Define the model parameters, inputs, outputs, and states
    # Energy conversions:
    # Chemical -> exhaust thermal: inefficiency possible (imperfect combustion; could be different between fossil fuel and biomass)
    # Exhaust thermal -> steam thermal: inefficiency possible (waste heat)
    # Steam thermal -> mechanical pressure: inefficiency possible (waste heat)
    # Mechanical pressure -> rotational: inefficiency possible (friction)
    # Rotational -> electrical: inefficiency possible (waste flux)
    parameters={'fos_type': 'coal',         # Type of fossil fuel (also determines type of biomass): coal, oil, gas (solid, liquid, gas).
                'fos_eff': 1,               # Fraction electrical energy from chemical energy from fossil fuel.
                'bio_eff': 1,               # Fraction electrical energy from chemical energy from biomass.
                'fos_NRG_density': 1,       # Amount of chemical energy per unit of weight (kWh/kg) for the fossil fuel.
                'bio_NRG_density': 1,       # Amount of chemical energy per unit of weight (kWh/kg) for the biomass.
                'fos_specific_emission': 1, # Amount of CO2 emission (kg) per unit of weight (kg) of burned fossil fuel.
                'bio_specific_emission': 1, # Amount of CO2 emission (kg) per unit of weight (kg) of burned biomass.
                'rated_pow': 500,           # Maximum power generation capacity (kW). CONVERT TO MW!!!!!!!!!!!!!!!!!
                'output_type': 'power',     # Output type of the generation, either 'power' (kW) or 'energy' (kWh).
                'name': 'Fossil1'
                }
    inputs={'req_pow': None,       # Required power output (kW) or energy (kWh) based on the chosen output type (power or energy).
            'req_pow_dict': {},
            'bio_frac': 0.2     # Fraction of mass per second ((kg/s)/(kg/s)) burned that is biomass for a given hour.
            }
    outputs={'gen_pow': 0,          # Generated power output (kW) or energy (kWh) based on the chosen output type (power or energy).
             'emission': 0,         # Amount of CO2 emission (kg) for that time step.
             'fossil_fuel_burned': 0, # Amount of fossil fuel (kg) used for that time step.
             'biomass_burned': 0      # Amount of biomass (kg) used for that time step.
             }
    states={'limit_flag': 0         # 0: req_pow within rated power capacity; 1: req_pow greater than rated power capacity
            }
    
    # define other attributes
    time_step_size=1
    time=None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the fossil generator model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
            Additional keyword arguments to initialize the...
        """
        super().__init__(**kwargs)
        self.fos_type = self.parameters['fos_type']
        self.fos_eff = self.parameters['fos_eff']
        self.bio_eff = self.parameters['bio_eff']
        self.fos_NRG_density = self.parameters['fos_NRG_density']
        self.bio_NRG_density = self.parameters['bio_NRG_density']
        self.fos_specific_emission = self.parameters['fos_specific_emission']
        self.bio_specific_emission = self.parameters['bio_specific_emission']
        self.rated_pow = self.parameters['rated_pow']
        self.output_type = self.parameters['output_type']
        self.name = self.parameters['name']

         

    # define step function
    def step(self, time: int, inputs: dict=None, max_advance: int=1) -> None:  # step function always needs arguments self, time, inputs and max_advance. Max_advance needs an initial value.
        """
        Advances the simulation one time step.
        Args:
            time (float): Current simulation time in seconds
            inputs (dict): Dictionary containing input values:
            - req_pow (float): Power required of the generator
            max_advance (int, optional): Maximum time to advance in seconds. Defaults to 1.
        Returns:
            float: Next simulation time in seconds
        """
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible
        self.time = time

        if input_data['req_pow'] is not None:
            req_pow = input_data['req_pow']
        else:
            req_pow = input_data['req_pow_dict'][self.name]
            
        bio_frac = input_data['bio_frac']

        results = self.generation(req_pow, bio_frac)
        self.limit_flag = results.pop('limit_flag')

        self.set_states({'limit_flag': self.limit_flag})
        self.set_outputs(results)

        # return the time of the next step (time until current information is valid)
        return time + self._model.time_step_size
    


    def pow_frac(n1, n2, d1) -> float:
        frac = n1*n2/(n1*n2 + (1-n1)*d1)
        return frac
    
    
    
    def burn_and_emission_rate(mech_pow, eff, NRG_density, specific_emission) -> float:
        # Calculate CO2 emission rate (kg/s)
        chem_pow = mech_pow/eff
        burn_rate = chem_pow/NRG_density
        emission_rate = burn_rate*specific_emission
        return burn_rate, emission_rate
    


    def generation(self, req_pow:float, bio_frac:float) -> dict:
        if req_pow > self.rated_pow:
            limit_flag = 1
        else:
            limit_flag = 0

        # Principle: gen_pow == req_pow
        bio_chem_pow_frac = self.pow_frac(bio_frac, self.bio_NRG_density, self.fos_NRG_density)
        bio_mech_pow_frac = self.pow_frac(bio_chem_pow_frac, self.bio_eff, self.fos_eff)
        
        bio_mech_pow = req_pow*bio_mech_pow_frac
        fos_mech_pow = req_pow - bio_mech_pow

        fos_burn_rate, fos_emission_rate = self.burn_and_emission_rate(fos_mech_pow, self.fos_eff,
                                                                       self.fos_NRG_density, self.fos_specific_emission)
        bio_burn_rate, bio_emission_rate = self.burn_and_emission_rate(bio_mech_pow, self.bio_eff,
                                                                       self.bio_NRG_density, self.bio_specific_emission)
        
        fossil_fuel_burned = fos_burn_rate * self.time_step_size
        biomass_burned = bio_burn_rate * self.time_step_size

        emission = (fos_emission_rate + bio_emission_rate) * self.time_step_size

        re_params = {'gen_pow': req_pow, 'emission': emission, 'fossil_fuel_burned': fossil_fuel_burned,
                     'biomass_burned': biomass_burned, 'limit_flag': limit_flag}
        return re_params