#! /bin/bash
cd $3/Station
python station_model.py $1:$2 --remote
echo "finished"
