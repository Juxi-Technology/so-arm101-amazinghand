# linux

# 阶段六：部署与评估（Linux）

本阶段加载训练好的策略，让机器人**自主执行**任务，并录制评估视频验证效果。这是整个流程的收尾，也是检验训练成果的关键。

---

## 前置条件

- 已完成 阶段五：模型训练

- 训练产出 `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/`

- 相机索引已记录

---

## 步骤 1：确认模型文件

```Bash
ls outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model
```

应包含 `model.safetensors` 等模型文件。

> **⚠️ 注意（模型路径）**：`--policy.path` 必须指向 `pretrained_model` 目录（含配置 \+ 权重），不是 checkpoint 根目录。

---

## 步骤 2：部署评估

```Bash
lerobot-record \
  --robot.type=so101_amazing_hand \
  --robot.port=<从动臂串口> \
  --robot.hand_port=<手串口> \
  --robot.id=amazing_hand_follower \
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' \
  --policy.path=outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model \
  --dataset.repo_id=soarm_amazing_hand_pick_eval \
  --dataset.root=~/lerobot_data \
  --dataset.push_to_hub=false \
  --dataset.num_episodes=10 \
  --dataset.single_task="Pick up the cube with the dexterous hand" \
  --display_data=true
```

> 将 `<从动臂串口>` / `<手串口>` 替换为实际路径；相机 `index_or_path` 替换为你的相机索引。

> **💡 说明**：使用 `lerobot-record` 但**不加 ****`--teleop.type`**，策略将自主控制机器人（替代人工遥操作）。数据保存为评估集。`--dataset.root` / `--dataset.push_to_hub=false` 与阶段四一致，纯本地保存无需 HF 登录。

---

## 评估操作

1. 将机器人 \+ 手复位到**起始位置**

2. 按 Enter 开始：策略自主执行任务

3. 观察**是否成功抓取**（每轮结束按 Enter 继续）

4. 重复 `num_episodes` 轮

**评估指标**：成功率 = 成功轮数 / 总轮数

> **⚠️ 注意 1（复位一致性）**：每轮从**相同起始位**开始，否则策略泛化失败，成功率会虚低。

> **⚠️ 注意 2（安全）**：首次自主运行建议**手扶/慢速**观察，确认策略动作合理。策略可能做出意外动作。

> **⚠️ 注意 3（成功率预期）**：ACT 在 20 轮数据上通常 50\-80% 成功率。若低于预期，回去补录数据或调训练步数。

> **⚠️ 注意 4（无头环境）**：`--display_data=true` 需要显示服务器；无 GUI 时去掉该参数（评估仍进行，只是不实时显示）。

---

## 迭代优化

若评估成功率不理想，按优先级调整：

|优先级|优化项|操作|
|---|---|---|
|1|补录高质量数据|回 阶段四，加录 20\-30 轮更一致的数据|
|2|增加训练步数|回 阶段五，`--steps=100000`|
|3|检查起始位一致|评估时每轮严格复位|
|4|调整任务描述|确保 `single_task` 与任务一致|

---

至此完成 SO\-ARM101 \+ AmazingHand 的**完整闭环**：标定 → 遥操作 → 采集 → 训练 → 部署。

---

## 故障排查

|现象|原因|解决|
|---|---|---|
|模型加载失败|路径错/不完整|确认 `--policy.path` 指向 `pretrained_model` 目录|
|策略不动|相机/观测错|确认相机索引与训练时一致；检查 `/dev/video*` 权限|
|策略乱动|起始位不一致/数据差|严格复位；补录数据|
|与训练时表现不符|环境差异|确认相机、光照、物体位置与录制时一致|

