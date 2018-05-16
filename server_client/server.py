#!/user/bin/env/ python3
import socket
import threading
from _thread import *
import os
import time

if not os.path.exists('./data'):
    os.makedirs('./data/msg_template')
    os.makedirs('./data/histories')
    os.makedirs('./data/user')
    os.makedirs('./data/drone')

tLock = threading.Lock()

class Drone_Data:
    """This class stores the drone's telemetry data
    - name: name of the drone
    - avail: tof, if the drone is online or not
    - addr: address of the drone
    """
    def __init__(self, name, avail=False, address=None):
        self.name = name
        self.avail = avail
        self.addr = address
        self.gps = None
        self.homegps = None
        self.destination = None
        self.direc = None
        self.alt = None
        self.bat = None
        self.unix = None
        self.status = None
        self.message = None
        self.commands = None
        self.history_com = []

        self.drone_com_hist = None

    def drone_tel_data(self, gps, direc, alt, unix, bat, homegps, status, msg, lastcom, destination):
        """Apply the gps, direction, altitude, unix, battery to the object
        - gps = lat,lon
        - drec = which way the drone is pointing
        - alt = altitude relative from starting position 
        - unix = unix time from the drone
        - bat = battery level
        """
        self.gps = gps
        self.direc = direc
        self.alt = alt
        self.unix = unix
        self.bat = bat
        self.homegps = homegps
        self.status = status
        self.message = msg
        self.destination = destination

    def print_data(self):
        """For Debugging, prints out the data onto the console"""
        print('AVAIL: ' + str(self.avail))
        print('GPS: ' + str(self.gps))
        print('DIRECTION: ' + str(self.direc))
        print('ALT: ' + str(self.alt))
        print('BAT: ' + str(self.bat))
        print('UNIX: ' + str(self.unix))
        print('\n')

    def store_drone_com_hist(self, com_hist):
        with open('./data/histories/drone_' + str(time.ctime(time.time())) + '.txt', 'r', encoding='utf-8') as f:
            f.write(com_hist)

    def store_hist_com(self):
        """Store command history onto a text file"""
        with open('./data/histories/com_log.txt','a', encoding='utf-8') as f:
            f.write(str(time.ctime(time.time())) + '\n' + self.commands + '\nDRONE ADDRESS:' + str(self.addr) +'\n\n')

    def set_online(self, tof, addr):
        """Set if the drone is online or offline"""
        if(tof):
            self.avail = tof
            self.addr = addr
            return 'GET/SERVER/TEL/0.0'
        elif (not tof):
            self.avail = tof
            self.addr = None
            return 'Drone offline'
    
    def get_tel(self):
        """SERVER respone to get the telemetry data from drone"""
        return 'GET/SERVER/TEL/0.0'
        
    def for_user(self):
        """Return the telemetry data"""
        historyindex = 0
        if(len(self.history_com) == 0):
            tmp = 'UPDATE/SERVER/TELDATA/0.1\nDRONEAVAIL:{}\nDESTINATION:{}\nHOMEGPS:{}\nGPS:{}\nALT:{}\nSTATUS:{}\nMESSAGE:{}\nLASTCOMMAND:{}\nBATTERY:{}'.format(self.avail, self.destination, self.homegps, self.gps, self.alt, self.status, self.message, None, self.bat)
        else:
            historyindex = len(self.history_com) - 1
            tmp = 'UPDATE/SERVER/TELDATA/0.1\nDRONEAVAIL:{}\nDESTINATION:{}\nHOMEGPS:{}\nGPS:{}\nALT:{}\nSTATUS:{}\nMESSAGE:{}\nLASTCOMMAND:{}\nBATTERY:{}'.format(self.avail, self.destination, self.homegps, self.gps, self.alt, self.status, self.message, self.history_com[historyindex], self.bat)
        return tmp
    
    def store_user(self, user_msg):
        """Store user message onto a text file, the whole message that the user have sent will be stored
        - user_msg = The whole content of the message
        """
        with open('./data/user/log.txt', 'a', encoding='utf-8') as f:
            f.write( str(time.ctime(time.time())) + '\n' + user_msg + '\n\n') 

    def store_drone(self, drone_msg):
        """Store the drone message sent to the server
        - drone_msg = The whole message content
        """
        with open('./data/drone/falcon_1.txt', 'a', encoding='utf-8') as f:
            f.write(str(time.ctime(time.time())) + '\n' + drone_msg + '\n\n')

    def check_coms(self, coms):
        """Check for which command to store for later"""
        text_split = coms.split('\n')
        
        if('GOTO' in text_split[0]):
            self.go_to(False, text_split[3].replace('GPS:', ''), text_split[4].replace('ALT:', ''), text_split[5].replace('SPEED:', ''))
        elif('TAKEOFF' in text_split[0]):
            self.takeoff(text_split[3].replace('ALT:', ''), text_split[4].replace('HOVERTIME:', ''))
        elif('RTL' in text_split[0]):
            self.rtl()
        elif('TEL' in text_split[0]):
            self.store_drone_data(coms)

    def takeoff(self, alt, hovertime):
        """Take off command
        - alt = Target altitude in meters
        - hovertime = time in seconds (I don't know if this is needed)
        """
        self.commands = 'UPDATE/SERVER/TAKEOFF/DATA/0.0\nALT:{}\nHOVERTIME:{}'.format(alt, hovertime)        
        # Stores the command histroy onto a file
        self.store_hist_com()
        # Stores the command histroy onto an array
        self.history_com.append(self.commands.replace('\n', '|'))

    def go_to(self, add_way, gps, alt, speed):
        """GO TO DESTINATION
        - add_way = tof, if we're adding any waypoint
        - gps = lat,lon (The destination the drone should fly to)
        - alt = flight altitude in meters
        """
        self.commands = 'UPDATE/SERVER/GOTO/DATA/0.1\nADDWAYPOINT:{}\nGPS:{}\nALT:{}\nSPEED:{}'.format(add_way, gps, alt, speed)
        # Stores the command histroy onto a file
        self.store_hist_com()
        # Stores the command histroy onto an array
        self.history_com.append(self.commands.replace('\n', '|'))
    
    def rtl(self):
        """Tell the vehicle to return to the launch site"""
        self.commands = 'UPDATE/SERVER/RTL/DATA/0.1'
        # Stores the command histroy onto a file
        self.store_hist_com()
        # Stores the command histroy onto an array
        self.history_com.append(self.commands.replace('\n', '|'))

    def apply_command(self):
        """Apply the command, this will send the command to the drone and clear the current command"""
        tmp = self.commands
        self.commands = None
        return tmp

    def store_drone_data(self, data):
        """Parse the data the drone sent and store it"""
        tmp = data.split('\n')
        gps = tmp[1].replace('GPS:', '')
        direc = tmp[2].replace('DIRECTION:', '')
        alt = tmp[3].replace('ALT:', '')
        time = tmp[4].replace('TIME:', '')
        bat = tmp[5].replace('BATTERY:', '')
        homegps = tmp[6].replace('HOMEGPS:', '')
        status = tmp[7].replace('STATUS:', '')
        message = tmp[8].replace('MESSAGE:', '')
        lastcom = tmp[9].replace('LASTCOMMAND:', '')
        destination = tmp[10].replace('DESTINATION:', '')
        # Calls the function inside the class to store the telemetry data from the drone
        self.drone_tel_data(gps, direc, alt, time, bat, homegps, status, message, lastcom, destination)

