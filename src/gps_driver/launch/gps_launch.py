from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'port',
            default_value='/dev/pts/2',
            description='Serial port for the GPS puck'
        ),

        Node(
            package = 'gps_driver',
            executable = 'driver',
            name = 'GPSDriver',
            output = 'screen',
            parameters=[{
                'port' : LaunchConfiguration('port'),
            }]
        ),
    ])