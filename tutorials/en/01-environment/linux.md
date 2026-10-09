# linux

# Stage 1: Environment Setup (Linux)

Use **Miniforge** to create an isolated Python environment and install LeRobot with AmazingHand support. Run this page in **strict order**; each code block can be copied as a whole.

> Environment versions: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (customized version in this repository) · Ubuntu 20\.04/22\.04 recommended

---

## Step 1: Install Miniforge

```Bash
wget "https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-$(uname)-$(uname -m).sh"
```

```Bash
bash Miniforge3-$(uname)-$(uname -m).sh -b
~/miniforge3/bin/conda init
source ~/.bashrc
```

```Bash
conda --version
```

> Official address (for overseas networks): `https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh`

---

## Step 2: Configure a Domestic conda Mirror (Mainland China networks)

```Bash
conda config --remove-key channels
```

```Bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` has been taken offline (404); do not add it. If your network is unrestricted, you can skip this step.

---

## Step 3: Install Build Tools (required on a fresh system)

A freshly installed Ubuntu may lack build tools such as `gcc`, which are needed to install packages like `evdev`:

```Bash
sudo apt update
sudo apt install -y build-essential
```

---

## Step 4: Create a Virtual Environment

```Bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```Bash
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Expect `Python 3.12.x` \+ `64 bit`.

---

## Step 5: Install ffmpeg (required for video decoding)

LeRobot relies on ffmpeg to record and replay video data:

```Bash
conda install ffmpeg -c conda-forge -y
```

---

## Step 6: Install Project Dependencies

```Bash
cd ~/lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` includes: `feetech-servo-sdk` (arm motors), `rustypot` (hand motors), `pygame` (calibration GUI), `pyserial` (serial ports).

> If pip is slow, configure a domestic mirror first:

```Bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Step 7: Configure Serial Port Permissions

```Bash
sudo chmod 666 /dev/ttyACM*
```

> Permanent solution (udev rule, for the CP210x chip, VID `10c4`):

```Bash
sudo tee /etc/udev/rules.d/99-servo.rules << 'EOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## Step 8: Verify the Environment

```Bash
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> It should display `all OK` and `usage: lerobot-calibrate-amazing-hand ...`.

---

## Step 9: Confirm the Serial Ports

```Bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

Or use `lerobot-find-port`. Confirm the paths of the three devices (examples `/dev/ttyACM0`/`/dev/ttyACM1`/`/dev/ttyACM2`, **which must be replaced with your actual values**).

---

Done → Stage 2: Calibration

---

## Troubleshooting

|Symptom|Solution|
|---|---|
|`conda` command not found|`source ~/.bashrc`, or reopen the terminal after `conda init`|
|`pkgs/free` 404|That channel is offline; do not add it|
|Serial port `Permission denied`|Step 7 `sudo chmod 666`|
|Dependencies fail to install / are slow|Configure a domestic pip mirror (see the note in step 6)|
|`evdev` compilation error during install|Step 3 `sudo apt install build-essential`|
|GPU training CUDA check `False`|See the Stage 5 training document|

