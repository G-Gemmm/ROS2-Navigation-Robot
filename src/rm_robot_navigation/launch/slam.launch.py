import launch
import launch_ros
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from ament_index_python.packages import get_package_share_directory
import os 
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # 获取slam.yaml配置文件路径
    slam_package_path = get_package_share_directory("rm_robot_navigation")
    slam_default_path = os.path.join(slam_package_path, "config", "slam.yaml")

    # 获取rviz2配置文件路径
    rviz2_package_path = get_package_share_directory("rm_robot_navigation")
    rviz2_default_path = os.path.join(rviz2_package_path, "rviz2", "rm_robot.rviz")

    # 获取slam_toolbox的share目录
    slam_toolbox_share = FindPackageShare('slam_toolbox')
    slam_toolbox_default_path =  PathJoinSubstitution([slam_toolbox_share, 'launch', 'online_async_launch.py'])

    # 申明使用仿真时钟
    action_declare_use_sim_time_parameter = launch.actions.DeclareLaunchArgument(
        name="sim",
        default_value="true",
        description="是在仿真中使用仿真时钟"
    )

    # 启动rviz节点
    action_rviz2 = launch_ros.actions.Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d",str(rviz2_default_path)],
            parameters=[{"use_sim_time": LaunchConfiguration("sim"),}]
        )

    # 启动slam节点
    action_slam = launch.actions.IncludeLaunchDescription(
         PythonLaunchDescriptionSource(slam_toolbox_default_path),
         launch_arguments={
            'params_file': slam_default_path,
            'use_sim_time': LaunchConfiguration('sim')
        }.items()
    )
        
    return launch.LaunchDescription([
        action_declare_use_sim_time_parameter,
        action_rviz2,
        action_slam,
    ])
