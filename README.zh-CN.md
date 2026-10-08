# SO-ARM101 + AmazingHand 灵巧操作平台

[English](README.md) | **简体中文**

> 基于 [LeRobot](https://github.com/huggingface/lerobot) 框架，将 **AmazingHand 八自由度灵巧手** 集成到 **SO-ARM101 六自由度机械臂**，实现**遥操作 → 数据采集 → 模仿学习训练 → 自主执行**的完整闭环。

---

## 项目简介

本项目在 LeRobot 基础上完成了一套灵巧手机械臂的**硬件集成与软件适配**，主要解决三个工程问题：

| 问题 | 解决方案 |
|---|---|
| **协议冲突** —— 灵巧手舵机（SCS0009，协议 1）与臂体舵机（STS3215，协议 0）无法共用总线 | 三路物理隔离串口 + 独立供电 |
| **驱动栈污染** —— 同进程创建多个 Feetech 总线会互相干扰，导致读取数据损坏 | 灵巧手改用 `rustypot` 独立驱动栈，与臂体总线完全解耦 |
| **标定复杂** —— 8 舵机并联机构的开合标定困难 | 自研一体化标定工具，手指角度与夹爪方向一次标定、自动保存 |

## 核心特性

- **完整遥控闭环**：主动臂 5 关节 → 从动臂跟随；主动臂夹爪 → 灵巧手按比例开合
- **一体化标定**：`lerobot-calibrate-amazing-hand` 图形化标定手部开合角度与夹爪方向，结果自动落盘、启动自动加载，**无需修改任何代码**
- **数据采集与训练**：支持双路相机同步采集，产出 LeRobotDataset v3.0 格式数据集，可直接用于 ACT 等策略训练
- **容器化交付**：提供 CPU / CUDA 两套 Docker 镜像，导入即用，免装环境
- **文档完备**：六阶段教程，Windows / Linux 分平台（仓库内为英文版，中文版见 [wiki](https://wiki.juxitech.com/zh-hant/tutorials/robot-arms/so-arm-amazinghand/)）

## 硬件要求

| 部件 | 型号 / 说明 |
|---|---|
| 从动臂 | SO-ARM101，5 × `STS3215`（ID 1–5），**拆除原厂 6 号夹爪** |
| 灵巧手 | AmazingHand，8 × `SCS0009`（ID 1–8），**独立串口 + 独立供电** |
| 主动臂 | SO-ARM101，6 舵机（**保留 6 号夹爪**作为手部控制输入） |
| 相机 | 2 × USB 摄像头，640×480 @ 30 fps |
| 转接件 | 3D 打印，将灵巧手安装至从动臂腕部 |

> ⚠️ **三个设备必须各自独立串口、独立供电。** SCS0009（协议 1）与 STS3215（协议 0）不能共用总线。

## 快速开始

完整流程见 **[tutorials/](tutorials/)**，按阶段组织，Windows / Linux 分开：

| 阶段 | Windows | Linux |
|---|---|---|
| 1. 环境搭建 | [win](tutorials/01-environment/win.md) | [linux](tutorials/01-environment/linux.md) |
| 2. 标定 | [win](tutorials/02-calibration/win.md) | [linux](tutorials/02-calibration/linux.md) |
| 3. 遥操作 | [win](tutorials/03-teleoperation/win.md) | [linux](tutorials/03-teleoperation/linux.md) |
| 4. 数据采集 | [win](tutorials/04-data-collection/win.md) | [linux](tutorials/04-data-collection/linux.md) |
| 5. 模型训练 | [win](tutorials/05-training/win.md) | [linux](tutorials/05-training/linux.md) |
| 6. 部署评估 | [win](tutorials/06-deployment/win.md) | [linux](tutorials/06-deployment/linux.md) |

> 📖 **文档语言**
>
> | 语言 | 位置 |
> |---|---|
> | **English** | 本仓库 —— [`tutorials/`](tutorials/) |
> | **简体中文** | [wiki.juxitech.com](https://wiki.juxitech.com/zh-hant/tutorials/robot-arms/so-arm-amazinghand/) |

**环境安装（概要）**：

```bash
conda create -y -n lerobot python=3.12
conda activate lerobot
pip install -e ".[amazinghand,training]"
```

**常用命令**：

```bash
# 标定手部角度 + 夹爪方向（GUI）
lerobot-calibrate-amazing-hand --hand_port=<手串口> --leader_port=<主动臂串口>

# 遥操作
lerobot-teleoperate \
  --robot.type=so101_amazing_hand \
  --robot.port=<从动臂串口> --robot.hand_port=<手串口> \
  --robot.id=amazing_hand_follower \
  --teleop.type=so101_leader --teleop.port=<主动臂串口> \
  --teleop.id=amazing_hand_leader

# 部署训练好的策略
lerobot-rollout --strategy.type=base \
  --policy.path=<模型目录> \
  --robot.type=so101_amazing_hand \
  --robot.port=<从动臂串口> --robot.hand_port=<手串口> \
  --task="Pick up the cube with the dexterous hand"
```

## 容器化

```bash
# 构建（在 Linux 上）
bash docker/build_and_export.sh cpu     # CPU 版，约 1 GB
bash docker/build_and_export.sh cuda    # CUDA 版，约 3.5 GB

# 客户侧导入即用
docker load -i dist/lerobot-amazinghand-cpu.tar
```

详见 **[docker/README_DEPLOY.md](docker/README_DEPLOY.md)**（含串口/相机/GUI 直通配置）。

## 本仓库相对原版 LeRobot 的改动

| 位置 | 改动 |
|---|---|
| `src/lerobot/robots/so_amazing_hand/` | **新增** —— SO-ARM101 + 灵巧手组合的机器人定义 |
| `src/lerobot/scripts/lerobot_calibrate_amazing_hand.py` | **新增** —— 灵巧手一体化标定 GUI |
| `src/lerobot/robots/so_follower/so_follower.py` | 总线写操作增加重试，提升偶发丢包容错 |
| `pyproject.toml` | 新增 `amazinghand` extra |
| `tutorials/` | **新增** —— 六阶段教程（英文版） |
| `docker/Dockerfile.amazinghand.*` | **新增** —— CPU / CUDA 镜像 |

其余目录（`policies/`、`datasets/`、`envs/` 等）与原版 LeRobot 一致。

## 目录结构

```
so-arm101-amazinghand/
├── src/lerobot/
│   ├── robots/so_amazing_hand/          # 灵巧手机械臂定义（本项目核心）
│   ├── scripts/lerobot_calibrate_amazing_hand.py  # 标定工具
│   └── ...                              # 其余为 LeRobot 原生代码
├── tutorials/                           # 六阶段教程（英文，Win / Linux）
├── docker/                              # 容器化方案
├── diagnose_feetech_bus.py              # Feetech 总线诊断工具
└── preview_cameras.py                   # 摄像头实时预览工具
```

## 故障排查

**总线找不到舵机**（`FeetechMotorsBus motor check failed`）：

```bash
python diagnose_feetech_bus.py /dev/ttyACM0    # Linux
python diagnose_feetech_bus.py COM58           # Windows
```

该脚本扫描全部 ID × 全部波特率，可区分「总线没通」与「ID 配置不对」。

**相机打不开**：

```bash
lerobot-find-cameras opencv       # 确认索引
python preview_cameras.py         # 实时预览
```

## 致谢与许可

本项目基于以下开源工作：

- **[LeRobot](https://github.com/huggingface/lerobot)** —— 训练与部署框架（Apache-2.0）
- **[AmazingHand](https://github.com/pollen-robotics/AmazingHand)** —— 开源灵巧手，Pollen Robotics 出品（软件 Apache-2.0 / 机械设计 CC BY 4.0）
- **SO-ARM101** —— 开源六自由度机械臂

本仓库代码以 **Apache-2.0** 协议开源，详见 [LICENSE](LICENSE)。硬件设计部分请遵循各上游项目协议。
