# win

# ステージ5：モデル訓練（Windows）

本ステージでは収集したデータセットを用いてポリシー（ACT など）を訓練し、デプロイ可能なモデルを生成します。訓練は最も時間がかかる工程で、**NVIDIA GPU の使用を推奨します**。

---

## 前提条件

- ステージ4：データ収集 を完了している

- NVIDIA GPU（推奨）、CUDA ドライバ

- データセットを記録済み（ローカルキャッシュで確認可能）

---

## ステップ 1：GPU 環境の確認

```PowerShell
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**期待される出力**：`CUDA: True | GPU: <your_gpu_name>`

> **⚠️ 注意（CUDA torch）**：`CUDA: False` の場合は、CPU 版の torch がインストールされています。CUDA 版を再インストールする必要があります：

```PowerShell
# 公式リポジトリ（海外ネットワーク）
pip install torch --index-url https://download.pytorch.org/whl/cu128

# 中国本土のネットワークでは Alibaba Cloud ミラーを優先
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
```

> または CPU で訓練します（`--policy.device=cpu`、ただし速度は大幅に遅く、複雑なタスクには現実的ではありません）。

---

## ステップ 2：訓練

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

> **💡 説明**：`--dataset.repo_id` と `--dataset.root` はステージ4 の記録時と**完全に一致**させる必要があります（`repo_id=soarm_amazing_hand_pick`、`root=D:\lerobot_data`）。これでローカルデータセットを読み込め、HF ログインは不要です。

---

## パラメータ説明

|パラメータ|説明|
|---|---|
|`--dataset.repo_id`|データセット名（記録時と一致）|
|`--dataset.root`|データセットのローカルパス（記録時と一致）|
|`--policy.type`|ポリシーの種類。`act` が一般的な選択|
|`--output_dir`|訓練の出力ディレクトリ（checkpoints、ログ）|
|`--job_name`|ジョブ名（ログの識別用）|
|`--policy.device`|`cuda`（GPU）または `cpu`|
|`--wandb.enable`|重みのログ。`false` で無効（wandb アカウント不要）|
|`--policy.push_to_hub`|モデルを HF へプッシュするか。`false` はローカルのみ|
|`--steps`|訓練ステップ数|

---

## 訓練プロセスの説明

- **checkpoints**：各ステップで自動的に `outputs/train/soarm_amazing_hand_pick/checkpoints/` に保存されます

- **ログ**：ターミナルに loss などの指標をリアルタイム表示します

- **所要時間**：60000 ステップはコンシューマー向け GPU で通常数時間です（グラフィックカードによります）

> **⚠️ 注意 1（ステップ数の調整）**：`--steps=60000` は ACT の典型的な値です。単純なタスクなら 30000 に減らし、複雑なタスクなら 100000\+ に増やせます。loss の収束を観察してください。

> **⚠️ 注意 2（訓練中断からの再開）**：中断後に**同じパラメータのコマンド**を再実行すると、最後の checkpoint から再開します。

> **⚠️ 注意 3（wandb）**：loss 曲線を可視化したい場合は `--wandb.enable=true` を有効にできます（`wandb login` が必要）。デフォルトは無効です。

> **⚠️ 注意 4（メモリ/VRAM）**：VRAM が不足する場合は `--policy.batch_size=8` を追加できます（バッチサイズを下げる）；動画デコードのメモリが不足する場合は `width/height` を小さくします。

---

本ステージを完了したら、ステージ6：デプロイと評価 に進みます。

---

## トラブルシューティング

|現象|原因|解決|
|---|---|---|
|`CUDA: False`|CPU 版 torch|CUDA 版 torch を再インストール|
|VRAM 不足（OOM）|バッチサイズが大きすぎる|`--policy.batch_size=8` またはそれ以下|
|データセットが見つからない|repo\_id/root が不一致|記録時と `--dataset.repo_id` および `--dataset.root` が完全に一致するか確認|
|訓練が遅い|CPU 訓練|GPU を使用；または `--steps` を減らす|
|`wandb` がエラー|未ログイン|`--wandb.enable=false` または `wandb login`|

