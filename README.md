# Goal

The goal of this project is to avoid cats to poop in the garden. A python script uses TensorFlow to detect cats from the IP camera pictures. Once the cat detected the sprinkler is turned on quickly.
This project is based this TensorFlow [classification example](https://www.tensorflow.org/tutorials/images/classification).

# Hardware

- Regular PC with python3, ftp server, webserver, php
The hardware used is a regular computer for a ftp server, webserver, python3 and to run TensorFlow.
- IP camera
The IP camera needs to upload pictures to the FTP server when a motion is detected.
- Solenoid valve
I bought a random motion activated sprinkler that I dissambled for the solenoid valve.
- Raspberry pi (or Wifi arduino)
The solenoid valve is driven by the Raspberry Pi using a relay.

# Software

`pip3 install matplotlib`
`pip3 install numpy`
`apt install libatlas-base-dev`
`apt install libopenjp2-7`
`apt install ffmpeg`

## FTP server

The IP camera is setup to upload pictures to the computer ftp server, as soon as a motion is detected.

## daemon.py

`scripts/daemon.py` is in charge to pick-up the newly uploaded pictures, to move them into `website/images/incoming` directory, and the daemon evaluates each picture. The result of the evaluation is saved into `website/images/incoming/image_name.json` (for `image_name.jpg`).

## MQTT

## Website (PHP)
