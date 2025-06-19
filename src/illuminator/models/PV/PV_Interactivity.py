



####### Interactivity ######

import signal

import spidev

from collections import deque

from pvlib import solarposition
from pvlib.location import Location
import pandas as pd
from datetime import datetime, date
import time as timee


import requests

import subprocess




API_KEY = "456db28b094c717c8b7e5a3e0d4fb4d0"
LAT = 52.0116   # Delft latitude
LON = 4.3571    # Delft longitude


spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1350000

location = (LAT, LON)  # Delft (lat, lon) 
 
# Create location object
site = Location(LAT, LON)

 
data_time = deque(maxlen=10)
data_G_Gh = deque(maxlen=10)
data_G_Dh = deque(maxlen=10)
data_G_Bn = deque(maxlen=10)
data_Ta = deque(maxlen=10)
data_hs = deque(maxlen=10)
data_FF = deque(maxlen=10)
data_Az = deque(maxlen=10)


#interrupt function
def handle_sigquit(signum, frame):
    
    new_rows = []
    new_row_load = []
    new_row_wind = []
    
    #specify the input .txt file that is not the interactive model but is in the .yaml file.
    
    #model 1
    df = pd.read_csv('/home/Raspinator/Illuminator/examples/Tutorial1/data/winddata_NL.txt', skiprows=1, parse_dates=['time'])
    df.set_index('time', inplace=True)
    
    
    # Extract only .txt file time data
    txt_date = datetime.strptime('2012-06-01 00:00:00', '%Y-%m-%d %H:%M:%S')  # time where data should be extrapolated from
    df_day = df.loc[str(txt_date.date())].reset_index()
     
    # Combine today's date with original time
    new_date = datetime.now().date()
 
    df_day['time'] = [datetime.combine(new_date, t.time()) for t in df_day['time']]
    df_day.set_index('time',inplace=True)
    wind_df_day = df_day
    
    
    #model 2
    df = pd.read_csv('/home/Raspinator/Illuminator/examples/Tutorial1/data/load_data.txt', skiprows=1, parse_dates=['time'])
    df.set_index('time', inplace=True)
    
    

    txt_date = datetime.strptime('2012-06-01 00:00:00', '%Y-%m-%d %H:%M:%S')  # time where data should be extrapolated from
    df_day = df.loc[str(txt_date.date())].reset_index()
     

    new_date = datetime.now().date()

    df_day['time'] = [datetime.combine(new_date, t.time()) for t in df_day['time']]
    df_day.set_index('time',inplace=True)
    
    
    

    
    #Arange the rows that should be added to all input .txt file.
    for i in range(len(list(data_Az))):
        row = f"{list(data_time)[i]},{list(data_G_Gh)[i]},{list(data_G_Dh)[i]},{list(data_G_Bn)[i]},{list(data_Ta)[i]},{list(data_hs)[i]},{list(data_FF)[i]},{list(data_Az)[i]}"
        new_rows.append(row)
        
        # Find closest row for interpolation
        target_time = pd.to_datetime(list(data_time)[i])
        
        wind_df_interp = wind_df_day.resample('1T').interpolate('time')
        row = wind_df_interp.reindex([target_time], method='nearest', tolerance=pd.Timedelta('14m'))
        new_row_wind.append(row)
        
        

        df_interp = df_day.resample('1T').interpolate('time')
        row = df_interp.reindex([target_time], method='nearest', tolerance=pd.Timedelta('14m'))
        new_row_load.append(row)
        
        
    #append the iterpolated and interactive model data to the input .txt file.    
    with open('/home/Raspinator/Illuminator/examples/Tutorial1/data/pv_data_Rotterdam_NL-15min.txt', "a") as file:
        for row in new_rows:   
            file.write(row + "\n" )
            
            
    with open('/home/Raspinator/Illuminator/examples/Tutorial1/data/load_data.txt', "a") as file:
        for row in new_row_load:   
            file.write(row.to_csv(header=False, index=True).strip() + "\n" )

    with open('/home/Raspinator/Illuminator/examples/Tutorial1/data/winddata_NL.txt', "a") as file:
        for row in new_row_wind:   
            file.write(row.to_csv(header=False, index=True).strip()   +  "\n")

    # file must be send to master and wind turbine slave       
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

#read photoresistor
def read_channel(channel):
    adc=spi.xfer2([1,  (8+channel) << 4 ,0 ])
    data = ((adc[1]&3) <<8 ) +adc[2]
    return data
    



#take the last 10samples of the solar pannel
print("Running. Press Ctrl+\\ (backslash) to send SIGQUIT.")
while True:
    print(list(data_G_Gh))
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    now = datetime.now()
    if not list(data_time):
        data_time.append(datetime.now().replace(microsecond=0))
        data_G_Gh.append(read_channel(0)/1023*900)
        data_G_Dh.append(read_channel(0)/1023*900)
        data_G_Bn.append(0)
        data_Ta.append(response.json()['main']['temp'])
        data_hs.append(solarposition.get_solarposition(pd.Timestamp('now', tz='Europe/Amsterdam'), location[0], location[1])['elevation'].iloc[0])
        data_FF.append(response.json()['wind']['speed'])
        data_Az.append(solarposition.get_solarposition(pd.Timestamp('now', tz='Europe/Amsterdam'), location[0], location[1])['azimuth'].iloc[0])
        timee.sleep(0.40)      
    elif now.replace(microsecond=0) != list(data_time)[-1]:
        data_time.append(datetime.now().replace(microsecond=0))
        data_G_Gh.append(read_channel(0)/1023*900)
        data_G_Dh.append(read_channel(0)/1023*900)
        data_G_Bn.append(0)
        data_Ta.append(response.json()['main']['temp'])
        data_hs.append(solarposition.get_solarposition(pd.Timestamp('now', tz='Europe/Amsterdam'), location[0], location[1])['elevation'].iloc[0])
        data_FF.append(response.json()['wind']['speed'])
        data_Az.append(solarposition.get_solarposition(pd.Timestamp('now', tz='Europe/Amsterdam'), location[0], location[1])['azimuth'].iloc[0])
        timee.sleep(0.40)
    else:
        dummy = 0



