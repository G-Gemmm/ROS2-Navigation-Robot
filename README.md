# ROS2 Navigation Robot

基于 ROS2 Jazzy 的自主导航机器人项目复现。

本项目参考开源项目 **linorobot2** 的整体架构，从零开始构建了一个完整的 2WD 差速仿真机器人导航系统。整个过程不搬运原项目代码，所有文件在理解后手写完成，目的是深入掌握 ROS2 Navigation Stack 的每一层。

项目目标是搭建一个从机器人模型、仿真环境、传感器融合、SLAM 建图到 Nav2 自主导航的完整 Pipeline。

整个系统基于 Gazebo Harmonic 仿真环境运行，并集成：

- Robot Description（URDF/Xacro 宏定义组织）
- Gazebo Harmonic Simulation
- ros_gz_bridge（ROS2-Gazebo 话题桥接）
- robot_localization EKF（轮式里程计 + IMU 融合）
- SLAM Toolbox（在线异步建图）
- Nav2 Navigation Stack（全局规划 + 局部控制 + 代价地图 + 行为树）
- RViz2 Visualization

---

# Project Overview

## Autonomous Navigation Pipeline

完整自主导航流程如下：

```
Sensors
   |
   v
LiDAR / IMU / Wheel Odometry  <-- Gazebo Harmonic
   |
   v
ros_gz_bridge  (topic bridge: /scan /imu/data /odom/unfiltered)
   |
   v
robot_localization EKF  (odom0 + imu0 fusion)
   |
   +--> /odometry/filtered
   +--> odom -> base_footprint TF
   |
   v
SLAM Toolbox (online_async)  -->  map -> odom TF
   |
   v
Nav2 Navigation Stack
   |
   +--> Planner Server (SmacPlanner2D)
   +--> Controller Server (RegulatedPurePursuitController)
   +--> Global / Local Costmap
   +--> Behavior Tree Navigator
   +--> Collision Monitor
   |
   v
Velocity Command (/cmd_vel)
   |
   v
ros_gz_bridge
   |
   v
Gazebo DiffDrive Plugin
   |
   v
Mobile Robot
```

机器人能够完成：

- Gazebo Harmonic 中机器人 URDF 模型加载与可视化
- 传感器数据模拟（LiDAR / IMU / 轮式里程计）
- SLAM Toolbox 在线异步建图
- 地图保存与加载
- AMCL 全局定位
- Nav2 全局路径规划与局部避障
- 一键自主导航

---

# Features

## 1. Complete Robot Simulation

项目包含完整机器人仿真模型，采用 Xacro 宏定义组织，便于维护和扩展：

```
rm_robot_description/urdf/
|
+-- rm_robot.urdf.xacro          (入口文件)
+-- common_inertia.urdf.xacro    (通用惯性矩阵)
+-- base/
|   +-- base.urdf.xacro          (底盘主体)
+-- actuator/
|   +-- wheel.urdf.xacro         (差速轮)
|   +-- caster.urdf.xacro        (万向轮)
+-- sensor/
|   +-- laser.urdf.xacro         (2D 激光雷达)
|   +-- imu.urdf.xacro           (IMU)
|   +-- depth.urdf.xacro         (深度相机, 可选)
+-- plugin/
    +-- gz_sim_control_plugin.urdf.xacro   (DiffDrive + JointState)
    +-- gz_sim_sensor_plugin.urdf.xacro    (GPU Ray + IMU)
```

Gazebo Plugin 配置包含：

| Plugin | 功能 |
|--------|------|
| gz::sim::systems::DiffDrive | 差速驱动控制 |
| gz::sim::systems::JointState | 关节状态发布 |
| gz::sim::systems::GPU_ray | GPU 加速激光雷达仿真 |
| gz::sim::systems::Imu | IMU 物理传感器 |

## 2. ROS-Gazebo Bridge

使用 `ros_gz_bridge` 完成 ROS2 与 Gazebo Harmonic 的双向话题桥接：

