# linux

# 階段五：模型訓練（Linux）

本階段使用採集的數據集訓練策略（ACT 等），產出可部署的模型。**Linux 是 GPU 訓練的最佳環境**——CUDA torch 依賴自動解析，無需手動配置。

---

## 前置條件

- 已完成 階段四：數據採集

- NVIDIA GPU（推薦）、CUDA 驅動（`nvidia-smi` 可查）

- 數據集已錄製（本地緩存可見）

---

## 步驟 1：確認 GPU 環境

```Bash
# 確認 CUDA 驅動
nvidia-smi

# 確認 torch 可用 CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**期望輸出**：`CUDA: True | GPU: <你的顯卡名>`

> **⚠️ 注意（CUDA torch）**：若 `CUDA: False`，說明裝的是 CPU 版 torch。重裝 CUDA 版：

```Bash
# 官方源（海外網路）
pip install torch --index-url https://download.pytorch.org/whl/cu128

# 中國大陸網路優先用阿里雲鏡像
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
```

> 或用 CPU 訓練（`--policy.device=cpu`，但速度慢很多）。

> **💡 提示**：`pip install -e ".[amazinghand]"` 在 Linux 上通常已解析 GPU 版 torch（若檢測到 CUDA 環境）。若否，按上述命令重裝。

---

## 步驟 2：訓練

```Bash
lerobot-train \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --policy.type=act \
  --output_dir=outputs/train/soarm_amazing_hand_pick \
  --job_name=soarm_amazing_hand_pick \
  --policy.device=cuda \
  --wandb.enable=false \
  --policy.push_to_hub=false \
  --steps=60000
```

> **💡 說明**：`--dataset.repo_id` 和 `--dataset.root` 必須與階段四錄製時**完全一致**（`repo_id=soarm_amazing_hand_pick`、`root=~/lerobot_data`），即可讀取本地數據集，無需 HF 登入。

---

## 參數說明

|參數|說明|
|---|---|
|`--dataset.repo_id`|數據集名稱（與錄製時一致）|
|`--dataset.root`|數據集本地路徑（與錄製時一致）|
|`--policy.type`|策略類型，`act` 為常用選擇|
|`--output_dir`|訓練輸出目錄（checkpoints、日誌）|
|`--job_name`|任務名（用於日誌區分）|
|`--policy.device`|`cuda`（GPU）或 `cpu`|
|`--wandb.enable`|權重日誌，`false` 關閉（無需 wandb 帳號）|
|`--policy.push_to_hub`|是否推送模型到 HF，`false` 僅本地|
|`--steps`|訓練步數|

---

## 訓練過程說明

- **checkpoints**：每步自動儲存到 `outputs/train/soarm_amazing_hand_pick/checkpoints/`

- **日誌**：終端實時顯示 loss 等指標

- **時長**：60000 步在消費級 GPU 上通常數小時（具體取決顯卡）

> **⚠️ 注意 1（步數調整）**：`--steps=60000` 為 ACT 典型值。任務簡單可減至 30000，複雜任務可加至 100000\+。觀察 loss 收斂情況。

> **⚠️ 注意 2（訓練中斷續跑）**：中斷後重新執行**同參數命令**會從最後 checkpoint 繼續。

> **⚠️ 注意 3（wandb）**：如需可視化 loss 曲線，可開 `--wandb.enable=true`（需 `wandb login`）。預設關閉。

> **⚠️ 注意 4（無頭伺服器）**：若在 SSH/無顯示器伺服器訓練，確保不要依賴 GUI（訓練本身無需顯示）。若使用 `--display_data` 相關參數則需顯示伺服器。

> **⚠️ 注意 5（後台訓練）**：長訓練建議用 `nohup ... &` 或 `tmux` 保持進程，避免 SSH 斷開中斷：

```Bash
tmux new -s train
lerobot-train --dataset.repo_id=...
# Ctrl+B 然後 D 脫離；tmux attach -t train 重新進入
```

---

完成本階段後，進入 階段六：部署與評估。

---

## 故障排查

|現象|原因|解決|
|---|---|---|
|`CUDA: False`|CPU 版 torch|重裝 CUDA 版 torch|
|顯存不足（OOM）|批大小過大|`--policy.batch_size=8` 或更低|
|數據集找不到|repo\_id/root 不一致|確認與錄製時 `--dataset.repo_id` 和 `--dataset.root` 完全一致|
|訓練中途 SSH 斷|進程被殺|用 `tmux`/`nohup` 後台訓練|
|`wandb` 報錯|未登入|`--wandb.enable=false` 或 `wandb login`|

