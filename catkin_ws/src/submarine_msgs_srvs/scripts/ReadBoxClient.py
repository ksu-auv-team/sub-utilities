#!/usr/bin/env python

import sys
import rospy
from submarine_msgs_srvs.srv import ReadBox

def readBoxClient(box, desiredValue):
    rospy.wait_for_service('readBox')
    try:
        readBox = rospy.ServiceProxy('readBox', ReadBox)
        response = ReadBox(box, desiredValue)
        return response.value
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e
def usage():
        return "%s [box desiredVaue]"%sys.argv[0]

if __name__ == "__main__":
        if len(sys.argv) == 3:
                box = sys.argv[1]
                desiredValue = str(sys.argv[2])
        else:
                print usage()
                sys.exit(1)
        print "Requesting box[%s]"%(desiredValue)
        print "box[%s] =  %s"%(desiredValue, readBoxClient(box, desiredValue))