def start_server(port):
    host = ''
    port = port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 5)

    try:
        s.bind((host, port))
    except socket.error as e:
        print(str(e))

    # basically a que
    s.listen(5)
    return s

def threaded_client(conn, addr):
    """
    Parameters: 
    - conn = connection object
    - addr = connection address Array
    """
    global drone_data # get the global variable
    conn.settimeout(60)
    conn.send('You are now connected, 60 s timeout inactivity'.encode('utf-8'))
    while True:
        try:
            data = conn.recv(4096) # reading the data
            if not data:
                break
        except:
            break
        # parse the data and store the reply
        reply = parse_content(data.decode('utf-8'), addr)
        # this check if it's the drone     
        if(addr != drone_data.addr and reply != None and drone_data != None): 
            conn.sendall(str.encode(reply + "$", encoding='utf_8'))
        elif(reply != None):
            conn.sendall(str.encode(reply, encoding='utf-8'))
    
    conn.close()
    if(addr == drone_data.addr):
        print('drone disconnected')
        print(drone_data.addr)
        drone_data.set_online(False, None)
        drone_data.commands = None
    drone_data.print_data()
    print('connection broke: ', addr[0] + ':' + str(addr[1]))
    print('')

def parse_content(content, addr):
    """A function to parse the content and return the correct response
    - content = string, message from the client
    - addr = array, address that contains the port number and the ip the message is sent from
    """
    tLock.acquire() # acquire the memory usage rights
    global drone_data
    
    final = None # create an empty variable
    tmp = content.split('\n') # splits the message content with \n
    com_type = tmp[0].split('/') # This split the first line with /
    
    if('GET' in com_type):
        if('USER' in com_type):
            drone_data.store_user(content)
            final = drone_data.for_user()
        elif ('DRONE' in com_type):
            drone_data.store_drone(content)
            final = drone_data.set_online(True, addr)
    elif('UPDATE' in com_type):
        # Check which command to store
        drone_data.check_coms(content)

        if('USER' in com_type):
            drone_data.store_user(content)
            final = drone_data.for_user()
        elif('DRONE' in com_type and drone_data.commands == None):
            final = drone_data.get_tel()
        elif ('DRONE' in com_type and drone_data.commands != None):
            final = drone_data.apply_command()
    elif (final == 'ERROR'):
        final = 'ERROR'

    tLock.release() # release the memory usage rights
    return final # return the process message

def main(): # main program
    global drone_data # make a global variable
    drone_data = Drone_Data('TEST0') # make drone data object

    print('>>>starting the server...')
    # SELECT PORT NUMBER
    server = start_server(7000)
    print('>>>server started...')
    print("Waiting for connection...")
    
    while True: # This will loop forever to check for incoming connection
        try:
            conn, addr = server.accept() # accepts the connection
            print('Connected to: ' + addr[0] + ':' + str(addr[1]))

            start_new_thread(threaded_client, (conn, addr)) # hold the connection in a new thread
        except KeyboardInterrupt:
            print('\nThreads terminated')
            server.close()
            break

if __name__ == '__main__':
    main()
