import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
import os 

def generate_launch_description():
    # 先获取功能包路径再使用os拼接出urdf文件的路径
    urdf_package_path = get_package_share_directory("rm_robot_description")
    urdf_default_path = os.path.join(urdf_package_path, "urdf", "rm_robot.urdf.xacro")

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

    # 创建robot_state_publisher节点,并将其参数robot_description赋值为robot_description_value
    action_robot_state_publisher = launch_ros.actions.Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description_value}]
    )

    # 创建robot_joint_state_publisher节点
    action_robot_joint_state_publisher = launch_ros.actions.Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",   
    )   

    # 创建rviz2节点
    action_rviz2 = launch_ros.actions.Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d",str(rviz2_default_path)]
    )

    return launch.LaunchDescription([
        action_declare_parameter,
        action_robot_state_publisher,
        action_robot_joint_state_publisher,
        action_rviz2,
    ])