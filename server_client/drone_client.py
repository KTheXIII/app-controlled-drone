#!/user/bin/env/ python2
import socket
import time
import os
import sys
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil

import argparse  
parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='127.0.0.1:14550')
args = parser.parse_args()

class Drone:
    """Drone class, this class stores the data the flight controller return and store all the commands it receives from server
    The class also store the socket connection with the server.
    The communication between the flight controller is handle by the class, the 'vehicle' object is being pass into the drone class.
    
    - name = name of the vehicle
    - vehicle = the vehicle object from the dronekit
    
    """

    def __init__(self, name, vehicle):
        self.name = name
        self.gps = None
        self.homegps = None
        self.destination = None
        self.alt = None
        self.battery = None
        self.velocity = None
        self.message = None
        self.status = None
        self.command = None
        self.unix = time.time()
        self.com_hist = []
        self.waypoint = []

        self.s = None
        self.vehicle = vehicle
        self.start_time = time.ctime(time.time())        

        if(not os.path.exists('./drone')):
            os.makedirs('./drone/com_hist')
            os.makedirs('./drone/telemetry_data')

    def set_home(self):
        self.homegps = [self.vehicle.location.global_relative_frame.lat,self.vehicle.location.global_relative_frame.lon] #outputs: lat=-35.3632621765,lon=149.165237427,alt=583.989990234
    def store_com_hist(self, coms):
        """Store command history onto a text file"""
        with open('./drone/com_hist/' + str(self.start_time).replace(':', '-') + '-com_log.txt', 'a') as f:
            f.write(str(time.ctime(time.time())).replace(':', '-') + '\n' + coms +
                    '\nDRONE ADDRESS:'+ str(socket.gethostname()) + '\n\n')
        self.command = None

    def store_teldata(self):
        """Store the telemetry data"""
        with open('./drone/telemetry_data/' + str(self.start_time).replace(':', '-') + '-tel.txt', 'a') as f:
            f.write(str(time.ctime(time.time()).replace(':', '-')))

    def arm_and_takeoff(self, aTargetAltitude):
        """
        Arms vehicle and fly to aTargetAltitude.
        """
        print 'taking off...'
        self.message = 'taking off to ' + str(aTargetAltitude) + ' m'
        self.status = 'TAKEOFF' 
        self.send(self.prepare_data())
        self.send_read()
        print("Basic pre-arm checks")
        # Don't try to arm until autopilot is ready
        self.message = 'Basic pre-arm checks'
        self.vehicle.airspeed = 3
        self.send_read()
        while not self.vehicle.is_armable:
            print 'Waiting for vehicle to initialise...'
            self.message = 'Waiting for vehicle to initialise...'
            self.send_read()

        print("Arming motors")
        # Copter should arm in GUIDED mode
        self.message = 'Arming motors, copter should arm in GUIDED mode'
        self.send_read()
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        self.message = 'Vehicle armed'
        self.send_read()

        # Confirm vehicle armed before attempting to take off
        while not self.vehicle.armed:
            print " Waiting for arming..."
            self.message = 'Waiting for arming...'
            self.send_read()

        print "Taking off!"
        self.vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude
        self.message = 'Taking off!'
        self.send_read()

        start_time = time.time()
        last_alt = self.vehicle.location.global_relative_frame.alt

        # Wait until the vehicle reaches a safe height before processing the goto
        #  (otherwise the command after Vehicle.simple_takeoff will execute
        #   immediately).
        while True:
            print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
            self.message = 'Flying up to ' + str(aTargetAltitude) + ' m'
            self.alt = self.vehicle.location.global_relative_frame.alt
            self.gps = self.vehicle.location.global_relative_frame
            # Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
                print("Reached target altitude")
                self.message = "Reached target altitude"
                self.send_read()
                break
            if self.vehicle.location.global_relative_frame.alt - last_alt < 1 and time.time() - start_time >= 10:
                self.rtl()
                self.status = 'LANDING'
                self.send_read()
                break
            self.status = 'FLYING'
            self.send_read()

    def go_to(self, gps, alt, air_speed):
        print 'going to ' + str(gps)
        self.message = 'flying to ' + str(gps)
        self.destination = gps
        self.send(self.prepare_data())
        self.send_read()
        print("Set default/target airspeed to " + str(air_speed))
        self.vehicle.airspeed = air_speed #air_speed

        print("Going towards the point")
        point1 = LocationGlobalRelative(float(self.destination[0]), float(self.destination[1]), alt)
        self.vehicle.simple_goto(point1)

    def rtl(self):
        print 'returning to launch site'
        self.status = 'RTL'
        self.message = 'Returning to the launch site'
        self.send(self.prepare_data())
        self.vehicle.mode = VehicleMode("RTL")
        self.send_read()

    def land(self):
        print 'landing...'
        self.status = 'LAND'
        self.message = 'Landing at the current location'
        self.send(self.prepare_data())
        self.vehicle.mode = VehicleMode("LAND")
        self.send_read()

    def make_logfiles(self):
        if not os.path.exists('./data'):
            pass

    def apply_command(self):
        self.command = None

    def start_connection(self, host, port):
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
            except socket.error as msg:
                s = None
                continue
            try:
                s.connect(sa)
            except socket.error as msg:
                s.close()
                s = None
                continue
            break
        if s is None:
            print 'could not open socket...'
            sys.exit(1)
        print 'connection started...'
        self.s = s

    def send(self, content):
        self.s.sendall(content)
    
    def receive(self, content):
        return self.s.recv(4096)

    def send_read(self):
        data = self.s.recv(4096)
        # print(data)
        reply = self.parse_content(data)
        self.s.sendall(reply)

    def parse_content(self, content):
        tmp = content.split('\n')
        final = None
        tmp_mode = self.vehicle.mode.name
        if(tmp_mode == 'RTL' or tmp_mode == 'LAND'):
            self.status = tmp_mode

        if('GET' in tmp[0]):
            # A FUNCTION TO GET THE DATA FROM THE FLIGHT CONTROLLER
            self.store_tel_data()
            final = self.prepare_data()
        elif ('UPDATE' in tmp[0]):
            self.check_coms(content)
            self.command = tmp[0]
            self.com_hist.append(content)
            self.store_com_hist(content)
            final = self.prepare_data()
        if (final == None):
            final = 'ERROR'
        return final

    def check_coms(self, coms):
        text_split = coms.split('\n')
        if('RTL' in text_split[0]):
            self.rtl()
        elif('LAND' in text_split[0]):
            self.land()
        elif('TAKEOFF' in text_split[0]):
            self.arm_and_takeoff(float(text_split[1].replace('ALT:', '')))
        elif ('LOCATION' in text_split[0]):
            self.go_to(text_split[3].replace('GPS:', '').split(','), 10, 3)
        elif('GOTO' in text_split[0]):
            if(self.status != 'FLYING'):
                self.arm_and_takeoff(float(text_split[3].replace('ALT:', '')))                
                self.go_to(text_split[2].replace('GPS:', '').split(','), float(
                    text_split[3].replace('ALT:', '')), int(text_split[4].replace('SPEED:', '')))                
            else:
                self.go_to(text_split[2].replace('GPS:', '').split(','), float(
                    text_split[3].replace('ALT:', '')), int(text_split[4].replace('SPEED:', '')))

    def store_tel_data(self):
        self.gps = [self.vehicle.location.global_relative_frame.lat, self.vehicle.location.global_relative_frame.lon]
        self.alt = self.vehicle.location.global_relative_frame.alt
        self.battery = '{}V,{}%'.format(self.vehicle.battery.voltage, self.vehicle.battery.level)
        self.unix = time.time()

    def prepare_data(self):
        self.status = self.vehicle.mode.name
        gps = self.gps
        direc = 'no idea fam'
        alt = self.alt  # self.vehicle.location.global_relative_frame.alt
        unix = time.time()
        battery = self.battery
        homegps = self.homegps
        status = self.status
        message = self.message
        destination = self.destination
        lastcom = None
        
        if(len(self.com_hist) > 1):
            lastcom = self.com_hist[len(self.com_hist)-1]
        
        tmp = 'UPDATE/DRONE/TEL/0.1\nGPS:{}\nDIRECTION:{}\nALT:{}\nTIME:{}\nBATTERY:{}\nHOMEGPS:{}\nSTATUS:{}\nMESSAGE:{}\nLASTCOMMAND:{}\nDESTINATION:{}'.format(
            str(gps).replace('[', '').replace(']', '').replace(' ', ''), direc, alt, unix, battery, homegps, status, message, lastcom, destination)
        return tmp


def main():
    # Connect to the Vehicle
    print 'Connecting to vehicle on: %s' % args.connect
    vehicle = connect(args.connect, baud=57600, wait_ready=True)
    drone = Drone('FALCON 1', vehicle)
    print '>>>starting connection with the server'
    drone.start_connection(host='ip-address', port=7000)

    print '>>>start receiving data'
    data = drone.s.recv(4096)
    print data
    print 'data received...'
    print '>>>sending update'
    drone.s.sendall(
        'GET/DRONE/START/0.0\nTIME:{}\nBATTERY:VOLTAGE'.format(time.time()))
    print 'message sent...'
    print '>>>entering the main loop...'
    drone.set_home()
    start_time = time.time()
    while True:
        drone.send_read()        

    drone.s.close()
    print 'closing the server'

if __name__ == '__main__':
    main()
