#!/usr/bin/env python2

from StateMachine.sub import *
import smach
import math
from StateMachine import sub

# define state interact_gate
class ZSpin(Sub):
    def __init__(self):
        smach.State.__init__(self, outcomes=['through_gate'])
    
    def execute(self, userdata):
        self.init_state()
        gbl.state_heading = gbl.heading

        msg = self.init_joy_msg()

        #python runsub.py --no-arduino --no-network --simulate -s ZSpinMachine

        while rospy.get_time() < (self.current_state_start_time + 100):

            #rotate the sub
            msg.axes[const.AXES['rotate']] = 0.6

            subAngle = gbl.heading

            #direction the sub should go
            #(90 is north, 180 is west, etc)
            target = 90

            targetAngle = (subAngle + (target - 108)) % 360
            
            #convert to radians
            tAngle_radians = (targetAngle) * (math.pi/180.0)

            #calculate frontback and strafe
            fb = math.sin(tAngle_radians)
            s = math.cos(tAngle_radians)
            
            #move the sub, divide by 2 to reduce power
            msg.axes[const.AXES['frontback']] = fb / 2
            msg.axes[const.AXES['strafe']] = s / 2

            # rospy.loginfo('angle: ' + str(self.subAngle) + ' fb: ' + str(fb) + ' s: ' + str(s))
        
            self.publish(msg)
            rospy.sleep(const.SLEEP_TIME)
            

        return 'through_gate'


    def log(self):
        rospy.loginfo('Executing state SPIN2WIN')