# linux

# 階段六：部署與評估（Linux）

本階段載入訓練好的策略，讓機器人**自主執行**任務，並錄製評估影片驗證效果。這是整個流程的收尾，也是檢驗訓練成果的關鍵。

---

## 前置條件

- 已完成 階段五：模型訓練

- 訓練產出 `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/`

- 相機索引已記錄

---

## 步驟 1：確認模型檔案

```Bash
ls outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model
```

應包含 `model.safetensors` 等模型檔案。

> **⚠️ 注意（模型路徑）**：`--policy.path` 必須指向 `pretrained_model` 目錄（含配置 \+ 權重），不是 checkpoint 根目錄。

---

## 步驟 2：部署評估

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

> 將 `<從動臂串口>` / `<手串口>` 替換為實際路徑；相機 `index_or_path` 替換為你的相機索引。

> **💡 說明**：使用 `lerobot-record` 但**不加 ****`--teleop.type`**，策略將自主控制機器人（替代人工遙操作）。數據儲存為評估集。`--dataset.root` / `--dataset.push_to_hub=false` 與階段四一致，純本地儲存無需 HF 登入。

---

## 評估操作

1. 將機器人 \+ 手復位到**起始位置**

2. 按 Enter 開始：策略自主執行任務

3. 觀察**是否成功抓取**（每輪結束按 Enter 繼續）

4. 重複 `num_episodes` 輪

**評估指標**：成功率 = 成功輪數 / 總輪數

> **⚠️ 注意 1（復位一致性）**：每輪從**相同起始位**開始，否則策略泛化失敗，成功率會虛低。

> **⚠️ 注意 2（安全）**：首次自主執行建議**手扶/慢速**觀察，確認策略動作合理。策略可能做出意外動作。

> **⚠️ 注意 3（成功率預期）**：ACT 在 20 輪數據上通常 50\-80% 成功率。若低於預期，回去補錄數據或調訓練步數。

> **⚠️ 注意 4（無頭環境）**：`--display_data=true` 需要顯示伺服器；無 GUI 時去掉該參數（評估仍進行，只是不實時顯示）。

---

## 迭代優化

若評估成功率不理想，按優先級調整：

|優先級|優化項|操作|
|---|---|---|
|1|補錄高質素數據|回 階段四，加錄 20\-30 輪更一致的數據|
|2|增加訓練步數|回 階段五，`--steps=100000`|
|3|檢查起始位一致|評估時每輪嚴格復位|
|4|調整任務描述|確保 `single_task` 與任務一致|

---

至此完成 SO\-ARM101 \+ AmazingHand 的**完整閉環**：標定 → 遙操作 → 採集 → 訓練 → 部署。

---

## 故障排查

|現象|原因|解決|
|---|---|---|
|模型載入失敗|路徑錯/不完整|確認 `--policy.path` 指向 `pretrained_model` 目錄|
|策略不動|相機/觀測錯|確認相機索引與訓練時一致；檢查 `/dev/video*` 權限|
|策略亂動|起始位不一致/數據差|嚴格復位；補錄數據|
|與訓練時表現不符|環境差異|確認相機、光照、物體位置與錄製時一致|

