# 阶段六：部署与评估（Windows）

本阶段加载训练好的策略，让机器人**自主执行**任务，并录制评估视频验证效果。这是整个流程的收尾，也是检验训练成果的关键。

---

## 前置条件

- 已完成 [阶段五：模型训练](../05-training/win.md)
- 训练产出 `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/`
- 相机索引已记录

---

## 步骤 1：确认模型文件

```powershell
# 确认模型目录存在
dir outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model
```

应包含 `model.safetensors` 等模型文件。

> **⚠️ 注意（模型路径）**：`--policy.path` 必须指向 `pretrained_model` 目录（含配置 + 权重），不是 checkpoint 根目录。

---

## 步骤 2：自主评估（不录制）

```powershell
lerobot-rollout `
  --strategy.type=base `
  --policy.path=outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model `
  --device=cuda `
  --robot.type=so101_amazing_hand `
  --robot.port=<从动臂COM> `
  --robot.hand_port=<手COM> `
  --robot.id=amazing_hand_follower `
  --robot.cameras='{
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30},
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}
  }' `
  --task="Pick up the cube with the dexterous hand" `
  --duration=60 `
  --play_sounds=false
```

> 将 `<从动臂COM>` / `<手COM>` 替换为实际 COM 号；相机 `index_or_path` 用 `lerobot-find-cameras` 确认。

> **⚠️ 注意（必须用 `lerobot-rollout`）**：部署评估用 `lerobot-rollout`，**不是** `lerobot-record`——后者强制要求 `--teleop.type`，无法用于策略自主执行。

### 参数说明

| 参数 | 说明 |
|---|---|
| `--strategy.type=base` | 自主执行、**不录制**（纯评估）。可选：`episodic`（录制评估数据）、`sentry`（连续录制+自动上传）、`highlight`（环形缓冲按键保存）、`dagger`（人在回路） |
| `--policy.path` | 训练好的模型目录，**必须指向 `pretrained_model`**（含 `config.json` + 权重），不是 checkpoint 根目录 |
| `--device` | `cuda` 或 `cpu`。**有 NVIDIA 显卡务必用 `cuda`**；CPU 推理慢 5~10 倍，机器人动作会明显变慢 |
| `--robot.type` | `so101_amazing_hand`（从动臂 + 灵巧手组合） |
| `--robot.port` | 从动臂串口 |
| `--robot.hand_port` | 手串口 |
| `--robot.id` | 机器人标识，须与标定时一致 |
| `--robot.cameras` | 相机配置，**相机名称、索引顺序必须与训练时一致** |
| `--task` | 任务描述，**必须与训练时的 `--dataset.single_task` 完全一致** |
| `--duration` | 运行秒数。`60` = 跑 60 秒自动停；`0` = 无限（`Ctrl+C` 手动停） |
| `--play_sounds` | 语音播报。**Windows 上建议 `false`**——TTS 走 PowerShell 合成，会阻塞数秒拖慢控制循环 |
| `--display_data=true` | 打开 Rerun 可视化窗口（可选，会额外占用 CPU） |

> **💡 其他可调参数**：
> - `--fps=30`：控制频率（默认 30）。推理跟不上时警告里会提示实际帧率
> - `--policy.n_action_steps`：每次推理后连续执行的动作步数（默认 100）。**慢机器上不要调小**——调小会让"重新推理"更频繁，动作变得一卡一卡；保持默认反而流畅（一段轨迹一次走完）
> - `--interpolation_multiplier`：动作插值倍数，调大可让动作更平滑
> - `--return_to_initial_position=false`：结束时保持当前姿势，不自动回到起始位

---

## 步骤 3：（可选）录制评估数据

只验证成功率的话，步骤 2 就够了（**不产生任何文件**）。若要保存评估数据用于分析或补录，换成 `episodic` 策略并指定数据集：

```powershell
lerobot-rollout `
  --strategy.type=episodic `
  --policy.path=outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model `
  --device=cuda `
  --robot.type=so101_amazing_hand `
  --robot.port=<从动臂COM> `
  --robot.hand_port=<手COM> `
  --robot.id=amazing_hand_follower `
  --robot.cameras='{
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30},
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}
  }' `
  --task="Pick up the cube with the dexterous hand" `
  --duration=0 `
  --play_sounds=false `
  --dataset.repo_id=soarm_amazing_hand_pick_eval `
  --dataset.root=D:\lerobot_data\soarm_amazing_hand_pick_eval `
  --dataset.single_task="Pick up the cube with the dexterous hand"
```

