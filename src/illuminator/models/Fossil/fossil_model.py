# Code to model fossil fuel generators

from illuminator.builder import ModelConstructor

# construct the model
class Fossil(ModelConstructor):
    # Define the model parameters, inputs, outputs...
    # all parameters will be directly available as attributes
    parameters={'fos_type': 'coal',         # Type of fossil fuel (also determines type of biomass): coal, oil, gas.
                'fos_eff': 1,               # Fraction mechanical energy from chemical energy from the fossil fuel.
                'bio_eff': 1,               # Fraction mechanical energy from chemical energy from the biomass.
                'fos_NRG_density': 1,       # Amount of chemical energy per unit of weight (kWh/kg) for the fossil fuel.
                'bio_NRG_density': 1,       # Amount of chemical energy per unit of weight (kWh/kg) for the biomass.
                'fos_specific_emission': 1, # Amount of CO2 emission (kg) per unit of weight (kg) of burned fossil fuel.
                'bio_specific_emission': 1, # Amount of CO2 emission (kg) per unit of weight (kg) of burned biomass.
                'max_pow': 500,             # Maximum power generation capacity (kW).
                'output_type': 'power'      # Output type of the generation, either 'power' (kW) or 'energy' (kWh).
                }
    inputs={'req_pow': 0    # Required power output (kW) or energy (kWh) based on the chosen output type (power or energy).
                            # Alternatively, use tot_pow and let the generator calculate the output.
            }
    outputs={'gen_pow': 0,  # Generated power output (kW) or energy (kWh) based on the chosen output type (power or energy).
             'emission': 0  # Amount of CO2 emission (kg) for that time step.
             }
    states={'bio_frac': 0.2,        # Fraction of mass per second (kg/s) burned that is biomass for a given hour.
            'price': 10,            # Price per unit of energy (euros/kWh) for a given hour.
            'committed_NRG': 1000   # Amount of energy (kWh) committed for a given hour.
            }
    
    # define other attributes
    time_step_size=1
    time=None
    powerout = 0  # Output power for given required power.

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
        self.max_pow = self.parameters['max_pow']
        self.output_type = self.parameters['output_type']
        self.bio_frac = self.states['bio_frac']
        self.price = self.states['price']
        self.committed_NRG = self.states['committed_NRG']
         


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
        self.resolution_h = self.time_resolution / 60 / 60  # convert scenario resolution to hours
        input_data = self.unpack_inputs(inputs)  # make input data easily accessible

        results = self.generation(req_pow=input_data['req_pow'])

        self.set_outputs(results)
        self.set_states({'bio_frac': self.bio_frac})
        self.set_states({'price': self.price})
        self.set_states({'committed_NRG': self.committed_NRG})

        # return the time of the next step (time until current information is valid)
        return time + self._model.time_step_size
    


    def frac(n1, n2, d1):
        frac = n1*n2/(n1*n2 + (1-n1)*d1)
        return frac
    

    
    def emission_rate(mech_pow, eff, NRG_density, specific_emission) -> float:
        # Calculate CO2 emission rate (kg/s)
        chem_pow = mech_pow/eff
        burn_rate = chem_pow/NRG_density
        emission_rate = burn_rate*specific_emission
        return emission_rate
    


    def generation(self, req_pow:float) -> dict:
        # Principle: gen_pow == req_pow
        bio_chem_pow_frac = self.frac(self.bio_frac, self.bio_NRG_density, self.fos_NRG_density)
        bio_mech_pow_frac = self.frac(bio_chem_pow_frac, self.bio_eff, self.fos_eff)
        
        bio_mech_pow = req_pow*bio_mech_pow_frac
        fos_mech_pow = req_pow - bio_mech_pow

        fos_emission_rate = self.emission_rate(fos_mech_pow, self.fos_eff, self.fos_NRG_density, self.fos_specific_emission)
        bio_emission_rate = self.emission_rate(bio_mech_pow, self.bio_eff, self.bio_NRG_density, self.bio_specific_emission)

        emission = (fos_emission_rate + bio_emission_rate) * self.time_step_size

        re_params = {'gen_pow': req_pow, 'emission': emission}
        return re_params