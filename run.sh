#! /bin/bash
lxterminal -e ssh Raspinator@127.0.0.1 './Illuminator/configuration/runshfile/runUSBdetector.sh 127.0.0.1 2003 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@127.0.0.1 './Illuminator/configuration/runshfile/runLED_connection.sh 127.0.0.1 5678 /home/Raspinator/Illuminator/src/illuminator/models/'&
