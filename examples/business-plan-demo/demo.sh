lxterminal -e ssh Raspinator@192.168.0.6 './Illuminator/configuration/runshfile/runPV.sh 192.168.0.6 5100 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@192.168.0.10 './Illuminator/configuration/runshfile/runBattery.sh 192.168.0.10 5100 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@192.168.0.11 './Illuminator/configuration/runshfile/runLoad.sh 192.168.0.11 5100 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@192.168.0.9 './Illuminator/configuration/runshfile/runWind.sh 192.168.0.9 5100 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@192.168.0.6 './Illuminator/configuration/runshfile/runLED_connection.sh 192.168.0.6 5000 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@192.168.0.9 './Illuminator/configuration/runshfile/runLED_connection.sh 192.168.0.9 5000 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@192.168.0.10 './Illuminator/configuration/runshfile/runLED_connection.sh 192.168.0.10 5000 /home/Raspinator/Illuminator/src/illuminator/models/'&
lxterminal -e ssh Raspinator@192.168.0.11 './Illuminator/configuration/runshfile/runLED_connection.sh 192.168.0.11 5000 /home/Raspinator/Illuminator/src/illuminator/models/'&