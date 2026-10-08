# SO-ARM101 + AmazingHand 使用教程

本教程面向复现 **SO-ARM101 从动臂 + AmazingHand 灵巧手** 的遥操作、数据采集与训练全流程，基于 LeRobot（本仓库定制版）。

教程按**阶段**组织，每个阶段独立成目录，内部按操作系统拆分 `win.md`（Windows）与 `linux.md`（Linux）两个文档。请根据你的操作系统选择对应文档阅读。

---

## 硬件与软件概览

| 设备 | 串口（示例，需替换） | 舵机型号 | 说明 |
|---|---|---|---|
| 主动臂（Leader） | `COM54` / `/dev/ttyACM1` | 混合型号 | 遥操作输入，保留 6 号夹爪 |
| 从动臂（Follower） | `COM58` / `/dev/ttyACM0` | `sts3215-C018`（1-5 号） | 执行端，拆除 6 号夹爪 |
| AmazingHand 灵巧手 | `COM11` / `/dev/ttyACM2` | `scs0009`（8 个，ID 1-8） | 从动臂末端，独立串口 |

> **⚠️ 串口名因机器而异**：上表为示例。每台电脑的 COM 号/设备路径都不同，务必用 `lerobot-find-port` 确认本机实际值，并替换所有命令中的占位参数。

> 三个设备必须**各自独立串口、独立供电**。SCS0009（协议 1）与 STS3215（协议 0）不兼容于同一总线。

---

## 教程目录结构

```
tutorials/
├── README.md                          # 本文件（总览）
├── 01-environment/                    # 阶段一：环境搭建
│   ├── win.md                         #   Windows 环境搭建
│   └── linux.md                       #   Linux 环境搭建
├── 02-calibration/                    # 阶段二：标定
│   ├── win.md
│   └── linux.md
├── 03-teleoperation/                  # 阶段三：遥操作
│   ├── win.md
│   └── linux.md
├── 04-data-collection/                # 阶段四：数据采集
│   ├── win.md
│   └── linux.md
├── 05-training/                       # 阶段五：模型训练
│   ├── win.md
│   └── linux.md
└── 06-deployment/                     # 阶段六：部署与评估
    ├── win.md
    └── linux.md
```

---

## 推荐阅读路径

| 步骤 | 阶段 | Windows | Linux |
|---|---|---|---|
| 1 | 环境搭建 | [01-environment/win.md](01-environment/win.md) | [01-environment/linux.md](01-environment/linux.md) |
| 2 | 标定 | [02-calibration/win.md](02-calibration/win.md) | [02-calibration/linux.md](02-calibration/linux.md) |
| 3 | 遥操作 | [03-teleoperation/win.md](03-teleoperation/win.md) | [03-teleoperation/linux.md](03-teleoperation/linux.md) |
| 4 | 数据采集 | [04-data-collection/win.md](04-data-collection/win.md) | [04-data-collection/linux.md](04-data-collection/linux.md) |
| 5 | 模型训练 | [05-training/win.md](05-training/win.md) | [05-training/linux.md](05-training/linux.md) |
| 6 | 部署与评估 | [06-deployment/win.md](06-deployment/win.md) | [06-deployment/linux.md](06-deployment/linux.md) |

---

## 各阶段核心差异速查

| 方面 | Windows | Linux |
|---|---|---|
| Python 环境 | Miniconda + `conda create -n lerobot python=3.12` | Miniforge + 同样命令 |
| 串口名 | `COM54` / `COM58` / `COM11`（示例） | `/dev/ttyACM0/1/2`（示例） |
| 串口权限 | 无需特殊配置 | 需 `sudo chmod 666 /dev/ttyACM*` 或 udev 规则 |
| 命令调用 | conda 激活后 `lerobot-xxx` | conda 激活后 `lerobot-xxx` |
| CUDA 训练 | 需手动装 CUDA torch | 官方支持，解析顺畅 |

---

## 通用注意事项

1. **先跑通阶段一，再进入后续阶段**——环境是后续所有命令的前提。
2. **每台电脑必须重新标定**：尤其是手角度（`lerobot-calibrate-amazing-hand`），config 里的角度是 AmazingHand 官方通用默认，仅作后备；`hand_angles.json` 存在时优先加载本机实测值。
3. **标定文件位置**：`~/.cache/huggingface/lerobot/calibration/`，换机器需迁移或重标定。
4. **首次遥操作务必验证方向**：夹爪张开 ↔ 手张开、捏合 ↔ 手闭合。
5. 每个阶段的 `win.md` / `linux.md` 内均包含**该平台特有的注意事项**，请完整阅读。

