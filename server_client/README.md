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

You can flash raspbian using [Etcher](https://etcher.io/), available on Mac, PC and Linux.

#### Install the required software on Raspberry Pi
If you haven't already follow the instruction on how to set Pixhawk and Raspberry Pi together then follow these instructions.

Step 1 wire the Pixhawk and Raspberry Pi according to this diagram.

![Wiring diagram between Pixhawk and Raspberry Pi](http://ardupilot.org/dev/_images/RaspberryPi_Pixhawk_wiring1.jpg)

Step 2 open the terminal on the Raspberry Pi. Copy and paste this whole command:

```bash
sudo apt-get update && \
sudo apt-get install screen python-wxgtk2.8 python-matplotlib python-opencv python-pip python-numpy python-dev libxml2-dev libxslt-dev && \
sudo pip install future && \
sudo pip install pymavlink && \
sudo pip install mavproxy && \
sudo pip install dronekit
```

#### Run a simulation on a Linux Machine
Before you're testing your own code make sure to test run it on a simulation. To get started download [VirtualBox](https://www.virtualbox.org/) and your favorite Linux distro. Since I use [Ubuntu](https://www.ubuntu.com/) to test I would advise you do the same if you already don't have experience with Linux machines. Please follow this [YouTube Guide](https://youtu.be/sB_5fqiysi4) if you don't know how to install Linux on VirtualBox.

After installation you would need to download [DroneKit](http://python.dronekit.io/guide/quick_start.html). To begin open your Terminal and follow these steps.

On Linux you will first need to install pip and python-dev:
```bash
sudo apt-get install python-pip python-dev
```

pip is then used to install dronekit and dronekit-sitl
```bash
sudo pip install dronekit && \
sudo pip install dronekit-sitl
```

After the installation you can create your own workspace and maybe go ahead and download some [examples](http://python.dronekit.io/examples/running_examples.html) using git. In short, go to the directory you want to save the example using `cd` command in Terminal and clone this [repository](https://github.com/dronekit/dronekit-python).

Example:
```bash
git clone http://github.com/dronekit/dronekit-python.git
```
```
cd dronekit-python/examples/vehicle_state/
```

#### Simulate the drone
Please follow this [guide](http://python.dronekit.io/develop/sitl_setup.html) for further details on how to simulate the drone.
