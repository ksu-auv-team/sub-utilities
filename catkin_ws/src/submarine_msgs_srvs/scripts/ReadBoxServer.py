#!/usr/bin/env python

from submarine_msgs_srvs.srv import ReadBox
import rospy

def readBox_server():
    rospy.init_node('readBox_server')
    srv = rospy.Service('readBox', ReadBox, handleReadBox)
    print("Ready to readBox")
    rospy.spin()

def handleReadBox(request):
    print("Returning %s", request.desiredValue)
    if(request.desiredValue == "image_id"):
        return request.box[0]
    elif(request.desiredValue == "class_id"):
        return request.box[1]
    elif(request.desiredValue == "score"):
        return request.box[2]
    elif(request.desiredValue == "box_left"):
        return request.box[3]
    elif(request.desiredValue == "box_top"):
        return request.box[4]
    elif(request.desiredValue == "box_right"):
        return request.box[5]
    elif(request.desiredValue == "box_bottom"):
        return request.box[6]

if __name__ == "__main__":
    readBox_server()
    
