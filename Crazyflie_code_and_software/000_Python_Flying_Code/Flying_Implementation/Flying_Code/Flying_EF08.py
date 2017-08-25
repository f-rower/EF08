''' This code is used to implement flying, landing and perching operations'''
import pid_param #includes the pid parameters for each flying mode
import time
from threading import Timer
from threading import Thread
from cflib.utils.callbacks import Caller #THis will be useful to create a callback for when a joystick button is pressed.
import gamepad #For reading gamepad inputs.
from Plotter import Plot
#import matplotlib.pyplot as plt  THIS IS TO BE USED FOR PLOTTING ON THE GO.
import cflib.crtp
from cflib.crazyflie import Crazyflie
import logging
import time
from cflib.crazyflie.log import LogConfig

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)
#plt.plot([1,2,3,4])
#plt.ylabel('some numbers')
#plt.show()

class LoggingExample:
    """
    Simple logging example class that logs the Stabilizer from a supplied
    link uri and disconnects after 5s.
    """

    def __init__(self, link_uri):
        """ Initialize and run the example with the specified link_uri """

        # Create a Crazyflie object without specifying any cache dirs
        self._cf = Crazyflie()

        # Connect some callbacks from the Crazyflie API
        self._cf.connected.add_callback(self._connected)
        self._cf.disconnected.add_callback(self._disconnected)
        self._cf.connection_failed.add_callback(self._connection_failed)
        self._cf.connection_lost.add_callback(self._connection_lost)

        print('Connecting to %s' % link_uri)

        # Try to connect to the Crazyflie
        self._cf.open_link(link_uri)

        # Variable used to keep main loop occupied until disconnect
        self.is_connected = True

    def _connected(self, link_uri):
        """ This callback is called form the Crazyflie API when a Crazyflie
        has been connected and the TOCs have been downloaded."""
        print('Connected to %s' % link_uri)

    # CODE FOR LOGGING

        # Add logconfigs for plotting/saving later
        self._lg_stab = LogConfig(name='Stabilizer', period_in_ms=100) #self.lg_stab is a LogConfig object. See log.py for details.
        self._lg_stab.add_variable('stabilizer.roll', 'float')
        self._lg_stab.add_variable('stabilizer.pitch', 'float')
        self._lg_stab.add_variable('stabilizer.yaw', 'float')
        self._lg_stab.add_variable('stabilizer.thrust','float')
        print(time.strftime("%d/%m/%Y"))
        # Adding the configuration cannot be done until a Crazyflie is
        # connected, since we need to check that the variables we
        # would like to log are in the TOC.
        try:
            self._cf.log.add_config(self._lg_stab)
            # This callback will receive the data
            self._lg_stab.data_received_cb.add_callback(self._stab_log_data)#this says what to do when a new set of data is received
            # This callback will be called on errors
            self._lg_stab.error_cb.add_callback(self._stab_log_error)
            # Start the logging
            self._lg_stab.start()
        except KeyError as e:
            print('Could not start log configuration,'
                  '{} not found in TOC'.format(str(e)))
        except AttributeError:
            print('Could not add Stabilizer log config, bad configuration.')

    # CALL FLYING CODE

        t2 = Thread(target = self.fly)
        t2.start()

    # METHODS FOR PLOTTING AND ERRORS

    def _stab_log_error(self, logconf, msg):
        """Callback from the log API when an error occurs"""
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _stab_log_data(self, timestamp, data, logconf):
        # logconf, timestamp and data come from the imported LogConfig class.
        """Callback from the log API when data arrives"""
        #print('[%d][%s]: %s' % (timestamp, logconf.name, data))
        f = open("fileread.txt", 'a+')
        f.write("%s\n" % data)
        f.close()
        # data is a DICTIONARY with entries that can be accessed in the way shown in this line.
        #print(data['stabilizer.roll'])

    def _connection_failed(self, link_uri, msg):
        """Callback when connection initial connection fails (i.e no Crazyflie
        at the speficied address)"""
        print('Connection to %s failed: %s' % (link_uri, msg))
        self.is_connected = False

    def _connection_lost(self, link_uri, msg):
        """Callback when disconnected after a connection has been made (i.e
        Crazyflie moves out of range)"""
        print('Connection to %s lost: %s' % (link_uri, msg))

    def _disconnected(self, link_uri):
        """Callback when the Crazyflie is disconnected (called in all cases)"""
        print('Disconnected from %s' % link_uri)
        self.is_connected = False

    # FLYING, LANDING AND PERCHING CODE

    def fly(self):
        print("I'm flying")
        # time.sleep(1)
        # THis is so that cf doesn't fly away at the beginning
        self._cf.commander.send_setpoint(0, 0, 0, 0)
        while (gamepad.get())[14] == 0:
            #Change maximum thrust here
            thrust = int(32000*(((gamepad.get())[0])))
            #print(thrust)
            #print((gamepad.get())[14])
            self._cf.commander.send_setpoint(0, 0, 0, abs(thrust))
            #self._cf.commander.send_setpoint(0, 0, 0, 0)
        self.land()

    def land(self):
        print("I'm landing")
        while (gamepad.get())[14] == 0:
            c=2




    # MAIN LOOP

if __name__ == '__main__':
    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    # Scan for Crazyflies and use the first one found
    print('Scanning interfaces for Crazyflies...')
    available = cflib.crtp.scan_interfaces()
    print('Crazyflies found:')
    for i in available:
        print(i[0])

    if len(available) > 0:
        le = LoggingExample(available[0][0])
    else:
        print('No Crazyflies found, cannot run example')

    # The Crazyflie lib doesn't contain anything to keep the application alive,
    # so this is where your application should do something. In our case we
    # are just waiting until we are disconnected.
    #while le.is_connected:
       #time.sleep(5)