| 话题方向 | ROS2 | Gazebo |
|----------|------|--------|
| GZ -> ROS | /clock | /world/empty/clock |
| GZ -> ROS | /odom/unfiltered | /odom/unfiltered |
| GZ -> ROS | /imu/data | /imu/data |
| GZ -> ROS | /scan | /scan |
| GZ -> ROS | /joint_states | /joint_states |
| ROS -> GZ | /cmd_vel | /cmd_vel |

## 3. Multi-Sensor Fusion (EKF)

项目使用 `robot_localization` 完成多传感器融合：

**输入：**

| 传感器 | 话题 | 融合维度 |
|--------|------|----------|
| Wheel Odometry | /odom/unfiltered | x, yaw, vx, vyaw |
| IMU | /imu/data | vyaw |

**输出：**

```
map (通过 SLAM Toolbox / AMCL)
 |
 v
odom (EKF 发布的稳定里程计)
 |
 v
base_footprint (EKF 发布的 TF)
 |
 v
base_link (robot_state_publisher)
 |
 +---> wheel_left_link
 +---> wheel_right_link
 +---> caster_link
 +---> laser_cylinder_link -> laser_link
 +---> imu_link
```

**EKF 配置要点：**

- `two_d_mode: true` — 2D 差速底盘，忽略 Z 轴运动
- `frequency: 50` — 50Hz 融合频率
- `odom0_config: [ yaw, vx, vyaw]` — 仅融合角度姿态和线/角速度
- `imu0_config: [ax, ay,vyaw]` — 融合线加速度和角速度

## 4. SLAM Mapping

使用 SLAM Toolbox (`online_async` 模式) 完成二维环境地图构建。

SLAM 启动文件包含：

- SLAM Toolbox 生命周期节点
- Lifecycle Manager (localization)
- RViz2 可视化
- 地图保存服务

启动 SLAM：

```bash
ros2 launch rm_robot_bringup rm_robot_slam.launch.py
```

控制机器人移动建图：

```bash
# 键盘控制在另一个终端自动启动
# i=前进, ,=后退, j=左转, l=右转, k=停止
```

保存地图：

```bash
ros2 run nav2_map_server map_saver_cli \
  -f ~/rm_robot_ws/src/rm_robot_navigation/map/<map_name>
```

生成结果：

```
map.yaml
map.pgm
```

## 5. Autonomous Navigation

项目基于 ROS2 Navigation2 (Nav2) 实现自主导航。

**Planner Server**

负责全局路径规划，使用 SmacPlanner2D (VON_NEUMANN 扩展方式)：

| 参数 | 值 |
|------|-----|
| tolerance | 0.5 m |
| max_iterations | 200000 |
| max_on_approach_iterations | 500 |
| cost_travel_multiplier | 2.0 |

**Controller Server**

负责局部轨迹跟踪与避障，使用 RegulatedPurePursuitController：

| 参数 | 值 |
|------|-----|
| max_linear_vel | 0.5 m/s |
| max_angular_vel | 1.0 rad/s |
| use_cost_regulated_linear_velocity_scaling | True |
| use_rotate_to_heading | True |

**Costmap**

Global Costmap：全地图静态层 + 障碍物层
Local Costmap：5x5 滚动窗口，以 odom 为参考坐标系

**Inflation 配置**

| 参数 | 值 | 作用 |
|------|-----|------|
| inflation_radius | 0.55 m | 扩展 11 个代价梯度格点 |
| cost_scaling_factor | 5.0 | 控制代价衰减速度 |

**Behavior Tree Navigator**

负责导航任务管理与 Recovery 行为（路径规划失败时路径重试、控制超时后旋转恢复）。

---

# Navigation Process

完整导航流程：

启动导航（一键包含 Gazebo + 核心节点 + Nav2）：

```bash
ros2 launch rm_robot_bringup rm_robot_navigation.launch.py
```

在 RViz2 中操作：

1. 点击 **2D Pose Estimate**，在地图上设定机器人初始位置
2. 点击 **2D Goal Pose**，在地图上选择目标点
3. 机器人自动规划路径并开始自主导航

