# SO-ARM101 + AmazingHand Docker 镜像使用说明

镜像里已经装好了完整环境（Python 3.12 / PyTorch / LeRobot 定制版 / rustypot / Feetech SDK / pygame / 中文字体 / ffmpeg），
**客户不需要再装任何环境**，导入镜像即可运行。

> ⚠️ **仅适用于 Linux 客户机**。Docker 在 Windows/macOS 上跑在虚拟机里，**无法直通 COM 串口和 USB 摄像头**，
> 硬件控制类项目不要用容器。Windows 客户请使用离线 conda 环境包方案。

---

## 一、两个版本怎么选

| 镜像 | 体积 | 用途 |
|---|---|---|
| `lerobot-amazinghand:cpu` | 约 1 GB | 遥操作、标定、录数据、回放。**策略推理约 4 Hz，动作会明显变慢** |
| `lerobot-amazinghand:cuda` | 约 3.5 GB | 上述全部 + **策略推理跑满 30 Hz**（需宿主机有 NVIDIA 显卡） |

**只做数据采集**用 CPU 版就够；**要部署策略做自主执行**建议 CUDA 版。

---

## 二、构建镜像（在你自己的机器上，只需一次）

在一台 Linux 机器（虚拟机 / 云服务器均可）上：

```bash
cd /path/to/so-arm101-amazinghand
bash docker/build_and_export.sh cpu        # 或 cuda / both
```

产物：
```
dist/lerobot-amazinghand-cpu.tar      （约 1 GB）
dist/lerobot-amazinghand-cuda.tar     （约 3.5 GB）
```

**国内网络加速**：脚本里已默认配置了国内源（基础镜像镜像站 + 清华 pip 源 + 阿里云 torch 源）。
如果某个源不通，可临时覆盖：

```bash
BASE_IMAGE_MIRROR=docker.m.daocloud.io/library/python:3.12-slim \
TORCH_INDEX_CUDA=https://mirrors.aliyun.com/pytorch-wheels/cu128 \
bash docker/build_and_export.sh both
```

---

## 三、分发给客户

把 `.tar` 文件拷给客户（U 盘 / 网盘均可），客户侧：

```bash
docker load -i lerobot-amazinghand-cpu.tar
docker images | grep lerobot-amazinghand
```

**全程不需要联网**——镜像里所有依赖都已打包。

---

## 四、运行

### 4.1 先确认设备名

```bash
ls /dev/ttyACM*     # 串口：从动臂 / 主动臂 / 灵巧手
ls /dev/video*      # 相机
```

### 4.2 启动容器（CPU 版）

```bash
docker run -it --rm \
  --device=/dev/ttyACM0 \
  --device=/dev/ttyACM1 \
  --device=/dev/ttyACM2 \
  --device=/dev/video0 \
  --device=/dev/video1 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -v ~/lerobot_data:/data \
  lerobot-amazinghand:cpu
```

| 参数 | 作用 |
|---|---|
| `--device=/dev/ttyACM*` | 直通三个串口（按实际设备名改） |
| `--device=/dev/video*` | 直通相机 |
| `-v /tmp/.X11-unix ... -e DISPLAY` | 让容器内 pygame 标定窗口显示在宿主机屏幕上 |
| `-v ~/.cache/huggingface:...` | **持久化标定文件**（`hand_angles.json` 等），否则容器删了就丢 |
| `-v ~/lerobot_data:/data` | 持久化数据集（容器内路径 `/data`） |

**显示 GUI 前宿主机需执行一次**：

```bash
xhost +local:docker
```

### 4.3 CUDA 版

在 4.2 的命令基础上加 `--gpus all`：

```bash
docker run -it --rm --gpus all \
  --device=/dev/ttyACM0 ... \
  lerobot-amazinghand:cuda
```

宿主机需装好 **NVIDIA 驱动 + nvidia-container-toolkit**，验证：

