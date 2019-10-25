#!/usr/bin/env python3

import os
import subprocess
import time
import datetime
import argparse
import signal
import sys
import rospy
from std_msgs.msg import Bool
from colorama import Fore

class SubSession():
    def __init__(self,no_save_images = ' ', network_model = ' ', state_machine = ' ' ):
        # Subprocesses:
        self.curr_children = []
        self.startup_processes = []
        
        # Arduino variables
        self.delay_start = 0
        self.sub_is_killed = True
        self.no_save_images = no_save_images
        self.network_model = network_model
        self.state_machine = state_machine


        #keep logs from each start in a separate directory
        self.script_directory = os.path.dirname(os.path.realpath(__file__)) + '/'
        self.curr_log_dir = self.script_directory + '../logs/{}/'.format(datetime.datetime.now())
        os.mkdir(self.curr_log_dir)
        
        # ROS subscribers
        self.startup_processes.append(self.start_roscore())
        killswitch_start_sub = rospy.Subscriber("killswitch_run_start", Bool, self.killswitch_start_callback)
        killswitch_realtime_sub = rospy.Subscriber("killswitch_is_killed", Bool, self.killswitch_realtime_callback, queue_size=1)
        
    # shut down child processes for restarting them cleanly or exiting
    def kill_children(self):
        self.curr_children
        print("Removing all runtime processes...")
        for i in range(len(self.curr_children)):
            try:
                proc = self.curr_children.pop()
                print("Killing: ")
                print(proc)
                if not proc.poll():
                    proc.kill()
            except Exception as e:
                print(e)
        print("Done!")

    def kill_startup(self):
        print("Removing Startup Process...")
        for i in range(len(self.startup_processes)):
            try:
                proc = self.startup_processes.pop()
                print("Killing: ")
                print(proc)
                if not proc.poll():
                    proc.kill()
            except Exception as e:
                print(e)
            print("Removed Startup Process!")
        bashCommand = "pkill -f ros"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) 

    def start_roscore(self):
        roscore_string = 'roscore'
        roscore_command = roscore_string.split()

        print(Fore.GREEN + 'starting roscore with command: ' + Fore.WHITE + roscore_string)
        with open('{}roscoreout.txt'.format(self.curr_log_dir), 'w') as rcout:
            rc = subprocess.Popen(roscore_command, stdout=rcout, stderr=rcout)
            return rc

    def start_video(self):
        video_string = "python " + self.script_directory + "camera_node.py " + self.no_save_images
        video_command = video_string.split()

        print(Fore.GREEN + "starting video node with command: " + Fore.WHITE + video_string)
        with open('{}videoout.txt'.format(self.curr_log_dir), 'w') as videoout:
            video = subprocess.Popen(video_command, stdout=videoout, stderr=videoout)
            return video

