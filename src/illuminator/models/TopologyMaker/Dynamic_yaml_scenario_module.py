import yaml
import numpy as np
import csv

def write_LED_portmaps(LED_model):
    LED_model_array = np.asarray(LED_model, dtype=object)
    LED_portmap = []

    for i in np.arange(len(LED_model_array)):
        Pi_IP_address = LED_model_array[i, 0]
        ip_port = LED_model_array[i, 1]
        serial_port = LED_model_array[i, 2]

        LED_portmap.append({'name': f'LED_model_{i+1}', 'type': 'LED_connection', 
                            'connect': {'ip': Pi_IP_address, 'port': ip_port}, 
                            'parameters': {'min_speed': 0, 'max_speed': 0.6, 'direction': 0, 'port': serial_port},
                            'input': {'speed': 5}
                            })
    return LED_portmap

def determine_connected_pairs(Network):           #this function creates an array of all Station pairs in S/R order

    highest_ID = np.max(np.array(np.array(Network)[:,0], dtype = int))  #determine highest ID value in the Network
    ID = np.arange(1, highest_ID + 1)                                   #create ID list with range 1 up to highest ID + 1
    connected_pair_array = np.empty((0, 3))                             #create a blank-by-2 array  
    for i in np.arange(len(ID)):                                        #loop over every ID value
        connected_pair = []                                             #redefine connected_pair list before each ID value
        for model in np.arange(len(Network)):                           #loop over the Network array
            if Network[model][0] == ID[i]:                              #compare Network's 0th element to ID's ith element
                connected_pair.append(Network[model][1])                #add Network's Station element to the connected_pair list
                connected_pair.append(Network[model][2])                #add Network's Sender/Receiver element to list
                connected_pair.append(i+1)
        if (len(connected_pair) == 0):                                  #if this ID value had no connections, skips
            continue
        
        if ('Sender' in connected_pair[1]):
            connected_pair_array = np.append(connected_pair_array, [[connected_pair[0], connected_pair[3], connected_pair[2]]], axis=0)
            #add connected Station pair to next row in array in standard order (for S/R) 
        else:    
            connected_pair_array = np.append(connected_pair_array, [[connected_pair[3], connected_pair[0], connected_pair[2]]], axis=0) 
            #add connected Station pair to next row in array in reverse order (for S/R)                        
    return connected_pair_array



def write_topology(connected_pair_array):
    with open(f'{filename}.yaml', 'r') as f:        #opens a yaml file to read
    data = yaml.safe_load(f)                        #loads the yaml data in safe mode
    topology_list = (data[f'{key}'])                #copies everything under a given "key:" to a list
    data.pop(key)                                   #pops the "key:" and everything underneath
    with open(f'{write_file}.yaml', 'w') as file:   #opens a different yaml file to write to
    yaml.dump(data,file,sort_keys=False)            #writes the original yaml data, excluding the popped key, to said different yaml file
                                                    #the purpose of this operation is to copy the static connections to the topology
                                                    #and then remove them in a new intermediary yaml file
                                                    #this leaves the models: section at the bottom of the file, for the LED_portmapping  
    from_model = ''
    to_model = ''
    line_id = ''

    with open('line_connections.csv', 'w', newline='') as csvfile:
        pass

    for i in range(np.shape(connected_pair_array)[0]):
        if ('Station' in connected_pair_array[i, 0]) and ('Station' in connected_pair_array[i, 1]):
            from_model = connected_pair_array[i, 0]+'.transmit'
            to_model = connected_pair_array[i, 1]+'.receive'
            line_id = 'line_'+connected_pair_array[i, 2]
            
            topology_list.append({'from': from_model, 'to': to_model, 'line_id': line_id})

            with open('line_connections.csv', 'a', newline='') as csvfile:
                line_connector = csv.writer(csvfile, delimiter=' ')
                line_connector.writerow([connected_pair_array[i, 0], connected_pair_array[i, 1], connected_pair_array[i, 2]])
    return topology_list

def read_and_copy_yaml_data_plus_add_data_to_new_file(filename,write_file,LED_portmap):
    with open(f'{filename}.yaml', 'r') as f:        #opens a yaml file to read
        data = yaml.safe_load(f)                    #loads the yaml data in safe mode
    with open(f'{write_file}.yaml', 'w') as file:   #opens a different yaml file to write to
        connections = {'connections' : topology}            #defines a dict with connections: {topology}, to recover the popped
                                                            #connections: section from the original yaml file
        yaml.dump(data,file,sort_keys=False)                #writes the read yaml data to said different yaml file
        yaml.dump(LED_portmap,file, sort_keys=False)        #writes the LED models to the models: section (which should be at the bottom)
        yaml.dump(connections,file,sort_keys=False)         #writes the connections to the connections: section
    print('simulation file connections updated') 
    
if __name__ == "__main":
    Network = [
           [1, 'Station1', 'Sender'], 
           [1, 'Station4', 'Receiver'], 
           [2, 'Station1', 'Receiver'], 
           [2, 'Station2', 'Sender'], 
           [12, 'Station2', 'Sender'], 
           [12, 'Station3', 'Receiver'], 
           [4, 'Station3', 'Receiver'], 
           [4, 'Station4', 'Sender'],
           [7, 'Station2', 'Receiver'],
           [7, 'Station4', 'Sender']
          ]

    #LED_Model = [ip, ip_port, serial_port]
    LED_Model = [['192.168.137.150', 5023, 'dev/ttyACM0'], 
                 ['127.0.0.1', 5023, 'dev/ttyACM1'], 
                 ['127.0.0.1', 5024, 'dev/ttyACM0']
                 ]
    
    LED_portmap = write_LED_portmaps(LED_Model)
    connected_pair_array = determine_connected_pairs(Network)
    print(connected_pair_array)
    topology = write_topology(connected_pair_array)
    print (topology)
    read_and_copy_yaml_data_plus_add_data_to_new_file('Tutorial_Power_Balance_b', 'simulation_file')
