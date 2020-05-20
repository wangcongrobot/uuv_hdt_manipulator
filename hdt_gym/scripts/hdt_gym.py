
# system lib
import os
import sys
import copy
import threading
import time
from time import sleep
import subprocess
import numpy as np

# ROS lib
import rospy
import roslaunch
import rosparam
import rostopic
import rosmsg, rosservice
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist, Pose, PoseStamped
from sensor_msgs.msg import JointState

import ikfastpy

class HDTAnglerROS(object):
    def __init__(self,
                 robot_name='hdt_angler',
                 debug_print=True,
                 control_freq=10,
                 ):
        # Environment variable
        self.env = os.environ.copy()
        self.debug_print = debug_print

        # run ROS core if not already running
        self.core = None # roscore
        self.gui = None # RQT
        master_uri = 11311
        self.init_core(port=master_uri)
        try:
            rospy.init_node('hdt_gym_ros_interface', anonymous=True)
            rospy.logwarn("ROS node hdt_gym_ros_interface has already been initialized")
        except rospy.exception.ROSException:
            rospy.logwarn('ROS node hdt_gym_ros_interface has not been initialized')

        # control frequency
        self.control_rate = rospy.Rate(control_freq)

        ## HDT Angler arm
        self.arm_joint_names = ["drive1_joint",
                                "drive2_joint",
                                "drive3_joint",
                                "drive4_joint",
                                "drive5_joint",
                                "drive6_joint"]
        self.arm_joint_home = [0,0,0,0,0,0]

        self.arm_dof = len(self.arm_joint_names)

        self.arm_joint_state_lock = threading.RLock()

        self.rostopic_arm_joint_states = '/joint_states'
        rospy.Subscriber(self.rostopic_arm_joint_states, JointState, self.arm_callback_joint_states)

        self.arm_gym_action_pub = rospy.Publisher('/gym_action', Pose, queue_size=1)

        self.hdt_kin = ikfastpy.Pykinematics()


        # Initialization
        self.check_all_systems_ready()

        rospy.sleep(2)
        print("HDT Angler ROS interface initialize successfully")

    def check_all_systems_ready(self):
        joints = None
        while joints is None and not rospy.is_shutdown():
            try:
                joints = rospy.wait_for_message(self.rostopic_arm_joint_states, JointState, timeout=1.0)
                rospy.logwarn("Current " + str(self.rostopic_arm_joint_states) + "READY => " + str(joints))
            except:
                rospy.logerr("Current " + str(self.rostopic_arm_joint_states) + " not ready yet, retrying...")

    @staticmethod
    def is_core_running():
        """
        Return True if the ROS core is running
        """
        try:
            rostopic.get_topic_class('/roscore')
        except rostopic.ROSTopicIOException as e:
            return False
        return True
    
    def init_core(self, uri='localhost', port=11311):
        """
        Initialize the core if it not running.
        From [1], "the ROS core will start up:
        - a ROS master
        - a ROS parameter server
        - a rosout logging node"

        Args:
            uri (str): ROS master URI. The ROS_MASTER_URI will be set to
            `http://<uri>:<port>/`.
            port (int): Port to run the master on.

        Reference:
        - [1] roscore: http://wiki.ros.org/roscore
        """
        # if the core is not already running, run it
        if not self.is_core_running():
            self.env["ROS_MASTER_URI"] = "http://" + uri + ":" + str(port)

            # this is for the rospy methods such as: wait_for_service(), init_node(), ...
            os.environ['ROS_MASTER_URI'] = self.env['ROS_MASTER_URI']

            # run ROS core if not already running
            # if "roscore" not in [p.name() for p in ptutil.process_iter()]:
            # subprocess.Popen("roscore", env=self.env)
            self.core = subprocess.Popen(["roscore", "-p", str(port)], env=self.env, preexec_fn=os.setid) # , shell=True)

    def arm_get