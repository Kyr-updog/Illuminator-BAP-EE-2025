#! /bin/bash
cd $3/Controllers
python controllerT3_fos_nuc.py $1:$2 --remote
echo "finished"
