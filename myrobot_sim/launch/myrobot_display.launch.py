"""Display the Assem30 URDF in RViz2 (no Gazebo).

Starts robot_state_publisher, a joint state publisher (GUI sliders by default,
so you can spin the wheels) and RViz2 with a pre-made config.

  ros2 launch assem30_sim display.launch.py
  ros2 launch assem30_sim display.launch.py gui:=false
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('myrobot_sim')
    #urdf_pkg = get_package_share_directory('rom2109_description')
    #urdf_path= os.path.join(urdf_pkg, 'urdf/raw', "rom2109_tall.urdf")
    #urdf = open(urdf_path).read()

    xacro_file = os.path.join(pkg_share, 'urdf', 'robot.urdf.xacro')
    default_rviz = os.path.join(pkg_share, 'rviz2', 'display.rviz')

    gui = LaunchConfiguration('gui')
    rviz_config = LaunchConfiguration('rviz_config')
    use_sim_time = LaunchConfiguration('use_sim_time')

    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true',
                              description='Show joint_state_publisher_gui sliders (wheel joints)'),
        DeclareLaunchArgument('rviz_config', default_value=default_rviz,
                              description='RViz2 config file'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description,
                         'use_sim_time': use_sim_time}],
        ),
        Node(
           package='joint_state_publisher_gui',
           executable='joint_state_publisher_gui',
           condition=IfCondition(gui),
           parameters=[{'use_sim_time': use_sim_time}],
        ),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            condition=UnlessCondition(gui),
            parameters=[{'use_sim_time': use_sim_time}],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen',
        ),
    ])