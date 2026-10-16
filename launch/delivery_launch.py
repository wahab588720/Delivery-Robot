from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='delivery_robot',
            executable='delivery_server',
            name='delivery_server',
            output='screen'
        )
    ])