#kept changed args.network_model to self.network_model and args.no_save_images to self.no_save_images and type casted the booleans to a string
    def start_network(self):
        network_string = "python3 " + self.script_directory + '../submodules/jetson_nano_inference/jetson_live_object_detection.py --model ' + self.network_model + ' ' + self.no_save_images
        network_command = network_string.split()
    
        print(Fore.GREEN + 'starting Neural Network with command: ' + Fore.WHITE + network_string)
        with open('{}networkout.txt'.format(self.curr_log_dir), 'w') as networkout:
            network = subprocess.Popen(network_command, stdout=networkout, stderr=networkout)
            return network

    def start_movement(self):
        movement_string = "roslaunch movement_package manualmode.launch"
        movement_command = movement_string.split()

        print(Fore.GREEN + 'starting movement_package with command: ' + Fore.WHITE + movement_string)
        with open('{}movementout.txt'.format(self.curr_log_dir), 'w') as mvout:
            mv = subprocess.Popen(movement_command, stdout=mvout, stderr=mvout)
            return mv 

    def start_execute(self):
        execute_string = 'python ' + self.script_directory + '../submodules/subdriver/execute_withState.py --machine ' + args.state_machine + ' ' + args.debug_execute
        execute_command = execute_string.split()

        print(Fore.GREEN + 'starting execute with command: ' + Fore.WHITE + execute_string)
        with open('{}executeout.txt'.format(self.curr_log_dir), 'w') as executeout:
            ex = subprocess.Popen(execute_command, stdout=executeout, stderr=executeout)
            return ex
                
    def start_arduino(self):
        arduino_string = "rosrun rosserial_python serial_node.py /dev/arduino_0"
        arduino_command = arduino_string.split()

        print(Fore.GREEN + 'starting Arduino Process with command: ' + Fore.WHITE + arduino_string)
        with open('{}arduinoout.txt'.format(self.curr_log_dir), 'w') as ardout:
            arduino = subprocess.Popen(arduino_command, stdout=ardout, stderr=ardout)
            return arduino

    #start ALL the things
    def start(self):     
        # Run the Video Node
        self.curr_children.append(self.start_video())
        
        self.delay_start = time.time() # The time we will compare our arduino time to
        while(time.time() - self.delay_start < 2 and not self.sub_is_killed):
            pass

        # Run Movement Package
        self.curr_children.append(self.start_movement())

        self.delay_start = time.time() # The time we will compare our arduino time to
        while(time.time() - self.delay_start < 10 and not self.sub_is_killed):
            pass

        # Run Execute
        if(args.manual):
            print('Manual Mode enabled, start your joystick node')
        else:
            self.curr_children.append(self.start_execute())
             
        print('exiting start')

    def signal_handler(self, sig, frame):
        print("\nCaptured Ctrl+C, stopping execution...")
        self.kill_children()
        self.kill_startup()
        sys.exit(0)

    def killswitch_start_callback(self, msg):
        if(msg.data):
            print('Starting Sub Runtime Processes')
            self.start()
        else:
            print('Sub has been killed')
            self.kill_children()
            

    def killswitch_realtime_callback(self, msg):
            self.sub_is_killed = msg.data
        

if __name__ == '__main__':
    # Parse command line arguments:
    parser = argparse.ArgumentParser(description="run the submarine")
    parser.add_argument('-i', '--internet-address', help="override default hostname or ip address for remote computer (not currently functional)")
    parser.add_argument('-m', '--manual', action='store_true', help="Will not run state machine")
    parser.add_argument('-s', '--state-machine', default="QualifyStraightMachine", help="set name of state machine to use (default: %(default)s)")
    parser.add_argument('-n', '--network-model', default="qual_2_rcnn_frozen", help="set name of neural network to use (default: %(default)s)")
    parser.add_argument('-v', '--verbosity', help="set logging verbosity (doesn't work)")
    parser.add_argument('--no-arduino', action='store_true', help='Runs the sub without running any physical arduino hardware.')
    parser.add_argument('--no-network', action='store_true', help='Runs the sub without running the neural network')
    parser.add_argument('--no-save-images', action='store_const', default ='', const='--no-save-images', help='Will not record any video/pictures from the sub')
    parser.add_argument('--debug-execute', action='store_const', default='', const='--debug', help='Will run execute with the debug flag')
    parser.add_argument('--start-front-network', action='store_true', help='Will begin with the front neural network running')
    parser.add_argument('--start-bottom-network', action='store_true', help='Will begin with the bottom neural network running')
    args = parser.parse_args()

    # Wait for arduino to start
    time.sleep(3)

    # Create Subsession
    go_sub_go = SubSession(args.no_arduino)

    # Ros init
    rospy.init_node("run_sub")
    
    if not args.no_network:
        if args.start_front_network:
            front_pub = rospy.Publisher('enable_front_network', Bool, queue_size=1)
            front_pub.publish(True)
        if args.start_bottom_network:
            bottom_pub = rospy.Publisher('enable_bottom_network', Bool, queue_size=1)
            bottom_pub.publish(True)

    # captureing Ctrl+C
    signal.signal(signal.SIGINT, go_sub_go.signal_handler)
    
    # If we are running without an arduino hooked up, just run the start, don't listen()
    if args.no_arduino:
        if(not args.no_network):
            go_sub_go.startup_processes.append(go_sub_go.start_network())
        time.sleep(3)
        go_sub_go.start()

    # If we do have an arduino hooked up, we need to forward the ROS stuff over
    else:
        go_sub_go.startup_processes.append(go_sub_go.start_arduino())
        if(not args.no_network):
            go_sub_go.startup_processes.append(go_sub_go.start_network())

    #the loop everything runs from
    rospy.spin()
