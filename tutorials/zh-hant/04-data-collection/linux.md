# linux

# 階段四：數據採集（Linux）

本階段錄製遙操作數據集：在人工操控下採集"關節角 \+ 相機圖像"樣本，供後續訓練。數據集質素直接決定策略效果，**操作要規範、一致**。本階段**全程本地錄製，無需 HF 登入**。

---

## 前置條件

- 已完成 階段三：遙操作 並驗證方向正確

- 相機已連接並記錄索引（`lerobot-find-cameras`）

- 已確定本地數據集存儲路徑（本文示例用 `~/lerobot_data`，可自定義）

---

## 步驟 1：確認相機索引

```Bash
lerobot-find-cameras
```

記錄相機編號。例如：

- 0 號：腕部相機（wrist）

- 1 號：頂部相機（top）

> **⚠️ 注意（相機索引）**：`index_or_path` 是相機索引（0/1/2\.\.\.）或影片流路徑。不同電腦編號不同，務必先確認。

---

## 步驟 2：錄製數據集（本地儲存，無需登入）

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

> 將 `<從動臂串口>` / `<手串口>` / `<主動臂串口>` 替換為實際路徑；相機 `index_or_path` 替換為你的相機索引。

> **💡 說明**：

- `--dataset.root=~/lerobot_data`：數據集儲存到指定**本地路徑**，**無需 HF 登入**（不寫則預設存 `~/.cache/huggingface/lerobot/datasets/...`）。

- `--dataset.push_to_hub=false`：**關閉上傳**（預設會嘗試推送到 HF，需登入）。只有需要共享數據集時才改為 `true`。

- `--dataset.repo_id=soarm_amazing_hand_pick`：數據集名稱，訓練時用**同一名稱**引用。

- `--display_data=true` 需要 rerun（未裝則 `pip install "rerun-sdk>=0.24.0,<0.34.0"`）且需圖形環境，或去掉該參數（錄製不受影響）。

---

## 參數說明

|參數|說明|
|---|---|
|`--robot.cameras`|相機配置。`index_or_path` 為相機索引，`width/height/fps` **必填**|
|`--dataset.repo_id`|數據集名稱（本地標識用）|
|`--dataset.root`|數據集本地存儲路徑。**純本地錄製必加**，避免預設路徑不可控|
|`--dataset.push_to_hub`|`false`=僅本地（預設建議）；`true`=推送到 HF（需登入）|
|`--dataset.num_episodes`|錄製輪數（episode）|
|`--dataset.episode_time_s`|**每輪錄製最長秒數**（預設 60）。任務提前完成可按 Enter 提前結束；超過自動結束該輪|
|`--dataset.single_task`|任務描述，寫入數據集元數據|
|`--display_data=true`|實時顯示錄製畫面（可選）|

---

## 錄製操作規範

**每輪（episode）流程**：

1. 將機器臂 \+ 手復位到**起始位置**

2. 在終端按 Enter 開始錄製

3. 操作主動臂執行任務（如抓取方塊），**動作要慢、一致**

4. 任務完成後按 Enter 結束本輪（**不按則最多錄 60 秒**，由 `--dataset.episode_time_s` 控制，到時自動結束）

5. 重複直至達到 `num_episodes`

> **⚠️ 注意 1（起始位一致）**：每輪從**相同起始位**開始，避免數據分布混亂。建議固定一個復位姿勢。

> **⚠️ 注意 2（動作一致性）**：同一任務用相似的操作軌跡（接近角度、抓取位置、速度），策略學得更快更穩。

> **⚠️ 注意 3（錄製質素）**：寧可少錄幾輪高質素，不要大量混亂樣本。20 輪是 ACT 的起點，複雜任務建議 30\-50 輪。

> **⚠️ 注意 4（相機實時性）**：錄製時避免遮擋相機、強光變化，圖像一致性影響泛化。

---

## 數據存儲

- **本地錄製**：數據儲存在 `--dataset.root` 指定的目錄下（示例 `~/lerobot_data/soarm_amazing_hand_pick`）。

- **訓練引用**：訓練時用**同一 ****`--dataset.repo_id`**** \+ ****`--dataset.root`** 即可，無需手動移動檔案：

```Bash
lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=~/lerobot_data ...
```

- **HF 登入場景**（可選）：需要共享數據集到雲端時，改成 `--dataset.push_to_hub=true`（需 `huggingface-cli login`）。僅本地訓練**不需要**。

> **⚠️ 注意（本地 vs 雲端）**：預設教程全程本地，`--dataset.push_to_hub=false` 確保不觸發 HF 登入。只有想共享數據集才加 `true`。

---

## 步驟 3：回放驗證（可選但推薦）

錄製完成後，可用 `lerobot-replay` 回放某輪數據，驗證**數據質素 \+ 機器人動作記錄是否正確**。回放時機器人自動重演該輪動作（含手開合）。

```Bash
lerobot-replay \
  --robot.type=so101_amazing_hand \
  --robot.port=<从动臂串口> \
  --robot.hand_port=<手串口> \
  --robot.id=amazing_hand_follower \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --dataset.episode=0
```

> 將 `<從動臂串口>` / `<手串口>` 替換為實際路徑；`--dataset.episode` 為要回放的輪序號（**從 0 開始**，如錄了 20 輪則 `0`\~`19`）。

> **💡 說明**：回放前將從動臂 \+ 手**移回起始位**，避免動作衝突；回放過程中機器人會自行運動，**不要手動干預**。若回放動作與錄製時明顯不一致，說明數據質素有問題，建議重錄該輪。

---

完成本階段後，進入 階段五：模型訓練。

---

## 故障排查

|現象|原因|解決|
|---|---|---|
|相機找不到|索引錯/權限/驅動缺失|`lerobot-find-cameras` 確認；檢查 `/dev/video*` 權限（加入 `video` 組）|
|錄製中斷|串口超時|確認三裝置串口未被佔用，重試|
|圖像全黑/花屏|相機配置錯|檢查 `index_or_path`/`fps`|
|`/dev/video*` 無權限|使用者不在 video 組|`sudo usermod -a -G video $USER` 後重新登入|
|數據集為空|未正確錄製|確認每輪按 Enter 開始/結束|

