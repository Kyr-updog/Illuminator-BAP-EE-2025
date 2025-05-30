import yaml
import numpy as np


def determine_connected_pairs(Network):           #this function creates an array of all Station pairs in S/R order

    highest_ID = np.max(np.array(np.array(Network)[:,0], dtype = int))  #determine highest ID value in the Network
    ID = np.arange(1, highest_ID + 1)                                   #create ID list with range 1 up to highest ID + 1
    connected_pair_array = np.empty((0, 2))                             #create a blank-by-2 array  
    for i in np.arange(len(ID)):                                        #loop over every ID value
        connected_pair = []                                             #redefine connected_pair list before each ID value
        for model in np.arange(len(Network)):                           #loop over the Network array
            if Network[model][0] == ID[i]:                              #compare Network's 0th element to ID's ith element
                connected_pair.append(Network[model][1])                #add Network's Station element to the connected_pair list
                connected_pair.append(Network[model][2])                #add Network's Sender/Receiver element to list
        if (len(connected_pair) == 0):                                  #if this ID value had no connections, skips
            continue
        
        if ('Sender' in connected_pair[1]):
            connected_pair_array = np.append(connected_pair_array, [[connected_pair[0], connected_pair[2]]], axis=0)
            #add connected Station pair to next row in array in standard order (for S/R) 
        else:    
            connected_pair_array = np.append(connected_pair_array, [[connected_pair[2], connected_pair[0]]], axis=0) 
            #add connected Station pair to next row in array in reverse order (for S/R)                        
    return connected_pair_array



def write_topology(connected_pair_array):
    topology_list = []   
    from_model = ''
    to_model = ''

    for i in range(np.shape(connected_pair_array)[0]):
        if ('Station' in connected_pair_array[i, 0]) and ('Station' in connected_pair_array[i, 1]):
            from_model = connected_pair_array[i, 0]+'.transmit'
            to_model = connected_pair_array[i, 1]+'.receive'
            topology_list.append({'from': from_model, 'to': to_model},)
    return topology_list



def read_and_copy_yaml_data_plus_add_data_to_new_file(filename,write_file, topology):
    with open(f'{filename}.yaml', 'r') as f:        #opens a yaml file to read
        data = yaml.safe_load(f)                    #loads the yaml data in safe mode
    with open(f'{write_file}.yaml', 'w') as file:   #opens a different yaml file to write to
        yaml.dump(data,file,sort_keys=False)        #writes the read yaml data to said different yaml file
        yaml.dump(topology,file,sort_keys=False)    #writes additional topology to said different yaml file
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

    connected_pair_array = determine_connected_pairs(Network)
    print(connected_pair_array)
    topology = write_topology(connected_pair_array)
    print (topology)

    '''topology = [ {'from': 'CSVload.load', 'to': 'Load1.load'},
                {'from' : 'PV', 'to': 'Controller'}, 
                {'from' : 'Wind', 'to': 'Home'}, 
                {'from' : 'Wind', 'to': 'Controller'}
    ]   '''
    read_and_copy_yaml_data_plus_add_data_to_new_file('Tutorial_Power_Balance_b', 'simulation_file')
