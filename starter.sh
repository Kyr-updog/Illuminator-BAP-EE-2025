#! /bin/bash
lxterminal -e ssh Raspinator@127.0.0.1 './Illuminator/configuration/runshfile/runRequester.sh 127.0.0.1 5000 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@127.0.0.1 './Illuminator/configuration/runshfile/runRequester.sh 127.0.0.1 5001 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@127.0.0.1 './Illuminator/configuration/runshfile/runRequester.sh 127.0.0.1 5002 /home/Raspinator/Illuminator/src/illuminator/models/'&