关闭 RViz2（仅终端运行）：

```bash
ros2 launch rm_robot_bringup rm_robot_navigation.launch.py rviz:=false
```

---

# Environment

## Software

| Software | Version |
|----------|---------|
| Ubuntu | 24.04 |
| ROS2 | Jazzy Jalisco |
| Gazebo | Harmonic |
| Python | 3.12 |
| RViz2 | ROS2 Jazzy |
| Simulation | VMware (12GB RAM) |

## Main ROS2 Packages

| Package | Function |
|---------|----------|
| rm_robot_description | Robot Model, URDF/Xacro, Gazebo, EKF, Bridge |
| rm_robot_navigation | SLAM Toolbox, Nav2 Config, Maps, RViz |
| rm_robot_bringup | Orchestrated Entry Points (SLAM / Navigation) |
| robot_localization | EKF Multi-Sensor Fusion |
| slam_toolbox | Online Asynchronous SLAM |
| nav2_bringup | Nav2 Lifecycle Nodes |

---

# Workspace Structure

```
rm_robot_ws/
|
+-- rm_robot_description/
|   +-- config/
|   |   +-- ekf.yaml                 # EKF 融合参数
|   |   +-- gz_bridge.yaml           # 话题桥接配置
|   +-- launch/
|   |   +-- core.launch.py           # Gazebo + Bridge + EKF + RSP
|   |   +-- display.launch.py        # 仅显示模型
|   |   +-- gazebo.launch.py         # 纯 Gazebo
|   +-- urdf/                        # Xacro 宏定义
|   |   +-- rm_robot.urdf.xacro
|   |   +-- common_inertia.urdf.xacro
|   |   +-- base/, actuator/, sensor/, plugin/
|   +-- world/
|   |   +-- rm_robot_world.sdf       # 自定义世界
|   |   +-- turtlebot3_world.sdf     # 推荐世界
|   +-- rviz/
|   |   +-- rm_robot.rviz            # RViz 配置
|   +-- CMakeLists.txt
|   +-- package.xml
|
+-- rm_robot_navigation/
|   +-- config/
|   |   +-- navigation.yaml          # Nav2 全部参数
|   |   +-- slam.yaml                # SLAM 参数
|   +-- launch/
|   |   +-- slam.launch.py           # SLAM 启动
|   |   +-- navigation.launch.py     # 导航启动
|   +-- map/                         # 建图结果
|   |   +-- turtlebot3_world.yaml/pgm
|   |   +-- rm_robot_map.yaml/pgm
|   +-- rviz/
|   |   +-- rm_robot.rviz            # 建图用 RViz
|   |   +-- new_rm_robot.rviz        # 导航用 RViz
|   +-- CMakeLists.txt
|   +-- package.xml
|
+-- rm_robot_bringup/
|   +-- launch/
|   |   +-- rm_robot_slam.launch.py  # 一键建图
|   |   +-- rm_robot_navigation.launch.py  # 一键导航
|   +-- CMakeLists.txt
|   +-- package.xml
|
+-- README.md
```

---

# Installation

创建并进入工作空间：

```bash
mkdir -p ~/rm_robot_ws/src
cd ~/rm_robot_ws/src
```

克隆仓库：

```bash
git clone https://github.com/G-Gemmm/ROS2-Navigation-Robot.git
```

安装依赖：

```bash
sudo apt update
sudo apt install ros-jazzy-robot-localization
sudo apt install ros-jazzy-slam-toolbox
sudo apt install ros-jazzy-nav2-bringup ros-jazzy-nav2-smac-planner
sudo apt install ros-jazzy-nav2-regulated-pure-pursuit-controller
sudo apt install ros-jazzy-nav2-collision-monitor
sudo apt install ros-jazzy-ros-gz-bridge ros-jazzy-ros-gz-sim
sudo apt install ros-jazzy-teleop-twist-keyboard
sudo apt install ros-jazzy-xacro
```

编译：

```bash
cd ~/rm_robot_ws
colcon build --symlink-install
source install/setup.bash
```

---

# Simulation Workflow

