# win

# Stage 1: Environment Setup (Windows)

Use **Miniconda** to create an isolated Python environment and install LeRobot with AmazingHand support. Run this page in **strict order**; each code block can be copied as a whole.

> Environment versions: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (customized version in this repository)

---

## Step 1: Install Miniconda

**Command-line install** (PowerShell, recommended) — use the Tsinghua mirror on Mainland China networks:

```PowerShell
curl.exe -L -o Miniconda3-latest-Windows-x86_64.exe https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Windows-x86_64.exe
```

```PowerShell
$installDir = "C:\Users\$env:USERNAME\miniconda3"
Start-Process -Wait .\Miniconda3-latest-Windows-x86_64.exe -ArgumentList "/S", "/D=$installDir"
```

```PowerShell
C:\Users\$env:USERNAME\miniconda3\Scripts\conda.exe init powershell
```

Reopen PowerShell and verify:

```PowerShell
conda --version
```

> **Graphical install** (optional): download the installer from the official site https://repo\.anaconda\.com/miniconda/Miniconda3\-latest\-Windows\-x86\_64\.exe, double-click to install, and check **"Add to PATH"**.

> If the `conda` command is not found, use **Anaconda Prompt** (Start menu) instead of PowerShell.

---

## Step 2: Configure a Domestic conda Mirror (Mainland China networks)

**Clear the default channels first, then add the Tsinghua mirror** (a fresh Miniconda ships with the official `repo.anaconda.com` channel, which triggers a ToS check and is slow):

```PowerShell
conda config --remove-key channels
```

```PowerShell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` has been taken offline (404); do not add it. If your network is unrestricted, you can skip this step.

---

## Step 3: Create a Virtual Environment

```PowerShell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```PowerShell
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Expect `Python 3.12.x` \+ `64 bit`. If `conda activate` shows no `(lerobot)` prefix, see the troubleshooting section at the end.

---

## Step 4: Install ffmpeg (required for video decoding)

LeRobot relies on ffmpeg to record and replay video data:

```PowerShell
conda install ffmpeg -c conda-forge -y
```

> If it is slow on domestic networks, use the Tsinghua conda\-forge channel you already configured. Skipping this will cause errors when recording data or playing back video.

---

## Step 5: Install Project Dependencies

```PowerShell
cd D:\Project\lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` includes: `feetech-servo-sdk` (arm motors), `rustypot` (hand motors), `pygame` (calibration GUI), `pyserial` (serial ports).

> If pip is slow, configure a domestic mirror first:

```PowerShell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Step 6: Verify the Environment

```PowerShell
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> It should display `all OK` and `usage: lerobot-calibrate-amazing-hand ...`.

---

## Step 7: Confirm the Serial Ports

```PowerShell
lerobot-find-port
```

In Device Manager → Ports \(COM & LPT\), confirm the COM numbers of the three devices (examples `COM54`/`COM58`/`COM11`, **which must be replaced with your actual values**). COM numbers change after unplugging and replugging, so rerun this to confirm.

---

Done → Stage 2: Calibration

---

## Troubleshooting

|Symptom|Solution|
|---|---|
|`conda` is not recognized as a command|Reopen the terminal / use Anaconda Prompt / `conda init powershell`|
|ToS error (repo\.anaconda\.com)|Step 2: clear the channels and keep only the Tsinghua mirror; or run `conda tos accept ...`|
|`pkgs/free` 404|That channel is offline; do not add it|
|`conda activate` shows no prefix|Execution policy issue, see below|
|Dependencies fail to install / are slow|Configure a domestic pip mirror (see the note in step 5)|

**conda activate shows no ****`(lerobot)`**** prefix** (common on Windows):

```PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "D:\Software\Miniconda3\shell\condabin\conda-hook.ps1"
conda activate lerobot
```

> Replace `D:\Software\Miniconda3` with your Miniconda installation path.

