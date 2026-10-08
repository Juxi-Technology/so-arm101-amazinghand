# Stage 1: Environment Setup (Windows)

Use **Miniconda** to create an isolated Python environment and install LeRobot with AmazingHand support. Follow this page in **strict order**; each code block can be copied as a whole.

> Environment versions: Python 3.12 · PyTorch ≥ 2.10 · LeRobot 0.6.2 (the customized version in this repository)

---

## Step 1: Install Miniconda

**Command-line installation** (PowerShell, recommended) — use the Tsinghua mirror for China mainland networks:

```powershell
curl.exe -L -o Miniconda3-latest-Windows-x86_64.exe https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Windows-x86_64.exe
```

```powershell
$installDir = "C:\Users\$env:USERNAME\miniconda3"
Start-Process -Wait .\Miniconda3-latest-Windows-x86_64.exe -ArgumentList "/S", "/D=$installDir"
```

```powershell
C:\Users\$env:USERNAME\miniconda3\Scripts\conda.exe init powershell
```

Reopen PowerShell, then verify:

```powershell
conda --version
```

> **Graphical installation** (optional): download the installer from https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe, double-click to install, and check **"Add to PATH"**.
>
> If the `conda` command cannot be found, use **Anaconda Prompt** (Start menu) instead of PowerShell.

---

## Step 2: Configure conda mirrors (China mainland networks)

**First clear the default channels, then add the Tsinghua mirrors** (a fresh Miniconda ships with the official `repo.anaconda.com` channel by default, which triggers a ToS check and is slow):

```powershell
conda config --remove-key channels
```

```powershell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` has been decommissioned (404); do not add it. If your network is unrestricted, you can skip this step.

---

## Step 3: Create the virtual environment

```powershell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```powershell
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Expected: `Python 3.12.x` + `64 bit`. If `conda activate` doesn't show the `(lerobot)` prefix, see the troubleshooting section at the end.

---

## Step 4: Install ffmpeg (required for video decoding)

LeRobot depends on ffmpeg to record/replay video data:

```powershell
conda install ffmpeg -c conda-forge -y
```

> If the network is slow in China mainland, you can use the already-configured Tsinghua conda-forge channel. Skipping this will cause errors when recording data or playing back video.

---

## Step 5: Install project dependencies

```powershell
cd D:\Project\so-arm101-amazinghand
pip install -e ".[amazinghand]"
```

`amazinghand` includes: `feetech-servo-sdk` (arm motors), `rustypot` (hand motors), `pygame` (calibration GUI), `pyserial` (serial port).

> If pip is slow, configure a China mainland mirror first:
> ```powershell
> pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
> ```

---

## Step 6: Verify the environment

```powershell
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> You should see `all OK` and `usage: lerobot-calibrate-amazing-hand ...`.

---

## Step 7: Confirm the serial ports

```powershell
lerobot-find-port
```

In Device Manager → Ports (COM & LPT), confirm the COM numbers of the three devices (examples: `COM54`/`COM58`/`COM11`, **replace with your actual values**). COM numbers change after unplugging and replugging, so rerun to confirm.

---

Done → [Stage 2: Calibration](../02-calibration/win.md)

---

## Troubleshooting

| Symptom | Solution |
|---|---|
| `conda` is not recognized as a command | Reopen the terminal / use Anaconda Prompt / run `conda init powershell` |
| ToS error (repo.anaconda.com) | Step 2: clear the channels and keep only the Tsinghua mirrors; or run `conda tos accept ...` |
| `pkgs/free` 404 | That channel is decommissioned; do not add it |
| `conda activate` shows no prefix | Execution policy issue, see below |
| Dependencies fail to install / are slow | Configure a China mainland pip mirror (hint in Step 5) |

**`conda activate` shows no `(lerobot)` prefix** (common on Windows):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "D:\Software\Miniconda3\shell\condabin\conda-hook.ps1"
conda activate lerobot
```

> Replace `D:\Software\Miniconda3` with your Miniconda installation path.