```bash
docker run --rm --gpus all lerobot-amazinghand:cuda \
  python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

### 4.4 设备名固定的方法（可选）

串口名（`ttyACM0/1/2`）插拔后会变，建议在宿主机用 udev 规则固定，或每次进容器前 `ls /dev/ttyACM*` 确认后按顺序传入。

---

## 五、容器里的常用命令

```bash
# 标定手 + 夹爪方向（GUI）
lerobot-calibrate-amazing-hand --hand_port=/dev/ttyACM2 --leader_port=/dev/ttyACM1

# 遥操作
lerobot-teleoperate \
  --robot.type=so101_amazing_hand \
  --robot.port=/dev/ttyACM0 --robot.hand_port=/dev/ttyACM2 \
  --robot.id=amazing_hand_follower \
  --teleop.type=so101_leader --teleop.port=/dev/ttyACM1 \
  --teleop.id=amazing_hand_leader

# 录数据（存到挂载出来的 /data）
lerobot-record \
  --robot.type=so101_amazing_hand \
  --robot.port=/dev/ttyACM0 --robot.hand_port=/dev/ttyACM2 \
  --robot.id=amazing_hand_follower \
  --robot.cameras='{top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30},wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}}' \
  --teleop.type=so101_leader --teleop.port=/dev/ttyACM1 \
  --teleop.id=amazing_hand_leader \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=/data/soarm_amazing_hand_pick \
  --dataset.push_to_hub=false \
  --dataset.num_episodes=20 \
  --dataset.single_task="Pick up the cube with the dexterous hand" \
  --play_sounds=false

# 部署策略
lerobot-rollout --strategy.type=base \
  --policy.path=<模型目录或 HF 仓库名> \
  --device=cuda \
  --robot.type=so101_amazing_hand \
  --robot.port=/dev/ttyACM0 --robot.hand_port=/dev/ttyACM2 \
  --robot.id=amazing_hand_follower \
  --robot.cameras='{top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30},wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}}' \
  --task="Pick up the cube with the dexterous hand" \
  --duration=60 --play_sounds=false
```

---

## 六、常见问题

| 现象 | 原因 / 解决 |
|---|---|
| `Permission denied` 打开串口 | 把设备全部 `--device` 传进来；或临时加 `--privileged` 排查 |
| 相机打不开 | `ls /dev/video*` 确认设备存在；索引可能因插拔变化，用 `lerobot-find-cameras` 重新确认 |
| 标定窗口显示方框 | 镜像已装 `fonts-noto-cjk`；若仍异常，检查宿主机 `xhost` 与 `DISPLAY` |
| GUI 弹不出来 | 宿主机执行 `xhost +local:docker`；确认 `DISPLAY` 环境变量正确传递 |
| `torch.cuda.is_available()` 为 False | 用了 CPU 版镜像，或宿主机没装 NVIDIA 驱动 / nvidia-container-toolkit |
| 重启后串口名变了 | 串口名依赖插入顺序，每次启动前 `ls /dev/ttyACM*` 重新确认 |
| 标定文件丢失 | 没挂载 `~/.cache/huggingface`，容器删除后标定随之消失 |
| 录制一启动就报错 | 加 `--play_sounds=false`（TTS 会阻塞控制循环） |

---

## 七、镜像里装了什么

| 类别 | 内容 |
|---|---|
| 基础 | Python 3.12 (slim) |
| 深度学习 | PyTorch（CPU 版或 cu128 版）+ torchvision |
| 机器人 | LeRobot 定制版（含 `so_amazing_hand` 机器人定义） |
| 硬件 | `rustypot`（灵巧手）、`feetech-servo-sdk`（机械臂）、`pyserial` |
| 视觉 | opencv-python-headless、PyAV、torchcodec |
| GUI | pygame + SDL2 + **中文字体（Noto CJK）** |
| 数据 | datasets、pandas、pyarrow、ffmpeg |
| 训练 | accelerate、wandb |
| 教程 | `/opt/lerobot/tutorials/`（Windows / Linux 两套） |
