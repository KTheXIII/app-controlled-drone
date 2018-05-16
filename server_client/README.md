# This contains the python server and the client

The server handles connection between the clients.
The client controls the drone with commands from the server.

The whole project is dependent on dronekit.

## Getting Started

To get started you need to download the repository and extract the zip file.

You need to install other software to run the server and the client. These instructions can be found below.

### Prerequisites

What things you need to install to run the software

#### Server
To run the server you would need to install Python 3.6. This can be found at [python.org](https://www.python.org/).

#### Drone client
The `drone_client.py` can be use with the Pixhawk flight contoller or in a simulated environment dronekit. 
To use the `drone_client.py` with the Pixhawk followed [these](http://ardupilot.org/dev/docs/raspberry-pi-via-mavlink.html) guides on how to wire the Pixhawk with Raspberry Pi.

To use the drone client you would need to follow these [instructions](https://github.com/KTheXIII/app-controlled-drone/tree/master/server_client#install-raspbian).

First install raspbian on Raspberry Pi. Found at [raspberrypi.org](https://www.raspberrypi.org/) in the downloads

#### Install Raspbian
If you're already have raspbian installed you can skip this step.

First you need to format your SD-card, you can use [SD Memory Card Formatter](https://www.sdcard.org/downloads/formatter_4/) or if you're on a Linux  you can follow [these](https://www.pcworld.com/article/3176712/linux/how-to-format-an-sd-card-in-linux.html) steps.  

You can flash raspbian using [Etcher](https://etcher.io/) available on Mac, PC and Linux.
