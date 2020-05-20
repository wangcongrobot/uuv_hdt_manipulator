#!/usr/bin/env python

"""
Publishes joint trajectory to move robot to given pose
"""

import rospy
from trajectory_msgs.msg import JointTrajectory
"""
rosmsg show trajectory_msgs/JointTrajectory
std_msgs/Header header
  uint32 seq
  time stamp
  string frame_id
string[] joint_names
trajectory_msgs/JointTrajectoryPoint[] points
  float64[] positions
  float64[] velocities
  float64[] accelerations
  float64[] effort
  duration time_from_start
"""
from trajectory_msgs.msg import JointTrajectoryPoint
"""
rosmsg show trajectory_msgs/JointTrajectoryPoint 
float64[] positions
float64[] velocities
float64[] accelerations
float64[] effort
duration time_from_start
"""
from std_srvs.srv import Empty
import argparse
import time

"""
name: - drive1_joint
- drive2_joint
- drive3_joint
- drive4_joint
- drive5_joint
- drive6_joint
- pincer_joint
- pincer_joint2
"""

def moveJoint(jointcmds, prefix, nbJoints):
    topic_name = '/' + prefix + '/arm_controller/command'
    print("topic_name: ", topic_name)
    pub = rospy.Publisher(topic_name, JointTrajectory, queue_size=1)
    jointCmd = JointTrajectory()
    point = JointTrajectoryPoint()
    jointCmd.header.stamp = rospy.Time.now() + rospy.Duration.from_sec(0.0);
    point.time_from_start = rospy.Duration.from_sec(0.)
    for i in range(0, nbJoints):
        jointCmd.joint_names.append('drive' + str(i+1) + '_joint')
        point.positions.append(jointcmds[i])
        point.velocities.append(0)
        point.accelerations.append(0)
        point.effort.append(0)
    jointCmd.points.append(point)
    rate = rospy.Rate(1)
    count = 0
    while (count < 2):
        pub.publish(jointCmd)
        count += 1
        rate.sleep()

def moveFiners(jointcmds, prefix, nbJoints):
    topic_name = '/' + prefix + '/hand_controller/command'
    pub = rospy.Publisher(topic_name, JointTrajectory, queue_size=1)
    jointCmd = JointTrajectory()
    point = JointTrajectoryPoint()
    jointCmd.header.stamp = rospy.Time.now() + rospy.Duration.from_sec(0.0)
    point.time_from_start = rospy.Duration.from_sec(.0)
    # for i in range(0, nbfingers):
    jointCmd.joint_names.append('pincer_joint')
    jointCmd.joint_names.append('pincer_joint2')
    for i in range(0, nbfingers):
        point.positions.append(jointcmds[i])
        point.velocities.append(0)
        point.accelerations.append(0)
        point.effort.append(0)
    jointCmd.points.append(point)
    rate = rospy.Rate(100)
    count = 0
    while (count < 500):
        pub.publish(jointCmd)
        count += 1
        rate.sleep()

if __name__ == '__main__':
    try:
        rospy.init_node('move_robot_using_trajectory_msg')
        prefix, nbJoints, nbfingers = 'hdt_arm', 6, 2
        # allow gazebo to launch
        # time.sleep(5)

        # Unpause the physics
        rospy.wait_for_service('/gazebo/unpause_physics')
        unpause_gazebo = rospy.ServiceProxy('/gazebo/unpause_physics', Empty)
        resp = unpause_gazebo()

        # home robots
        moveJoint([0., 0.0, 0., 0.0, 0., 0.0], prefix, nbJoints)
        # moveFiners([0.1,0.5], prefix, nbfingers)
    except rospy.ROSInterruptException:
        print("program interrupted before completion")