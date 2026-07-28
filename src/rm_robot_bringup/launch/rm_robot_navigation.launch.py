import launch
import launch_ros
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():
    # 获取navigation.launch.py文件路径
    navigation_package_path = get_package_share_directory("rm_robot_navigation")
    navigation_default_path = os.path.join(navigation_package_path, "launch", "navigation.launch.py")

    # 获取gazebo仿真世界路径 rm_robot_world.sdf地图存在问题,选用turtlebot3_world.sdf
    world_package_path = get_package_share_directory("rm_robot_description")
    world_default_path = os.path.join(world_package_path, "world", "turtlebot3_world.sdf")

    # 获取core.launch.py文件路径
    core_package_path = get_package_share_directory("rm_robot_description")
    core_default_path = os.path.join(core_package_path, "launch", "core.launch.py")

     # 获取map.yaml配置文件路径,rm_robot_world存在问题,地图改用turtlebot3_world
    map_package_path = get_package_share_directory("rm_robot_navigation")
    map_default_path = os.path.join(map_package_path, "map", "turtlebot3_world.yaml")
    

     # 申明使用仿真时钟
    action_declare_use_sim_time_parameter = launch.actions.DeclareLaunchArgument(
            name="sim",
            default_value="true",
            description="是在仿真中使用仿真时钟"
        )

     # 申明是否打开rviz
    action_declare_use_rviz_parameter = launch.actions.DeclareLaunchArgument(
            name="rviz",
            default_value="true",
            description="是否打开rviz"
        )
    
    # 声明gazebo仿真世界参数:"world"
    action_declare_world_parameter = launch.actions.DeclareLaunchArgument(
        name="world",
        default_value=str(world_default_path),
        description="gazebo仿真世界路径"
    )

    # 声明地图参数:"map"
    action_declare_map_parameter = launch.actions.DeclareLaunchArgument(
        name="map",
        default_value=str(map_default_path),
        description="地图配置路径"
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

    # 创建机器人实体节点 initial_pose_x initial_pose_y initial_pose_yaw
    # 可以在启动时指定机器人实体在仿真世界中的初始位置
    # 默认值为0.0
    action_declare_initial_pose_x_parameter = launch.actions.DeclareLaunchArgument(
            name="initial_pose_x",
            default_value="1.5",
            description="机器人实体在仿真世界中的x坐标"
        )
    action_declare_initial_pose_y_parameter = launch.actions.DeclareLaunchArgument(
            name="initial_pose_y",
            default_value="1.5",
            description="机器人实体在仿真世界中的y坐标"
        )
    action_declare_initial_pose_yaw_parameter = launch.actions.DeclareLaunchArgument(
            name="initial_pose_yaw",
            default_value="0.0",
            description="机器人实体在仿真世界中的yaw角度"
        )
    
    # 启动core.launch.py文件
    action_launch_core = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource([core_default_path]),
        launch_arguments=[
            ("use_sim_time", LaunchConfiguration("sim")),
            ("world", LaunchConfiguration("world")),
            ("spawn_x", LaunchConfiguration("spawn_x")),
            ("spawn_y", LaunchConfiguration("spawn_y")),
            ("spawn_z", LaunchConfiguration("spawn_z"))
        ]
    )

    # 启动navigation.launch.py文件
    action_launch_navigation = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource([navigation_default_path]),
        launch_arguments=[
            ("use_sim_time", LaunchConfiguration("sim")),
            ("rviz", LaunchConfiguration("rviz")),
            ("initial_pose_x", LaunchConfiguration("initial_pose_x")),
            ("initial_pose_y", LaunchConfiguration("initial_pose_y")),
            ("initial_pose_yaw", LaunchConfiguration("initial_pose_yaw")),
            ("map", LaunchConfiguration("map"))
        ]
    )

    return launch.LaunchDescription([
        action_declare_use_sim_time_parameter,
        action_declare_use_rviz_parameter,
        action_declare_world_parameter,
        action_declare_map_parameter,
        action_declare_spawn_x_parameter,
        action_declare_spawn_y_parameter,
        action_declare_spawn_z_parameter,
        action_declare_initial_pose_x_parameter,
        action_declare_initial_pose_y_parameter,
        action_declare_initial_pose_yaw_parameter,
        action_launch_core,
        action_launch_navigation,
    ])
