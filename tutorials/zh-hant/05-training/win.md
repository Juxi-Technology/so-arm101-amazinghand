# win

# 階段五：模型訓練（Windows）

本階段使用採集的數據集訓練策略（ACT 等），產出可部署的模型。訓練是最耗時的一步，**建議使用 NVIDIA GPU**。

---

## 前置條件

- 已完成 階段四：數據採集

- NVIDIA GPU（推薦）、CUDA 驅動

- 數據集已錄製（本地緩存可見）

---

## 步驟 1：確認 GPU 環境

```PowerShell
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**期望輸出**：`CUDA: True | GPU: <你的顯卡名>`

> **⚠️ 注意（CUDA torch）**：若 `CUDA: False`，說明裝的是 CPU 版 torch。需重裝 CUDA 版：

```PowerShell
# 官方源（海外網路）
pip install torch --index-url https://download.pytorch.org/whl/cu128

# 中國大陸網路優先用阿里雲鏡像
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
```

> 或用 CPU 訓練（`--policy.device=cpu`，但速度慢很多，複雜任務不現實）。

---

## 步驟 2：訓練

```PowerShell
lerobot-train `
  --dataset.repo_id=soarm_amazing_hand_pick `
  --dataset.root=D:\lerobot_data `
  --policy.type=act `
  --output_dir=outputs/train/soarm_amazing_hand_pick `
  --job_name=soarm_amazing_hand_pick `
  --policy.device=cuda `
  --wandb.enable=false `
  --policy.push_to_hub=false `
  --steps=60000
```

> **💡 說明**：`--dataset.repo_id` 和 `--dataset.root` 必須與階段四錄製時**完全一致**（`repo_id=soarm_amazing_hand_pick`、`root=D:\lerobot_data`），即可讀取本地數據集，無需 HF 登入。

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

> **⚠️ 注意 4（記憶體/顯存）**：顯存不足可加 `--policy.batch_size=8`（降低批大小）；影片解碼記憶體不足可減小 `width/height`。

---

完成本階段後，進入 階段六：部署與評估。

---

## 故障排查

|現象|原因|解決|
|---|---|---|
|`CUDA: False`|CPU 版 torch|重裝 CUDA 版 torch|
|顯存不足（OOM）|批大小過大|`--policy.batch_size=8` 或更低|
|數據集找不到|repo\_id/root 不一致|確認與錄製時 `--dataset.repo_id` 和 `--dataset.root` 完全一致|
|訓練慢|CPU 訓練|用 GPU；或減小 `--steps`|
|`wandb` 報錯|未登入|`--wandb.enable=false` 或 `wandb login`|

