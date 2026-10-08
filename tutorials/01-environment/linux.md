# Stage 1: Environment Setup (Linux)

Use **Miniforge** to create an isolated Python environment and install LeRobot with AmazingHand support. Follow this page in **strict order**; each code block can be copied as a whole.

> Environment versions: Python 3.12 · PyTorch ≥ 2.10 · LeRobot 0.6.2 (the customized version in this repository) · Ubuntu 20.04/22.04 recommended

---

## Step 1: Install Miniforge

```bash
wget "https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-$(uname)-$(uname -m).sh"
```

```bash
bash Miniforge3-$(uname)-$(uname -m).sh -b
~/miniforge3/bin/conda init
source ~/.bashrc
```

```bash
conda --version
```

> Official URL (for overseas networks): `https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh`

---

## Step 2: Configure conda mirrors (China mainland networks)

```bash
conda config --remove-key channels
```

```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` has been decommissioned (404); do not add it. If your network is unrestricted, you can skip this step.

---

## Step 3: Install build tools (required on a fresh system)

A freshly installed Ubuntu may lack build tools such as `gcc`, which are needed when installing packages such as `evdev`:

```bash
sudo apt update
sudo apt install -y build-essential
```

---

## Step 4: Create the virtual environment

```bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```bash
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Expected: `Python 3.12.x` + `64 bit`.

---

## Step 5: Install ffmpeg (required for video decoding)

LeRobot depends on ffmpeg to record/replay video data:

```bash
conda install ffmpeg -c conda-forge -y
```

---

## Step 6: Install project dependencies

```bash
cd ~/so-arm101-amazinghand
pip install -e ".[amazinghand]"
```

`amazinghand` includes: `feetech-servo-sdk` (arm motors), `rustypot` (hand motors), `pygame` (calibration GUI), `pyserial` (serial port).

> If pip is slow, configure a China mainland mirror first:
> ```bash
> pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
> ```

---

## Step 7: Configure serial port permissions

```bash
sudo chmod 666 /dev/ttyACM*
```

> Permanent solution (udev rule, for the CP210x chip, VID `10c4`):
> ```bash
> sudo tee /etc/udev/rules.d/99-servo.rules << 'EOF'
> SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
> EOF
> sudo udevadm control --reload-rules && sudo udevadm trigger
> ```

---

## Step 8: Verify the environment

```bash
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> You should see `all OK` and `usage: lerobot-calibrate-amazing-hand ...`.

---

## Step 9: Confirm the serial ports

```bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

Or use `lerobot-find-port`. Confirm the paths of the three devices (examples: `/dev/ttyACM0`/`/dev/ttyACM1`/`/dev/ttyACM2`, **replace with your actual values**).

---

Done → [Stage 2: Calibration](../02-calibration/linux.md)

---

## Troubleshooting

| Symptom | Solution |
|---|---|
| `conda` command not found | Run `source ~/.bashrc`, or reopen the terminal after `conda init` |
| `pkgs/free` 404 | That channel is decommissioned; do not add it |
| Serial port `Permission denied` | Step 7: `sudo chmod 666` |
| Dependencies fail to install / are slow | Configure a China mainland pip mirror (hint in Step 6) |
| Install fails with an `evdev` compile error | Step 3: `sudo apt install build-essential` |
| GPU training CUDA check returns `False` | See the Stage 5 training document |
