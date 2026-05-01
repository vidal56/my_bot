import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'my_bot' 

    # --- 1. Configuração de Caminhos ---
    world_path = os.path.join(get_package_share_directory(package_name), 'worlds', 'obstacles.sdf')
    models_path = os.path.join(get_package_share_directory(package_name), 'models')

    set_env = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=models_path
    )

    # --- 2. Robot State Publisher ---
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # --- 3. Gazebo Sim (Jazzy) ---
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
                )]), launch_arguments={'gz_args': ['-r ', world_path]}.items()
    )

    # --- 4. Spawn do Robô ---
    spawn_entity = Node(package='ros_gz_sim', executable='create',
                        arguments=['-topic', 'robot_description',
                                   '-name', 'my_bot'],
                        output='screen')

    # --- 5. Bridge ---
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/tf_static@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        parameters=[{
            'qos_overrides./tf_static.publisher.durability': 'transient_local',
        }],
        output='screen'
    )
    
    return LaunchDescription([
        set_env,
        rsp,
        gazebo,
        spawn_entity,
        bridge,
    ])