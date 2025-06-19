#! /bin/bash
cd $3/Fossil
python fossil_model.py $1:$2 --remote
echo "finished"
