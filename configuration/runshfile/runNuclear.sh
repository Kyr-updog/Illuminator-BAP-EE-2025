#! /bin/bash
cd $3/Nuclear
python nuclear_model.py $1:$2 --remote
echo "finished"
