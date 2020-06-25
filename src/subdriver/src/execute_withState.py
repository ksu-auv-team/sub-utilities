#!/usr/bin/env python2

# ROS
import rospy

# All available state machines
import StateMachine.machines.BaseStateMachine as base
import StateMachine.machines.PrequalifyMachine as prequal
import StateMachine.machines.TestSpinMachine as testspin
import StateMachine.machines.QualifyStraightMachine as dumbqualify
import StateMachine.machines.TestTrackMachine as testtrack
import StateMachine.machines.TestArbitraryMachine as arb
import StateMachine.machines.ZSpinMachine as zspin

# Global values updated in real time
import StateMachine.gbl as gbl

# extra imports
import argparse
from pydoc import locate

parser = argparse.ArgumentParser(description="execute a state machine for the submarine")
parser.add_argument('-m', '--machine', default="BaseStateMachine", help="the name of the state machine to execute (default: %(default)s)")
parser.add_argument('-d', '--debug', action="store_true", help='Launches in debug mode. Will try to go through entire state machine.')
parser.add_argument('-l', '--list', action="store_true", help="List the available state machines.")
parser.add_argument('-a', '--arbitrary', default=None, help="Provide module path to the state that you want to test including the Class Name. EX: --arbitrary StateMachine.taskless.dumb_start.Dumb_Start")
args = parser.parse_args(rospy.myargv()[1:])

states = {
    'BaseStateMachine': base.createStateMachine,
    'PrequalifyMachine': prequal.createStateMachine,
    'TestSpinMachine': testspin.createStateMachine,
    'QualifyStraightMachine': dumbqualify.createStateMachine,
    'TestTrackMachine': testtrack.createStateMachine,
    'ZSpinMachine': zspin.createStateMachine
}

def main():
    # List all the states available to the user
    if args.list:
        print("Available State Machines:")
        for machine in states:
            print(machine)
        return
    
    # If the user wants to use an arbitrary state
    if args.arbitrary:
        my_class = locate(args.arbitrary)

        try:
            arb.createStateMachine(my_class())
        except:
            print("I could not find: " + args.arbitrary)
            print("There was something wrong with the arbitrary path you gave, I could not find it, please double check it and try again.")
            return

        return

    # Running the main state machine
    print("Running {}".format(args.machine))

    try:
        states[args.machine]()
    except KeyError:
        rospy.logfatal("Error: state machine name not recognized")

if __name__ == '__main__':
    gbl.debug = args.debug
    main()

