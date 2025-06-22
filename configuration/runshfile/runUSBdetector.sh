#! /bin/bash
cd $3/USBdetector
python USBdetector.py $1:$2 --remote
echo "finished"