## Step 1: SLAM Mapping

启动 SLAM 建图模式（Gazebo + Core + SLAM Toolbox + Keyboard Teleop）：

```bash
ros2 launch rm_robot_bringup rm_robot_slam.launch.py
```

在键盘控制终端中操作机器人遍历环境，RViz2 中实时观察地图构建过程。

## Step 2: Save Map

建图完成后保存地图：

```bash
ros2 run nav2_map_server map_saver_cli \
  -f ~/rm_robot_ws/src/rm_robot_navigation/map/my_map
```

## Step 3: Autonomous Navigation

启动导航模式（Gazebo + Core + Nav2）：

```bash
ros2 launch rm_robot_bringup rm_robot_navigation.launch.py \
  map:=~/rm_robot_ws/src/rm_robot_navigation/map/my_map.yaml
```

在 RViz2 中使用 2D Pose Estimate 设定初始位姿，使用 Nav2 Goal 发送目标点。

---

# Learning Notes

本项目从零复刻 linorobot2 架构，按功能包拆分为四个学习阶段：

## Layer 1: Robot Description

学习内容：

- URDF/Xacro 宏定义组织方式
- Gazebo Plugin 配置（DiffDrive, JointState, GPU Ray, IMU）
- ros_gz_bridge 话题桥接
- robot_localization EKF 参数配置
- TF 树设计与发布

## Layer 2: SLAM

学习内容：

- SLAM Toolbox 启动与参数配置
- online_async 模式的生命周期管理
- 地图保存与加载

## Layer 3: Navigation

学习内容：

- Nav2 完整参数配置（Planner / Controller / Costmap / BT）
- Navigation Lifecycle Manager
- AMCL 定位与粒子滤波
- 全局/局部代价地图配置
- 膨胀参数对规划质量的影响
- 导航过程中的常见问题排查

## Layer 4: Bringup

学习内容：

- 多功能包统筹编排
- Launch Argument 条件判断与参数传递

---

# Common Issues

## Gazebo 死寂白板

**原因**：VMware 3D 加速兼容性或 SDF 世界插件缺失。

**解决**：

- 设置环境变量 `export LIBGL_ALWAYS_SOFTWARE=1`
- 确认 SDF 中包含 `gz::sim::systems::Imu` 插件
- 确认 `/clock` 话题已从 `/world/empty/clock` 桥接

## IMU 数据不发布

**原因**：Gazebo Harmonic 中 Sensors 插件不包含 IMU。

**解决**：在世界 SDF 中增加 `<plugin name="gz::sim::systems::Imu" filename="gz-sim-imu-system"/>`

## 导航时机器人不避障或进入膨胀区

**原因**：膨胀半径过小导致代价梯度不足，规划器无法区分安全区和禁区。

**解决**：增大 inflation_radius（推荐 0.55-0.6m），使用 SmacPlanner2D 替代 Navfn。

## Controller Server 启动失败

**原因**：navigation.yaml 中参数类型错误。

**解决**：检查参数类型（height/width 应为 integer，非 double）。

---

# Future Improvements

可能的功能扩展方向：

- 实体机器人部署（Teensy + micro-ROS）
- 真实 LiDAR 硬件集成（RPLIDAR / YDLIDAR）
- ros2_control hardware interface
- 自主探索算法集成
- 视觉导航（深度相机 + 视觉 SLAM）
- 多机器人协同导航
- Docker 部署

---

# Reference

This project is inspired by and references:

- [linorobot2](https://github.com/linorobot/linorobot2) — Complete ROS2 navigation stack
- [ROS2 Navigation2](https://docs.nav2.org/) — Nav2 official documentation
- [SLAM Toolbox](https://github.com/SteveMacenski/slam_toolbox) — SLAM implementation
- [robot_localization](https://github.com/cra-ros-pkg/robot_localization) — EKF sensor fusion
- [Gazebo Sim Documentation](https://gazebosim.org/docs/harmonic) — Gazebo Harmonic

---

# License

This project is for learning and research purposes.
Apache License 2.0
