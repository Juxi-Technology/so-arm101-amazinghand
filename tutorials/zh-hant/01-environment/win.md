# win

# 階段一：環境搭建（Windows）

使用 **Miniconda** 建立獨立 Python 環境，安裝 LeRobot 及 AmazingHand 支援。本頁按**嚴格順序**執行，每個代碼塊可整體複製。

> 環境版本：Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2（本倉庫定製版）

---

## 步驟 1：安裝 Miniconda

**命令列安裝**（PowerShell，推薦）——中國大陸網絡用清華鏡像：

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

重開 PowerShell 後驗證：

```PowerShell
conda --version
```

> **圖形化安裝**（可選）：從官網 https://repo\.anaconda\.com/miniconda/Miniconda3\-latest\-Windows\-x86\_64\.exe 下載安裝包，雙擊安裝，勾選 **"Add to PATH"**。

> 若 `conda` 命令找不到，用 **Anaconda Prompt**（開始選單）代替 PowerShell。

---

## 步驟 2：配置 conda 國內源（中國大陸網絡）

**先清空預設源，再添加清華鏡像**（新 Miniconda 會預設帶 `repo.anaconda.com` 官方源，觸發 ToS 檢查且慢）：

```PowerShell
conda config --remove-key channels
```

```PowerShell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` 已下線（404），不要添加。網絡不限可跳過本步驟。

---

## 步驟 3：建立虛擬環境

```PowerShell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```PowerShell
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> 預期 `Python 3.12.x` \+ `64 bit`。若 `conda activate` 無 `(lerobot)` 前綴，見文末故障排查。

---

## 步驟 4：安裝 ffmpeg（影片解碼必需）

LeRobot 錄製/回放影片數據依賴 ffmpeg：

```PowerShell
conda install ffmpeg -c conda-forge -y
```

> 國內網絡若慢，可用已配置的清華 conda\-forge 通道。不裝會導致錄數據/播放影片報錯。

---

## 步驟 5：安裝項目依賴

```PowerShell
cd D:\Project\lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` 包含：`feetech-servo-sdk`（臂電機）、`rustypot`（手電機）、`pygame`（標定 GUI）、`pyserial`（串口）。

> pip 慢時先配置國內源：

```PowerShell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 步驟 6：驗證環境

```PowerShell
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> 應顯示 `all OK` 和 `usage: lerobot-calibrate-amazing-hand ...`。

---

## 步驟 7：確認串口

```PowerShell
lerobot-find-port
```

在裝置管理員 → 連接埠\(COM 和 LPT\) 確認三裝置 COM 號（示例 `COM54`/`COM58`/`COM11`，**需替換為你的實際值**）。COM 號插拔後會變，重跑確認。

---

完成 → 階段二：標定

---

## 故障排查

|現象|解決|
|---|---|
|`conda` 不是命令|重開終端 / Anaconda Prompt / `conda init powershell`|
|ToS 錯誤（repo\.anaconda\.com）|步驟 2 清空 channels 只留清華源；或 `conda tos accept ...`|
|`pkgs/free` 404|該通道已下線，不要添加|
|`conda activate` 無前綴|執行策略問題，見下|
|依賴裝不上/慢|配置 pip 國內源（步驟 5 提示）|

**conda activate 無 ****`(lerobot)`**** 前綴**（Windows 常見）：

```PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "D:\Software\Miniconda3\shell\condabin\conda-hook.ps1"
conda activate lerobot
```

> `D:\Software\Miniconda3` 替換為你的 Miniconda 安裝路徑。

