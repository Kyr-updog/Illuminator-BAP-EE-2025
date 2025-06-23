
###### Interactivity ##############################################################



from datetime import datetime, date
import time as timer

import signal
from collections import deque
import subprocess

import pandas as pd

import RPi.GPIO as GPIO


SENSOR_PIN = 14  # BCM numbering

# Set up
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

 
data_time = deque(maxlen=10)
data_u = deque(maxlen=10)



#interrupt function
def handle_sigquit(signum, frame):


    global data_time
    new_rows = []
    new_row_load = []
    new_row_sun = []
    
    #specify the input .txt file that is not the interactive model but is in the .yaml file.
    
    #model 1
    df = pd.read_csv('/home/Raspinator/Illuminator/examples/Tutorial1/data/pv_data_Rotterdam_NL-15min.txt', skiprows=1, parse_dates=['Time'])
    df.set_index('Time', inplace=True)
   
    
    # Extract only .txt file time data
    txt_date = datetime.strptime('2012-06-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    df_day = df.loc[str(txt_date.date())].reset_index()
     
    # Combine today's date with original time
    new_date = datetime.now().date()
 
    df_day['Time'] = [datetime.combine(new_date, t.time()) for t in df_day['Time']]
    df_day.set_index('Time',inplace=True)
    sun_df_day = df_day
    
    
    #model 2
    df = pd.read_csv('/home/Raspinator/Illuminator/examples/Tutorial1/data/load_data.txt', skiprows=1, parse_dates=['time'])
    df.set_index('time', inplace=True)
    
    

    txt_date = datetime.strptime('2012-06-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    df_day = df.loc[str(txt_date.date())].reset_index()
     

    new_date = datetime.now().date()

    df_day['time'] = [datetime.combine(new_date, t.time()) for t in df_day['time']]
    df_day.set_index('time',inplace=True)
    
    
    

    
    #Arange the rows that should be added to all input .txt file.
    data_time = list(data_time)
    diffs = [(t2 - t1).total_seconds()  for t1, t2 in zip(data_time, data_time[1:])]
    for i in range(len(diffs)):
        row = f"{list(data_time)[i]},{24*1 / diffs[i]}" #24 is the maximum wind speed level seen in data file. 1second is the maximum speed rotation of the physical wind turbine model.
        new_rows.append(row)
        
        # Find closest row
        target_time = pd.to_datetime(list(data_time)[i])
        
        sun_df_interp = sun_df_day.resample('1T').interpolate('time')
        row = sun_df_interp.reindex([target_time], method='nearest', tolerance=pd.Timedelta('14m'))
        new_row_sun.append(row)
        
        

        df_interp = df_day.resample('1T').interpolate('time')
        row = df_interp.reindex([target_time], method='nearest', tolerance=pd.Timedelta('14m'))
        new_row_load.append(row)
        
        
    #append the iterpolated and interactive model data to the input .txt file.    
    with open('/home/Raspinator/Illuminator/examples/Tutorial1/data/winddata_NL.txt', "a") as file:
        for row in new_rows:   
            file.write(row + "\n" )
            
            
    with open('/home/Raspinator/Illuminator/examples/Tutorial1/data/load_data.txt', "a") as file:
        for row in new_row_load:   
            file.write(row.to_csv(header=False, index=True).strip() + "\n" )

    with open('/home/Raspinator/Illuminator/examples/Tutorial1/data/pv_data_Rotterdam_NL-15min.txt', "a") as file:
        for row in new_row_sun:   
            file.write(row.to_csv(header=False, index=True).strip()   +  "\n")

    # file must be send to master and solar panel slave       
    subprocess.run([
        "scp",
        "/path/to/local/file",                              #Fill in local file path
        "Raspinator@remote_ip:/path/to/remote/destination"  #fill in remote username, ipadress and file destination
    ])            



    code = '''
    #run the simulation 
    CONFIG_FILE = '/home/Raspinator/Illuminator/examples/Tutorial1/Tutorial_Power_Balance_a.yaml'
    simulation_RES = Simulation(CONFIG_FILE)
    simulation_RES.set_model_param(model_name='CSVload', parameter='file_path', value='/home/Raspinator/Illuminator/examples/Tutorial1/data/load_data.txt')
    simulation_RES.set_model_param(model_name='CSV_pv', parameter='file_path', value='/home/Raspinator/Illuminator/examples/Tutorial1/data/pv_data_Rotterdam_NL-15min.txt')
    simulation_RES.set_model_param(model_name='CSV_wind', parameter='file_path', value='/home/Raspinator/Illuminator/examples/Tutorial1/data/winddata_NL.txt')
     
    new_settings = {'Wind1': {'p_rated': 0.3}, # power in kW
                    'Load1': {'houses': 5}, # number of houses
                    'PV1':{'cap': 500} # installed capacity in W
                    }
     
    simulation_RES.edit_models(new_settings)
    print(list(data_time)[0], list(data_time)[-1]) 
    simulation_RES.set_scenario_param('start_time', str(list(data_time)[0]))
    simulation_RES.set_scenario_param('end_time', str(list(data_time)[-1]))
    simulation_RES.set_scenario_param('time_resolution', 1)
     
    # run the simulation
    simulation_RES.run()    
    '''
    with open('simulation_script.py', 'w') as f:
        f.write(f"replace str(list(data_time)[0]) with {str(list(data_time)[0])}")
        f.write(f" replace str(list(data_time)[0]) with {str(list(data_time)[-1])}")
        f.write(code)

    #send only to master.
    subprocess.run([
        "scp",
        "/path/to/local/file",                              #Fill in local file path
        "Raspinator@remote_ip:/path/to/remote/destination"  #fill in remote username, ipadress and file destination
    ])



#create interrupt function
signal.signal(signal.SIGQUIT, handle_sigquit)





#take the last 10samples of the wind_mill



while True:
    if GPIO.input(SENSOR_PIN) == GPIO.LOW:
        print("Signal recognized")
        print(list(data_u))
        now = datetime.now()
        if not list(data_time):
            data_time.append(now.replace(microsecond=0))
            timer.sleep(0.40)      
        elif now.replace(microsecond=0) != list(data_time)[-1]:
            data_time.append(now.replace(microsecond=0))
            timer.sleep(0.40)
        else:
            dummy = 0
        while GPIO.input(SENSOR_PIN) == GPIO.LOW:
            dummy = 0
