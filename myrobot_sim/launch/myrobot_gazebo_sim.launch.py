"""Gazebo Classic 11 + ros2_control simulation of the Assem30 robot (ROS 2 Humble).

Starts: gazebo (arena world) -> robot_state_publisher -> spawn_entity ->
        joint_state_broadcaster -> diff_drive_controller.
The 2D lidar is published by the libgazebo_ros_ray_sensor.so plugin on /scan.

Drive with:  ros2 run teleop_twist_keyboard teleop_twist_keyboard
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription, RegisterEventHandler)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('myrobot_sim')
    gazebo_ros = get_package_share_directory('gazebo_ros')

    xacro_file = os.path.join(pkg_share, 'urdf', 'slam_robot_gazebo.urdf.xacro')
    default_world = os.path.join(pkg_share, 'worlds', 'maze1.world')
    default_rviz = os.path.join(pkg_share, 'rviz2', 'slam.rviz')

    world = LaunchConfiguration('world')
    gui = LaunchConfiguration('gui')
    rviz = LaunchConfiguration('rviz')
    rviz_config = LaunchConfiguration('rviz_config')
    x = LaunchConfiguration('x')
    y = LaunchConfiguration('y')
    yaw = LaunchConfiguration('yaw')

    args = [
        DeclareLaunchArgument('world', default_value=default_world, description='SDF world file'),
        DeclareLaunchArgument('gui', default_value='true', description='Start gzclient'),
        DeclareLaunchArgument('rviz', default_value='true', description='Start Rviz2'),
        DeclareLaunchArgument('rviz_config', default_value=default_rviz),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
    ]

    model_path = AppendEnvironmentVariable('GAZEBO_MODEL_PATH', os.path.dirname(pkg_share))

    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros, 'launch', 'gazebo.launch.py')),
        launch_arguments={'world': world, 'gui': gui, 'verbose': 'true'}.items(),
    )

    spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        #arguments=['-file', '/home/waihlan/ROS2/workspace/src/myrobot_sim/urdf/slam_robot_gazebo.urdf.xacro', '-entity', 'myrobot_sim',
        #arguments=['-database', 'myrobot', '-entity', 'myrobot_sim',
        arguments=['-topic', 'robot_description', '-entity', 'myrobot_sim',
                   '-x', x, '-y', y, '-z', '0.06', '-Y', yaw],
        output='screen'
    )

    jsb_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_broad', '--controller-manager', '/controller_manager'],
        output='screen',
    )
    
    diff_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_cont', '--controller-manager', '/controller_manager'],
        output='screen',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(rviz),
        output='screen',
    )

    after_spawn = RegisterEventHandler(OnProcessExit(target_action=spawn, on_exit=[jsb_spawner]))
    after_jsb = RegisterEventHandler(OnProcessExit(target_action=jsb_spawner, on_exit=[diff_spawner]))

    return LaunchDescription(args + [model_path, rsp, gazebo, spawn, after_spawn, after_jsb, rviz_node])
