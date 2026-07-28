import launch
import launch_ros
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():
    # 获取slam.launch.py文件路径
    slam_package_path = get_package_share_directory("rm_robot_navigation")
    slam_default_path = os.path.join(slam_package_path, "launch", "slam.launch.py")

    # 获取gazebo仿真世界路径 rm_robot_world.sdf地图存在问题,选用turtlebot3_world.sdf
    world_package_path = get_package_share_directory("rm_robot_description")
    world_default_path = os.path.join(world_package_path, "world", "turtlebot3_world.sdf")

    # 获取core.launch.py文件路径
    core_package_path = get_package_share_directory("rm_robot_description")
    core_default_path = os.path.join(core_package_path, "launch", "core.launch.py")

     # 申明使用仿真时钟
    action_declare_use_sim_time_parameter = launch.actions.DeclareLaunchArgument(
            name="sim",
            default_value="true",
            description="是在仿真中使用仿真时钟"
        )

    # 声明gazebo仿真世界参数:"world"
    action_declare_world_parameter = launch.actions.DeclareLaunchArgument(
        name="world",
        default_value=str(world_default_path),
        description="gazebo仿真世界路径"
    )

    # 创建机器人实体节点 spawn_x spawn_y spawn_z
    # 默认值为0.0
    action_declare_spawn_x_parameter = launch.actions.DeclareLaunchArgument(
        name="spawn_x",
        default_value="1.5",
        description="机器人实体在仿真世界中的x坐标"
    )
    action_declare_spawn_y_parameter = launch.actions.DeclareLaunchArgument(
        name="spawn_y",
        default_value="1.5",
        description="机器人实体在仿真世界中的y坐标"
    )
    action_declare_spawn_z_parameter = launch.actions.DeclareLaunchArgument(
        name="spawn_z",
        default_value="0.0",
        description="机器人实体在仿真世界中的z坐标"
    )

    # 启动core.launch.py文件
    action_launch_core = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource([core_default_path]),
        launch_arguments=[
            ("sim", LaunchConfiguration("sim")),
            ("world", LaunchConfiguration("world")),
            ("spawn_x", LaunchConfiguration("spawn_x")),
            ("spawn_y", LaunchConfiguration("spawn_y")),
            ("spawn_z", LaunchConfiguration("spawn_z"))
        ]
    )

    # 启动slam.launch.py文件
    action_launch_slam = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource([slam_default_path]),
        launch_arguments=[
            ("sim", LaunchConfiguration("sim")),
        ]
    )

    # 启动teleop_twist_keyboard节点
    action_launch_teleop_twist_keyboard = launch_ros.actions.Node(
        package="teleop_twist_keyboard",
        executable="teleop_twist_keyboard",
        parameters=[{"use_sim_time": LaunchConfiguration("sim")}]
    )

    return launch.LaunchDescription([
        action_declare_use_sim_time_parameter,
        action_declare_world_parameter,
        action_declare_spawn_x_parameter,
        action_declare_spawn_y_parameter,
        action_declare_spawn_z_parameter,
        action_launch_core,
        action_launch_slam,
        action_launch_teleop_twist_keyboard
    ])
