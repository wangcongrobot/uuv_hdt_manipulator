#!/usr/bin/env python

import rospy
from gazebo_msgs.msg import LinkStates
from geometry_msgs.msg import Pose

class GazeboLinkPose(object):
    def __init__(self, link_name='object_model::my_box'):
        self.link_name = link_name
        self.link_pose = Pose()
        self.link_name_rectified = link_name.replace("::", "_")

        self.base_link_name = 'hdt_arm::base_link'
        self.base_link_name_rectified = self.base_link_name.replace("::", "_")
        self.base_link_pose = Pose()

        self.object_link_name = 'object_model::my_box'
        self.object_link_pose = Pose()
        self.object_link_name_rectified = self.object_link_name.replace("::", "_")

        self.object_wrt_base_pose = Pose()

        if not self.object_link_name and self.base_link_name:
            raise ValueError("'link_name' is an empty string")
        
        self.states_sub = rospy.Subscriber("/gazebo/link_states", LinkStates, self.callback)

        self.object_pose_pub = rospy.Publisher("/gazebo/" + self.object_link_name_rectified, Pose, queue_size=1)
        self.base_pose_pub = rospy.Publisher("/gazebo/" + self.base_link_name_rectified, Pose, queue_size=1)
        self.object_wrt_base_pub = rospy.Publisher("/gazebo/target", Pose, queue_size=1)

    def callback(self, data):
        try:
            ind = data.name.index(self.base_link_name)
            self.base_link_pose = data.pose[ind]
            idx = data.name.index(self.object_link_name)
            self.object_link_pose = data.pose[idx]
            self.object_wrt_base_pose.position.x = self.object_link_pose.position.x - self.base_link_pose.position.x
            self.object_wrt_base_pose.position.y = self.object_link_pose.position.y - self.base_link_pose.position.y
            self.object_wrt_base_pose.position.z = self.object_link_pose.position.z - self.base_link_pose.position.z
            self.object_wrt_base_pose.orientation = self.object_link_pose.orientation
        except ValueError:
            pass
    
    def run(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            self.object_pose_pub.publish(self.object_link_pose)
            self.base_pose_pub.publish(self.base_link_pose)
            self.object_wrt_base_pub.publish(self.object_wrt_base_pose)
            print("object: ", self.object_wrt_base_pose)
            rate.sleep()


if __name__ == '__main__':
    try:
        rospy.init_node('gazebo_link_pose', anonymous=True)
        gp = GazeboLinkPose()
        
        gp.run()

    except rospy.ROSInterruptException:
        pass