> **⚠️ 注意（base 不产生文件）**：`--strategy.type=base` 是纯评估，**不写任何文件**。只有 `episodic` / `sentry` / `highlight` / `dagger` 且带 `--dataset.repo_id` 才会录制，数据落在 `--dataset.root` 指定目录。

> **💡 `episodic` 特点**：行为最接近 [阶段四录制](../04-data-collection/win.md)——每轮 `episode_time_s` 秒后进入 `reset_time_s` 复位阶段，期间会把机械臂移回起始位，适合"边评估边补数据"。键盘：`n`=结束本轮，`r`=重录，`q`=停止。

---

## 评估操作

1. 将机器臂 + 手复位到**起始位置**，物体放到录制时的起点
2. 启动后策略**自动开始执行**（无需按任何键）
3. 观察是否成功抓取
4. 一轮结束后**手动复位**（物体 + 机械臂都回起始位），等它开始下一次
5. 到 `--duration` 时间自动停止，或按 `Ctrl+C` 提前结束

**评估指标**：成功率 = 成功次数 / 总次数

> **⚠️ 注意 1（策略是单次的）**：策略学的是"抓一次"这个任务，**不会自主循环**。抓完后它不知道该做什么会停住，需手动复位才能开始下一次。
>
> **⚠️ 注意 2（复位要彻底）**：不只要把物体放回，**机械臂也要回到起始姿势**。否则策略看到的画面超出训练分布，会反应迟钝或乱动。
>
> **⚠️ 注意 3（安全）**：首次自主运行建议手扶急停附近观察，确认动作合理。`--duration` 到时后程序会**自动把机械臂移回起始位再断开**（手会张开，属正常）。
>
> **⚠️ 注意 4（退出顺序）**：先在终端按 `Ctrl+C`，**不要先去关 Rerun 窗口**——那样进程会卡在 gRPC 推送里，`Ctrl+C` 失效。
>
> **⚠️ 注意 5（成功率预期）**：ACT 在 20 轮数据上通常 50-80% 成功率。个别位置抓不准，通常是**该点位训练数据没覆盖到**，补录即可。

---

## 迭代优化

若评估成功率不理想，按优先级调整：

| 优先级 | 优化项 | 操作 |
|---|---|---|
| 1 | 补录高质量数据 | 回 [阶段四](../04-data-collection/win.md)，加录 20-30 轮更一致的数据 |
| 2 | 增加训练步数 | 回 [阶段五](../05-training/win.md)，`--steps=100000` |
| 3 | 检查起始位一致 | 评估时每轮严格复位 |
| 4 | 调整任务描述 | 确保 `single_task` 与任务一致 |

---

至此完成 SO-ARM101 + AmazingHand 的**完整闭环**：标定 → 遥操作 → 采集 → 训练 → 部署。

---

## 故障排查

| 现象 | 原因 | 解决 |
|---|---|---|
| 报错要求 `--teleop.type` | 用了 `lerobot-record` | 部署必须用 `lerobot-rollout` |
| 模型加载失败 | 路径错/不完整 | 确认 `--policy.path` 指向 `pretrained_model` 目录 |
| 策略不动 | 相机/观测错 | 确认相机索引与训练时一致；检查 `--display_data` 画面 |
| 策略乱动 | 起始位不一致/数据差 | 严格复位；补录数据 |
| **动作一卡一卡** | `--policy.n_action_steps` 调小，重新推理太频繁 | **去掉该参数用默认值**（慢机器上不要调小） |
| **抓完就停住** | 单次任务策略不会自主循环 | 正常现象，手动复位物体 + 机械臂后重新执行 |
| **运行很慢 + 帧率警告** | CPU 推理（`--device=cpu`） | 换 NVIDIA 显卡用 `--device=cuda` |
| **Ctrl+C 关不掉** | 先关了 Rerun 窗口，进程卡在 gRPC 推送 | 先在终端 Ctrl+C；已卡死用任务管理器结束 `lerobot-rollout` |
| 与训练时表现不符 | 环境差异 | 确认相机、光照、物体位置与录制时一致 |
