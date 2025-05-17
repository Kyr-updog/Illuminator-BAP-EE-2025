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
    outputs={'gen_pow': 0,          # Generated power output (kW) or energy (kWh) based on the chosen output type (power or energy).
             'waste': 0,            # Amount of waste (kg) for that time step.
             'fuel_used': 0         # Amount of fuel (kg) used for that time step.
             }
    states={'active': 0,            # 0: inactive; 1: active
            }
    
    # define other attributes
    time_step_size=1
    time=None