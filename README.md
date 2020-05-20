# BlueROV & HDT arm

This repository is in development. 

## Install

```
cd ~/catkin_ws/src
git clone https://github.com/wangcongrobot/uuv_hdt_manpulator.git
git clone https://github.com/wangcongrobot/bluerov2.git
cd ..
catkin_make
source devel/setup.bash
```

```
roslaunch uuv_gazebo_worlds ocean_waves.launch
roslaunch bluerov2_gazebo start_pid_controller_hdt_demo.launch
roslaunch uuv_control_utils send_waypoints_file.launch uuv_name:=bluerov2
```

![bluerov2_hdt_uuvsim](images/bluerov2_arm_uuvsimx2.gif)