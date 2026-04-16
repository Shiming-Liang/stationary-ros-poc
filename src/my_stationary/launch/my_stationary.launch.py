from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import os


def generate_launch_description():
    description_share = get_package_share_directory("my_stationary")
    urdf_file = os.path.join(description_share, "urdf", "two_arm.urdf.xacro")
    controller_config = os.path.join(
        get_package_share_directory("my_stationary"), "config", "controllers.yaml"
    )

    robot_description = Command([
        f"xacro {urdf_file} ros2_control_hardware_type:=real"
    ])

    return LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output="both",
            parameters=[{"robot_description": ParameterValue(robot_description, value_type=str)}],
        ),
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            output="both",
            parameters=[controller_config],
        ),
    ])
