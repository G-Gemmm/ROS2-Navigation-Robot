import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
import os 
from launch.actions import ExecuteProcess
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # 先获取功能包路径再使用os拼接出urdf文件的路径
    urdf_package_path = get_package_share_directory("rm_robot_description")
    urdf_default_path = os.path.join(urdf_package_path, "urdf", "rm_robot.urdf.xacro")

    # 获取gazebo仿真世界路径 rm_robot_world.sdf地图存在问题,选用turtlebot3_world.sdf
    world_package_path = get_package_share_directory("rm_robot_description")
    world_default_path = os.path.join(world_package_path, "world", "turtlebot3_world.sdf")

    # 获取ekf配置文件路径
    ekf_package_path = get_package_share_directory("rm_robot_description")
    ekf_default_path = os.path.join(ekf_package_path, "config", "ekf.yaml")

    # 获取gz_bridge配置文件路径
    gz_bridge_package_path = get_package_share_directory("rm_robot_description")
    gz_bridge_default_path = os.path.join(gz_bridge_package_path, "config", "gz_bridge.yaml")

     # 获取rviz2配置文件路径
    rviz2_package_path = get_package_share_directory("rm_robot_description")
    rviz2_default_path = os.path.join(rviz2_package_path, "rviz2", "rm_robot.rviz")
    
    # 声明urdf文件路径的参数:"model"
    # 便于在启动时指定不同的urdf文件
    # 默认值为rm_robot.urdf.xacro
    action_declare_parameter = launch.actions.DeclareLaunchArgument(
            name="model",
            default_value=str(urdf_default_path),
            description="要使用的urdf文件路径"
    )

    # 创建延迟执行Launch对象,substitution
    # 将xacro文件动态的转换成urdf文件,并将其结果赋值给变量substitutions_command_result
    substitutions_command_result = launch.substitutions.Command([
        "xacro ",launch.substitutions.LaunchConfiguration("model")])
    # 明确参数类型,创建参数值对象robot_description_value，以便传入robot_state_publisher节点
    robot_description_value = launch_ros.parameter_descriptions.ParameterValue(
        substitutions_command_result,value_type=str
    )

    # 声明gazebo仿真使用时间参数:"sim"
    # 在仿真中使用仿真时钟
    # 默认值为true
    action_declare_ues_sim_time_parameter = launch.actions.DeclareLaunchArgument(
        name="sim",
        default_value="true",
        description="是在仿真中使用仿真时钟"
    )    

    # 声明gazebo仿真世界参数:"world"
    # 默认值为turtlebot3_world.sdf
    action_declare_world_parameter = launch.actions.DeclareLaunchArgument(
        name="world",
        default_value=str(world_default_path),
        description="gazebo仿真世界路径"
    )

    # 创建机器人实体节点 spawn_x spawn_y spawn_z
    # 默认值为0.0
    action_declare_spawn_x_parameter = launch.actions.DeclareLaunchArgument(
        name="spawn_x",
        default_value="0.0",
        description="机器人实体在仿真世界中的x坐标"
    )
    action_declare_spawn_y_parameter = launch.actions.DeclareLaunchArgument(
        name="spawn_y",
        default_value="0.0",
        description="机器人实体在仿真世界中的y坐标"
    )
    action_declare_spawn_z_parameter = launch.actions.DeclareLaunchArgument(
        name="spawn_z",
        default_value="0.0",
        description="机器人实体在仿真世界中的z坐标"
    )

    # 创建robot_state_publisher节ction_declare_paramete点
    # 并将其参数ues_sim_time赋值为LaunchConfiguration("sim")
    action_robot_state_publisher = launch_ros.actions.Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"use_sim_time": LaunchConfiguration("sim"),
                     "robot_description": robot_description_value}]
    )

    # 创建gazebo仿真节点
    # Gazebo Harmonic 的命令是 gz sim。在 launch 里调用外部命令，用 ExecuteProcess
    # gz sim 打开的仿真世界路径为world参数的值
    action_launch_gazebo_sim = launch.actions.ExecuteProcess(
        cmd=[
            "gz",
            "sim",
            "-r",
            LaunchConfiguration("world")
        ],
        output="screen"
    )

    # 用 ros_gz_sim 包的 create 节点
    # 功能：读取 topic /robot_description 上的 URDF 文本，在 Gazebo 里生成机器人实体
    # 可选传参数：spawn_x spawn_y spawn_z 机器人实体在仿真世界中的坐标
    # 默认值为0.0 0.0 0.0
    action_create_robot_entity = launch_ros.actions.Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
                    "-name", "rm_robot",
                    "-topic", "/robot_description",
                    "-x", LaunchConfiguration("spawn_x"),
                    "-y", LaunchConfiguration("spawn_y"),
                    "-z", LaunchConfiguration("spawn_z")
                  ]
    )

    # --- 话题桥接 ---
    # 把 Gazebo 内部话题和 ROS2 话题桥接起来
    action_bridge = launch_ros.actions.Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{"use_sim_time": LaunchConfiguration("sim")},
                    {"config_file": gz_bridge_default_path}],
        output="screen"
    )

    # 创建ekf节点
    # 可执行文件名：ekf_node
    # 节点名：ekf_node 对应ekf.yaml文件
    action_launch_ekf = launch_ros.actions.Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        parameters=[
            str(ekf_default_path),
            # 传入sim参数,用于在仿真中使用仿真时钟
            {"use_sim_time": LaunchConfiguration("sim"),}
                    ],
        output="screen"
    )

    # # 创建rviz2节点
    # action_rviz2 = launch_ros.actions.Node(
    #     package="rviz2",
    #     executable="rviz2",
    #     arguments=["-d",str(rviz2_default_path)],
    #     parameters=[{"use_sim_time": LaunchConfiguration("sim"),}]
    # )

    return launch.LaunchDescription([
        action_declare_parameter,
        action_declare_ues_sim_time_parameter,
        action_declare_world_parameter,
        action_declare_spawn_x_parameter,
        action_declare_spawn_y_parameter,
        action_declare_spawn_z_parameter,
        action_robot_state_publisher,
        action_launch_gazebo_sim,
        action_create_robot_entity,
        action_bridge,
        action_launch_ekf,
        # action_rviz2,
    ])