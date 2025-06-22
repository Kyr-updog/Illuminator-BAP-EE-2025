from illuminator.builder import ModelConstructor

# construct the model
class Nuclear(ModelConstructor):
    # Define the model parameters, inputs, outputs, and states
    parameters={'fuel_type': 'uranium-235', # Type of fuel.
                'efficiency': 1,            # Fraction electrical energy from nuclear energy.
                'NRG_density': 1,           # Amount of chemical energy per unit of weight (kWh/kg) of the nuclear fuel.
                'specific_waste': 1,        # Amount of waste (kg) per unit of weight (kg) of 'burned' fuel.
                'rated_pow': 500,           # Maximum power generation capacity (kW).
                'output_type': 'power'      # Output type of the generation, either 'power' (kW) or 'energy' (kWh).
                }
    inputs={}
    outputs={'gen_pow': 0,              # Generated power output (kW) or energy (kWh) based on the chosen output type (power or energy).
             'waste_produced': 0,       # Amount of waste (kg) for that time step.
             'fuel_burned': 0           # Amount of fuel (kg) used for that time step.
             }
    states={}
    
    # define other attributes
    time_step_size=1
    time=None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the nuclear generator model with the provided parameters.

        Parameters
        ----------
        kwargs : dict
                Additional keyword arguments to initialize the...
        """
        super().__init__(**kwargs)
        self.fuel_type = self.parameters['fuel_type']
        self.efficiency = self.parameters['efficiency']
        self.NRG_density = self.parameters['NRG_density']
        self.specific_waste = self.parameters['specific_waste']
        self.rated_pow = self.parameters['rated_pow']
        self.output_type = self.parameters['output_type']

         

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
        self.time = time

        results = self.generation()
        self.set_outputs(results)

        # return the time of the next step (time until current information is valid)
        return time + self._model.time_step_size
    
    
    @staticmethod
    def burn_and_waste_rate(gen_pow, eff, NRG_density, specific_waste) -> float:
        # Calculate CO2 emission rate (kg/s)
        atomic_pow = gen_pow/eff
        burn_rate = atomic_pow/NRG_density
        waste_rate = burn_rate*specific_waste
        return burn_rate, waste_rate
    


    def generation(self) -> dict:
        gen_pow = self.rated_pow

        burn_rate, waste_rate = self.burn_and_waste_rate(gen_pow, self.efficiency, self.NRG_density, self.specific_waste)
        
        fuel_burned = burn_rate * self.time_step_size
        waste_produced = waste_rate * self.time_step_size

        re_params = {'gen_pow': gen_pow, 'waste_produced': waste_produced, 'fuel_burned': fuel_burned}
        return re_params
    