# Goal

The goal of this project is to avoid cats to poop in the garden. To do so, a camera is used to detect cats, and turn on the sprinkler quickly. This project is based on TensorFlow, and the training is described in this example [classification](https://www.tensorflow.org/tutorials/images/classification).

# Hardware

The hardware used is a regular computer for a ftp server and to run TensorFlow, an IP camera (I use Foscam FI9900P), a Raspberry Pi to trigger the sprinkler (an WiFi arduino can be used) and a solenoid valve (I used a random motion activated sprinkler that I dissambled for the solenoid valve).
The solenoid valve is drived by a relay plugged to the Raspberry Pi.

# Software

## FTP server

The IP camera is setup to upload pictures to the computer ftp server, as soon as a motion is detected.

## daemon.py

`scripts/daemon.py` is in charge to pick-up the newly uploaded pictures, to move them into `website/images/incoming` directory, and the daemon evaluates each picture. The result of the evaluation is saved into `website/images/incoming/image_name.json` (for `image_name.jpg`).

## website
