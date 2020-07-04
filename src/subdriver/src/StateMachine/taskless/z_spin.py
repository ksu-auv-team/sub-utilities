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
            msg.axes[const.AXES['rotate']] = 0.6

            #(+270) changes the gbl.heading to match the unit circle where 
            #(90 is north, 180 is west, etc)
            subAngle = (gbl.heading + 270) %  360

            #direction the sub should go
            #(90 is north, 180 is west, etc)
            target = 90

            #change the angle based on the target
            subAngle = (subAngle + (target - 110)) % 360
            
            #convert to radians
            subAngle_radians = (subAngle) * (math.pi/180.0)

            #calculate the force needed to keep the sub straight while rotating
            fb = math.sin(subAngle_radians)
            s = math.cos(subAngle_radians)

            if subAngle_radians >= math.pi:
                fb = abs(fb)
                s = 0
            
            #move the sub, divide by 2 to reduce power
            msg.axes[const.AXES['frontback']] = fb / 2
            msg.axes[const.AXES['strafe']] = s / 2
        
            self.publish(msg)
            rospy.sleep(const.SLEEP_TIME)
            

        return 'through_gate'


    def log(self):
        rospy.loginfo('Executing state SPIN2WIN')