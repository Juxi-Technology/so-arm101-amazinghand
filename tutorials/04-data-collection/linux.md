# 阶段四：数据采集（Linux）

本阶段录制遥操作数据集：在人工操控下采集"关节角 + 相机图像"样本，供后续训练。数据集质量直接决定策略效果，**操作要规范、一致**。本阶段**全程本地录制，无需 HF 登录**。

---

## 前置条件

- 已完成 [阶段三：遥操作](../03-teleoperation/linux.md) 并验证方向正确
- 相机已连接并记录索引（`lerobot-find-cameras`）
- 已确定本地数据集存储路径（本文示例用 `~/lerobot_data`，可自定义）

---

## 步骤 1：确认相机索引

```bash
lerobot-find-cameras
```

记录相机编号。例如：
- 0 号：腕部相机（wrist）
- 1 号：顶部相机（top）

> **⚠️ 注意（相机索引）**：`index_or_path` 是相机索引（0/1/2...）或视频流路径。不同电脑编号不同，务必先确认。

---

## 步骤 2：录制数据集（本地保存，无需登录）

```bash
lerobot-record \
  --robot.type=so101_amazing_hand \
  --robot.port=<从动臂串口> \
  --robot.hand_port=<手串口> \
  --robot.id=amazing_hand_follower \
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' \
  --teleop.type=so101_leader \
  --teleop.port=<主动臂串口> \
  --teleop.id=amazing_hand_leader \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --dataset.push_to_hub=false \
  --dataset.num_episodes=20 \
  --dataset.single_task="Pick up the cube with the dexterous hand" \
  --display_data=true
```

> 将 `<从动臂串口>` / `<手串口>` / `<主动臂串口>` 替换为实际路径；相机 `index_or_path` 替换为你的相机索引。
>
> **💡 说明**：
> - `--dataset.root=~/lerobot_data`：数据集保存到指定**本地路径**，**无需 HF 登录**（不写则默认存 `~/.cache/huggingface/lerobot/datasets/...`）。
> - `--dataset.push_to_hub=false`：**关闭上传**（默认会尝试推送到 HF，需登录）。只有需要共享数据集时才改为 `true`。
> - `--dataset.repo_id=soarm_amazing_hand_pick`：数据集名称，训练时用**同一名称**引用。
> - `--display_data=true` 需要 rerun（未装则 `pip install "rerun-sdk>=0.24.0,<0.34.0"`）且需图形环境，或去掉该参数（录制不受影响）。

---

## 参数说明

| 参数 | 说明 |
|---|---|
| `--robot.cameras` | 相机配置。`index_or_path` 为相机索引，`width/height/fps` **必填** |
| `--dataset.repo_id` | 数据集名称（本地标识用） |
| `--dataset.root` | 数据集本地存储路径。**纯本地录制必加**，避免默认路径不可控 |
| `--dataset.push_to_hub` | `false`=仅本地（默认建议）；`true`=推送到 HF（需登录） |
| `--dataset.num_episodes` | 录制轮数（episode） |
| `--dataset.episode_time_s` | **每轮录制最长秒数**（默认 60）。任务提前完成可按 Enter 提前结束；超过自动结束该轮 |
| `--dataset.single_task` | 任务描述，写入数据集元数据 |
| `--display_data=true` | 实时显示录制画面（可选） |

---

## 录制操作规范

**每轮（episode）流程**：
1. 将机器臂 + 手复位到**起始位置**
2. 在终端按 Enter 开始录制
3. 操作主动臂执行任务（如抓取方块），**动作要慢、一致**
4. 任务完成后按 Enter 结束本轮（**不按则最多录 60 秒**，由 `--dataset.episode_time_s` 控制，到时自动结束）
5. 重复直至达到 `num_episodes`

> **⚠️ 注意 1（起始位一致）**：每轮从**相同起始位**开始，避免数据分布混乱。建议固定一个复位姿势。
>
> **⚠️ 注意 2（动作一致性）**：同一任务用相似的操作轨迹（接近角度、抓取位置、速度），策略学得更快更稳。
>
> **⚠️ 注意 3（录制质量）**：宁可少录几轮高质量，不要大量混乱样本。20 轮是 ACT 的起点，复杂任务建议 30-50 轮。
>
> **⚠️ 注意 4（相机实时性）**：录制时避免遮挡相机、强光变化，图像一致性影响泛化。

