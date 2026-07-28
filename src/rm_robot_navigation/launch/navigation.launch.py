import launch
import launch_ros
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
import os 

def generate_launch_description():
    # 获取navigation.yaml配置文件路径
    navigation_package_path = get_package_share_directory("rm_robot_navigation")
    navigation_default_path = os.path.join(navigation_package_path, "config", "navigation.yaml")

    # 获取nav2_bringup中bringup.launch.py的路径
    nav2_bringup_share = FindPackageShare('nav2_bringup')
    nav2_bringup_default_path =  PathJoinSubstitution([nav2_bringup_share, 'launch', 'bringup_launch.py'])

    # 获取map.yaml配置文件路径,rm_robot_world存在问题,地图改用turtlebot3_world
    map_package_path = get_package_share_directory("rm_robot_navigation")
    map_default_path = os.path.join(map_package_path, "map", "turtlebot3_world.yaml")

    # 获取rviz2配置文件路径
    rviz2_package_path = get_package_share_directory("rm_robot_navigation")
    rviz2_default_path = os.path.join(rviz2_package_path, "rviz2", "new_rm_robot.rviz")

    # 申明使用仿真时钟
    action_declare_use_sim_time_parameter = launch.actions.DeclareLaunchArgument(
            name="sim",
            default_value="true",
            description="在仿真中使用仿真时钟"
        )

    # 创建机器人实体节点 initial_pose_x initial_pose_y initial_pose_yaw
    # 可以在启动时指定机器人实体在仿真世界中的初始位置
    # 默认值为0.0
    action_declare_initial_pose_x_parameter = launch.actions.DeclareLaunchArgument(
            name="initial_pose_x",
            default_value="0.0",
            description="机器人实体在仿真世界中的x坐标"
        )
    action_declare_initial_pose_y_parameter = launch.actions.DeclareLaunchArgument(
            name="initial_pose_y",
            default_value="0.0",
            description="机器人实体在仿真世界中的y坐标"
        )
    action_declare_initial_pose_yaw_parameter = launch.actions.DeclareLaunchArgument(
            name="initial_pose_yaw",
            default_value="0.0",
            description="机器人实体在仿真世界中的yaw角度"
        )
    
    # 申明是否打开rviz
    action_declare_use_rviz_parameter = launch.actions.DeclareLaunchArgument(
            name="rviz",
            default_value="true",
            description="是否打开rviz"
        )
    
    # 启动nav2_bringup节点,并传入params_file参数，初始化位置参数
    # 并设置autostart为true,用于在仿真中自动启动nav2_bringup节点,否则yaml文件中设置的生命周期参数不会被使用
    action_launch_nav2_bringup = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_bringup_default_path),
        launch_arguments=[
            ("initial_pose_x", LaunchConfiguration("initial_pose_x")),
            ("initial_pose_y", LaunchConfiguration("initial_pose_y")),
            ("initial_pose_yaw", LaunchConfiguration("initial_pose_yaw")),
            ("autostart", "true"),
            ("use_sim_time", LaunchConfiguration("sim")),
            ("map", map_default_path),
            ("params_file", navigation_default_path),]
            )

    # 启动rviz节点
    action_rviz2 = launch_ros.actions.Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d",str(rviz2_default_path)],
            parameters=[{"use_sim_time": LaunchConfiguration("sim"),}],
            output="screen",
            condition=IfCondition(LaunchConfiguration("rviz"))
        )
    
    return launch.LaunchDescription([
        action_declare_use_sim_time_parameter,
        action_declare_initial_pose_x_parameter,
        action_declare_initial_pose_y_parameter,
        action_declare_initial_pose_yaw_parameter,
        action_declare_use_rviz_parameter,
        action_launch_nav2_bringup,
        action_rviz2,
    ])