---

## 故障排查

各阶段文档内附该平台的故障排查表。以下是**跨阶段常见问题**汇总：

| 现象 | 原因 | 解决 |
|---|---|---|
| `FeetechMotorsBus motor check failed` | 总线无响应，或舵机 ID 与配置不符 | 运行 `python diagnose_feetech_bus.py <串口>` 定位（扫描全部 ID × 全部波特率） |
| `uv run` 报 32/64 位 / numpy 导入错误 | 解释器位数不对 | 用 `uv venv --python <64位解释器绝对路径>` 重建 |
| `uv` 报跨盘 `os error 17` | 缓存跨磁盘 | 设置 `UV_CACHE_DIR` / `TMPDIR` 到同一磁盘 |
| 主动臂标定报 2307 型号错误 | 臂总线被污染 | 确认未同时连接手总线；本项目手走 rustypot 已规避 |
| 手开合方向反 | 角度语义反 | 重标手，或交换 `hand_angles.json` 的 open / close |
| 手张合比例不匹配 | 夹爪映射方向错 | 实测夹爪开/合对应的 `gripper.pos`，调整 `gripper_open_pos` / `gripper_close_pos` |
| 手驱动报 `Operation timed out` | 串口忙碌 / 时序 | 确认手串口未被占用，重试 |
| 标定手无 GUI | 使用了错误命令 | 必须用 `lerobot-calibrate-amazing-hand`（不是 `lerobot-calibrate`） |
| `--display_data=true` 报 rerun 错误 | 可视化依赖缺失 | 去掉该参数，或安装 `lerobot[viz]` + Rerun Viewer |
| 录制一启动就崩溃 | 语音播报（TTS）阻塞控制循环 | 加 `--play_sounds=false` |
| 相机打不开 / 帧超时 | 索引变化，或摄像头 USB 状态卡死 | `lerobot-find-cameras` 确认索引；拔插摄像头重置 |
| 双摄同时打开失败 | 打开顺序问题 | 让索引较大的相机排在 cameras 配置前面 |

---

## 常见问题（FAQ）

**Q：为什么灵巧手不用 lerobot 的 `RangeFinderGUI` 标定？**

A：灵巧手走 `rustypot` 独立串口栈（规避 lerobot 双总线互相污染的缺陷），不使用 `FeetechMotorsBus`。因此采用专用的 `lerobot-calibrate-amazing-hand` GUI 标定开合角度。

**Q：`hand_angles.json` 与 config 里的默认值是什么关系？**

A：config 中的 `hand_open_angles` / `hand_close_angles` 是**后备默认值**（AmazingHand 官方通用值）；`hand_angles.json` 存在时**优先加载**本机实测值。重新标定手之后无需修改任何代码。

**Q：换一台电脑需要重新标定吗？**

A：需要。标定文件位于 `~/.cache/huggingface/lerobot/calibration/`，换机器需迁移该目录，或重新标定。`hand_angles.json` 也在此目录下。

**Q：Windows / Linux / macOS 的差异在哪里？**

A：命令本身相同，差异集中在这几处：

| 方面 | Windows | Linux | macOS |
|---|---|---|---|
| 串口名 | `COMx` | `/dev/ttyACM*` | `/dev/cu.*`（优先用 `cu.` 而非 `tty.`） |
| 虚拟环境路径 | `.venv\Scripts\` | `.venv/bin/` | `.venv/bin/` |
| 串口权限 | 无需配置 | 需 `sudo chmod 666 /dev/ttyACM*` | 无需配置 |

**Q：三个设备必须独立供电吗？**

A：必须。SCS0009（协议 1）与 STS3215（协议 0）不能共用同一条总线；且同进程混用 lerobot 串口栈会互相污染——这也是本项目让手走 rustypot 独立栈的原因。

**Q：训练好的模型在哪里？**

A：部署用 `outputs/train/<任务名>/checkpoints/last/pretrained_model/`（含 `config.json` + 权重），`--policy.path` 必须指向这个目录，不是 checkpoint 根目录。

