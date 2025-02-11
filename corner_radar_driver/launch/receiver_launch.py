# Copyright 2023 Robert Bosch GmbH and its subsidiaries
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params = PathJoinSubstitution([
        FindPackageShare('corner_radar_driver'),
        'config',
        'receiver_params.yaml'
    ])

    # Include the socket_can_bridge launch file
    socketcan_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource([
            FindPackageShare('ros2_socketcan'),
            '/launch/socket_can_bridge.launch.xml'
        ]),
        launch_arguments={
            'interface': 'can0',
            'enable_can_fd': 'true',
            'sender_timeout_sec': '0.1',
            'from_can_bus_topic': 'from_can_bus_fd',
            'to_can_bus_topic': 'to_can_bus_fd'
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument('params',
                            default_value=params,
                            description='Parameters for receiver'),
        
        # Launch the CAN bridge
        socketcan_launch,
        
        # Send initial CAN message
        ExecuteProcess(
            cmd=['cansend', 'can0', '401##10102030405060708'],
            output='screen'
        ),
        
        # Launch the receiver node
        Node(
            package='corner_radar_driver',
            executable='receiver',
            name='corner_radar_driver_receiver',
            output='screen',
            parameters=[LaunchConfiguration('params')],
            arguments=[]
        )
    ])
