# linux

# 階段一：環境搭建（Linux）

使用 **Miniforge** 建立獨立 Python 環境，安裝 LeRobot 及 AmazingHand 支援。本頁按**嚴格順序**執行，每個代碼塊可整體複製。

> 環境版本：Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2（本倉庫定製版）· 推薦 Ubuntu 20\.04/22\.04

---

## 步驟 1：安裝 Miniforge

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

> 官方地址（海外網絡）：`https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh`

---

## 步驟 2：配置 conda 國內源（中國大陸網絡）

```Bash
conda config --remove-key channels
```

```Bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` 已下線（404），不要添加。網絡不限可跳過本步驟。

---

## 步驟 3：安裝編譯工具（新系統必需）

新裝的 Ubuntu 可能缺 `gcc` 等編譯工具，安裝 `evdev` 等包時需要：

```Bash
sudo apt update
sudo apt install -y build-essential
```

---

## 步驟 4：建立虛擬環境

```Bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```Bash
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> 預期 `Python 3.12.x` \+ `64 bit`。

---

## 步驟 5：安裝 ffmpeg（影片解碼必需）

LeRobot 錄製/回放影片數據依賴 ffmpeg：

```Bash
conda install ffmpeg -c conda-forge -y
```

---

## 步驟 6：安裝項目依賴

```Bash
cd ~/lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` 包含：`feetech-servo-sdk`（臂電機）、`rustypot`（手電機）、`pygame`（標定 GUI）、`pyserial`（串口）。

> pip 慢時先配置國內源：

```Bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 步驟 7：配置串口權限

```Bash
sudo chmod 666 /dev/ttyACM*
```

> 永久方案（udev 規則，針對 CP210x 芯片，VID `10c4`）：

```Bash
sudo tee /etc/udev/rules.d/99-servo.rules << 'EOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## 步驟 8：驗證環境

```Bash
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> 應顯示 `all OK` 和 `usage: lerobot-calibrate-amazing-hand ...`。

---

## 步驟 9：確認串口

```Bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

或 `lerobot-find-port`。確認三裝置路徑（示例 `/dev/ttyACM0`/`/dev/ttyACM1`/`/dev/ttyACM2`，**需替換為你的實際值**）。

---

完成 → 階段二：標定

---

## 故障排查

|現象|解決|
|---|---|
|`conda` 命令找不到|`source ~/.bashrc` 或 `conda init` 後重開終端|
|`pkgs/free` 404|該通道已下線，不要添加|
|串口 `Permission denied`|步驟 7 `sudo chmod 666`|
|依賴裝不上/慢|配置 pip 國內源（步驟 6 提示）|
|安裝報 `evdev` 編譯錯|步驟 3 `sudo apt install build-essential`|
|GPU 訓練 CUDA 檢查 `False`|見階段五訓練文檔|

