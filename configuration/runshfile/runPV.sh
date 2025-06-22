#! /bin/bash
cd $3/PV
sudo python pv_model_v3.py $1:$2 --remote
echo "finished"