#! /bin/bash
cd $3/Controllers
python pandapower_controller.py $1:$2 --remote
echo "finished"
