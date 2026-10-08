# Stage 5: Model Training (Linux)

This stage trains a policy (ACT, etc.) on the collected dataset to produce a deployable model. **Linux is the best environment for GPU training** — CUDA torch dependencies resolve automatically, with no manual configuration needed.

---

## Prerequisites

- Completed [Stage 4: Data Collection](../04-data-collection/linux.md)
- NVIDIA GPU (recommended) and a CUDA driver (check with `nvidia-smi`)
- Dataset recorded (visible in the local cache)

---

## Step 1: Verify the GPU Environment

```bash
# Confirm the CUDA driver
nvidia-smi

# Confirm torch can use CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**Expected output**: `CUDA: True | GPU: <your GPU name>`

> **⚠️ Note (CUDA torch):** If `CUDA: False`, the CPU-only build of torch is installed. Reinstall the CUDA build:
> ```bash
> # Official index (overseas networks)
> pip install torch --index-url https://download.pytorch.org/whl/cu128
>
> # For mainland China networks, prefer the Aliyun mirror
> pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
> ```
> Alternatively, train on the CPU (`--policy.device=cpu`) — but it is much slower.
>
> **💡 Tip:** On Linux, `pip install -e ".[amazinghand]"` usually resolves a GPU build of torch (if a CUDA environment is detected). If not, reinstall using the commands above.

---

## Step 2: Train

```bash
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

> **💡 Note:** `--dataset.repo_id` and `--dataset.root` must **exactly match** the values used when [recording in Stage 4](../04-data-collection/linux.md) (`repo_id=soarm_amazing_hand_pick`, `root=~/lerobot_data`) — the local dataset is then read directly, with no HF login needed.

---

## Parameters

| Parameter | Description |
|---|---|
| `--dataset.repo_id` | Dataset name (must match the recording) |
| `--dataset.root` | Local dataset path (must match the recording) |
| `--policy.type` | Policy type; `act` is a common choice |
| `--output_dir` | Training output directory (checkpoints, logs) |
| `--job_name` | Job name (used to tell runs apart in the logs) |
| `--policy.device` | `cuda` (GPU) or `cpu` |
| `--wandb.enable` | Wandb logging; `false` disables it (no wandb account needed) |
| `--policy.push_to_hub` | Whether to push the model to HF; `false` keeps it local only |
| `--steps` | Number of training steps |

---

## What Happens During Training

- **Checkpoints**: saved automatically to `outputs/train/soarm_amazing_hand_pick/checkpoints/`
- **Logs**: loss and other metrics are displayed live in the terminal
- **Duration**: 60000 steps typically takes several hours on a consumer-grade GPU (exact time depends on the GPU)

> **⚠️ Note 1 (adjusting training steps):** `--steps=60000` is a typical value for ACT. For simple tasks you can reduce it to 30000; for complex tasks you can increase it to 100000+. Watch how the loss converges.
>
> **⚠️ Note 2 (resume after interruption):** Re-running the **same command with the same arguments** after an interruption resumes from the last checkpoint.
>
> **⚠️ Note 3 (wandb):** To visualize loss curves, enable `--wandb.enable=true` (requires `wandb login`). Disabled by default.
>
> **⚠️ Note 4 (headless servers):** If you train on an SSH/headless server, make sure nothing depends on a GUI (training itself needs no display). If you use `--display_data` or related arguments, a display server is required.
>
> **⚠️ Note 5 (background training):** For long training runs, keep the process alive with `nohup ... &` or `tmux`, so an SSH disconnect does not interrupt it:
> ```bash
> tmux new -s train
> lerobot-train --dataset.repo_id=...
> # Detach with Ctrl+B then D; reattach with tmux attach -t train
> ```
>
> **⚠️ Note 6 (AMD GPUs):** On Linux, AMD GPUs can use ROCm, but **only some discrete GPUs are supported** (e.g., the RX 6000/7000 series) — **integrated GPUs (such as the Radeon 780M) and most laptop APUs are not supported**. Such machines can only train on the CPU (`--policy.device=cpu`), which is tens of times slower and not a practical option. **We recommend training on a machine with an NVIDIA GPU or on a cloud GPU instead**, then copying the trained model back for deployment.

---

## Optional: Upload the Model to Hugging Face

After training, if you want to share the model to the cloud (for team deployment or backup):

1. Log in first (same as [Stage 4](../04-data-collection/linux.md#optional-upload-the-dataset-to-hugging-face)):
   ```bash
   hf auth login
   ```

2. Add two arguments to the training command:
   ```bash
   --policy.repo_id=<your-hf-username-or-org>/soarm_amazing_hand_act \
   --policy.push_to_hub=true \
   ```

> **⚠️ Note:** `--policy.push_to_hub=true` **requires also setting `--policy.repo_id`**; otherwise it fails with `save_checkpoint_to_hub requires --policy.repo_id`.
>
> **💡 Note:** After uploading, you can pull the model directly at deployment time with `--policy.path=<org-name>/soarm_amazing_hand_act` — no need to copy model files manually.

---

Once this stage is complete, continue to [Stage 6: Deployment & Evaluation](../06-deployment/linux.md).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `CUDA: False` | CPU-only torch build | Reinstall the CUDA build of torch |
| Out of memory (OOM) | Batch size too large | `--policy.batch_size=8` or lower |
| Dataset not found | repo_id/root mismatch | Make sure `--dataset.repo_id` and `--dataset.root` exactly match the values used when recording |
| SSH disconnects mid-training | Process killed | Train in the background with `tmux`/`nohup` |
| `wandb` error | Not logged in | `--wandb.enable=false` or `wandb login` |
