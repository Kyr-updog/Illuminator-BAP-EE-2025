#! /bin/bash
cd $3/Station
python wind_randomizer.py $1:$2 --remote
echo "finished"
