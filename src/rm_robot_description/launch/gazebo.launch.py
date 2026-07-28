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

    # 获取gazebo仿真世界路径
    world_package_path = get_package_share_directory("rm_robot_description")
    world_default_path = os.path.join(world_package_path, "world", "rm_robot_world.sdf")
    
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
    # 默认值为rm_robot_world.sdf
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
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/odom/unfiltered@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model",
            "/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan",
            "/imu/data@sensor_msgs/msg/Imu@gz.msgs.IMU",
        ],
        parameters=[{"use_sim_time": LaunchConfiguration("sim")}],
        output="screen"
    )

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
    ])