---

## 数据存储

- **本地录制**：数据保存在 `--dataset.root` 指定的目录下（示例 `~/lerobot_data/soarm_amazing_hand_pick`）。
- **训练引用**：训练时用**同一 `--dataset.repo_id` + `--dataset.root`** 即可，无需手动移动文件：
  ```bash
  lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=~/lerobot_data ...
  ```
- **HF 上传场景**（可选）：见下方[可选：上传数据集到 Hugging Face](#可选上传数据集到-hugging-face)。

> **⚠️ 注意（本地 vs 云端）**：默认教程全程本地，`--dataset.push_to_hub=false` 确保不触发 HF 登录。只有想共享数据集才加 `true`。

---

## 可选：上传数据集到 Hugging Face

如需把数据集共享到云端（多人/多机训练、或交付给团队），按以下步骤。**仅本地训练可跳过本节。**

### 1. 登录

先激活 lerobot 环境，再登录（新版 Hugging Face CLI 用 `hf` 命令，不再是 `huggingface-cli`）：

```bash
hf auth login
```

粘贴在 https://huggingface.co/settings/tokens 生成的 **Write** 权限 token，验证：

```bash
hf auth whoami
```

### 2. 录制时开启上传

在[步骤 2](#步骤-2录制数据集本地保存无需登录)的录制命令里，改两处：

```bash
--dataset.repo_id=<你的HF用户名或组织名>/soarm_amazing_hand_pick \
--dataset.push_to_hub=true \
--dataset.private=true \
```

> **⚠️ 注意 1（组织名）**：上传到企业/组织名下时，`repo_id` 用**组织名**（不是个人用户名），且你的账号需是该组织内有 write 权限的成员。上传到个人名下则用你的用户名。
>
> **⚠️ 注意 2（网络）**：中国大陆直连 `huggingface.co` 经常超时。**hf-mirror.com 等镜像只支持下载、不支持上传**，上传必须能直连官方站点（代理/VPN 或企业专线）。可先用 `curl -I https://huggingface.co` 测试连通性。
>
> **⚠️ 注意 3（权限）**：token 必须是 **Write** 类型，只读 token 上传会报 403。
>
> **⚠️ 注意 4（私有）**：`--dataset.private=true` 为私有仓库；企业共享可去掉或设 `false`。

---

## 步骤 3：回放验证（可选但推荐）

录制完成后，可用 `lerobot-replay` 回放某轮数据，验证**数据质量 + 机器人动作记录是否正确**。回放时机器人自动重演该轮动作（含手开合）。

```bash
lerobot-replay \
  --robot.type=so101_amazing_hand \
  --robot.port=<从动臂串口> \
  --robot.hand_port=<手串口> \
  --robot.id=amazing_hand_follower \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --dataset.episode=0
```

> 将 `<从动臂串口>` / `<手串口>` 替换为实际路径；`--dataset.episode` 为要回放的轮序号（**从 0 开始**，如录了 20 轮则 `0`~`19`）。

> **💡 说明**：回放前将从动臂 + 手**移回起始位**，避免动作冲突；回放过程中机器人会自行运动，**不要手动干预**。若回放动作与录制时明显不一致，说明数据质量有问题，建议重录该轮。

---

完成本阶段后，进入 [阶段五：模型训练](../05-training/linux.md)。

---

## 故障排查

| 现象 | 原因 | 解决 |
|---|---|---|
| 相机找不到 | 索引错/权限/驱动缺失 | `lerobot-find-cameras` 确认；检查 `/dev/video*` 权限（加入 `video` 组） |
| 录制中断 | 串口超时 | 确认三设备串口未被占用，重试 |
| 图像全黑/花屏 | 相机配置错 | 检查 `index_or_path`/`fps` |
| `/dev/video*` 无权限 | 用户不在 video 组 | `sudo usermod -a -G video $USER` 后重新登录 |
| 数据集为空 | 未正确录制 | 确认每轮按 Enter 开始/结束 |
