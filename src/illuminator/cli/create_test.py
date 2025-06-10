import yaml

test_size = 100

start = {
    "scenario":{
        "name":"startup",
        "start_time":'2012-01-01 00:00:00',
        "end_time":'2012-01-01 00:15:00',
        "time_resolution":900
    }
}

monitor = {
    "monitor":{
        "file":'./out.csv',
        "items":["requester0.stripList"]
    }
}

models = []

models.append({
    "name":"TopologyCreator",
    "type":"TopologyMaker",
    "parameters":{
        "filename":'examples/Cluster/Tutorial_cluster'
    },
    "inputs":{
        "config":{}
    }
})

for i in range (test_size):
    requester = {
        "name":"requester"+str(i),
        "type":"IDrequester",
        "connect":{
            "ip":"127.0.0.1",
            "port":5000+i
        },
        "parameters":{
            "deviceID":["127.0.0.1", 5000+i]
        },
        "states":{
            "stripList":None
        }
    }
    models.append(requester)

model_dict = {"models":models}

connections = []

for i in range(test_size):
    connection = {
        "from":"requester"+str(i)+".stripList",
        "to":"TopologyCreator.config"
    }
    connections.append(connection)

connections_dict = {
    "connections":connections
}

with open("starter.yaml", 'w') as file:
    yaml.dump(start, file, sort_keys=False)
    yaml.dump(monitor, file, sort_keys=False)
    yaml.dump(model_dict, file, sort_keys=False)
    yaml.dump(connections_dict, file, sort_keys=False)

with open("starter.sh", 'w') as shell_file:
    shell_file.write("#! /bin/bash\n")
    for i in range(test_size):
        shell_file.write(f"lxterminal -e ssh bram@127.0.0.1 './Documenten/Illuminator/configuration/runshfile/runRequester.sh 127.0.0.1 {5000+i} /home/bram/Documenten/Illuminator/src/illuminator/models/'&\n")