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
        
        while rospy.get_time() < (self.current_state_start_time + 100):

            #rotate the sub
            msg.axes[const.AXES['rotate']] = 0.8
            self.subAngle = (gbl.heading + 60) % 360
                
            #find the angle distance from 0 or 180
            target = 90 if 0 <= self.subAngle <=180 else 270
            diff = abs(target - self.subAngle)
            diff_angle = abs(90 - diff)

            #caculate 'frontback' and 'strafe' directions 
            fb = 1 * (2 * (int(0 <= self.subAngle <= 180)) - 1)
            s = (1 - (float(diff_angle / 90.0))) * (2 * (int( 0 <= self.subAngle <= 90 or 270 <= self.subAngle <= 360)) - 1)
            
            #move the sub
            msg.axes[const.AXES['frontback']] = fb
            msg.axes[const.AXES['strafe']] = s
        
            self.publish(msg)
            rospy.sleep(const.SLEEP_TIME)
            

        return 'through_gate'


    def log(self):
        rospy.loginfo('Executing state SPIN2WIN')