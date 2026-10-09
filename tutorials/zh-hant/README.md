# README

# SO\-ARM101 \+ AmazingHand 使用教程

本教程面向復現 **SO\-ARM101 從動臂 \+ AmazingHand 靈巧手** 的遙操作、數據採集與訓練全流程，基於 LeRobot（官方倉庫定製版）。

教程按**階段**組織，每個階段獨立成目錄，內部按操作系統拆分 `win.md`（Windows）與 `linux.md`（Linux）兩個文檔。請根據你的操作系統選擇對應文檔閱讀。

---

## 硬件與軟件概覽

|裝置|串口（示例，需替換）|舵機型號|說明|
|---|---|---|---|
|主動臂（Leader）|`COM54` / `/dev/ttyACM1`|混合型號<br>`sts3125-C001、sts3215-C044、sts3215-C046`|遙操作輸入，保留 6 號夾爪|
|從動臂（Follower）|`COM58` / `/dev/ttyACM0`|`sts3215-C018`（1\-5 號）|執行端，拆除 6 號夾爪|
|AmazingHand 靈巧手|`COM11` / `/dev/ttyACM2`|`scs0009`（8 個，ID 1\-8）|從動臂末端，獨立串口|

> **⚠️ 串口名因機器而異**：上表為示例。每台電腦的 COM 號/裝置路徑都不同，務必用 `lerobot-find-port` 確認本機實際值，並替換所有命令中的佔位參數。

> 三個裝置必須**各自獨立串口、獨立供電**。SCS0009（協定 1）與 STS3215（協定 0）不兼容於同一總線。

---

## 教程目錄結構

```Plaintext
tutorials/
├── README.md                          # 本文件（总览）
├── 01-environment/                    # 阶段一：环境搭建
│   ├── win.md                         #   Windows 环境搭建
│   └── linux.md                       #   Linux 环境搭建
├── 02-calibration/                    # 阶段二：标定
│   ├── win.md
│   └── linux.md
├── 03-teleoperation/                  # 阶段三：遥操作
│   ├── win.md
│   └── linux.md
├── 04-data-collection/                # 阶段四：数据采集
│   ├── win.md
│   └── linux.md
├── 05-training/                       # 阶段五：模型训练
│   ├── win.md
│   └── linux.md
└── 06-deployment/                     # 阶段六：部署与评估
    ├── win.md
    └── linux.md
```

---

## 推薦閱讀路徑

|步驟|階段|Windows|Linux|
|---|---|---|---|
|1|環境搭建|01\-environment/win\.md|01\-environment/linux\.md|
|2|標定|02\-calibration/win\.md|02\-calibration/linux\.md|
|3|遙操作|03\-teleoperation/win\.md|03\-teleoperation/linux\.md|
|4|數據採集|04\-data\-collection/win\.md|04\-data\-collection/linux\.md|
|5|模型訓練|05\-training/win\.md|05\-training/linux\.md|
|6|部署與評估|06\-deployment/win\.md|06\-deployment/linux\.md|

---

## 各階段核心差異速查

|方面|Windows|Linux|
|---|---|---|
|Python 環境|Miniconda \+ `conda create -n lerobot python=3.12`|Miniforge \+ 同樣命令|
|串口名|`COM54` / `COM58` / `COM11`（示例）|`/dev/ttyACM0/1/2`（示例）|
|串口權限|無需特殊配置|需 `sudo chmod 666 /dev/ttyACM*` 或 udev 規則|
|命令呼叫|conda 啟用後 `lerobot-xxx`|conda 啟用後 `lerobot-xxx`|
|CUDA 訓練|需手動裝 CUDA torch|官方支援，解析順暢|

---

## 通用注意事項

1. **先跑通階段一，再進入後續階段**——環境是後續所有命令的前提。

2. **每台電腦必須重新標定**：尤其是手角度（`lerobot-calibrate-amazing-hand`），config 裡的角度是 AmazingHand 官方通用預設，僅作後備；`hand_angles.json` 存在時優先載入本機實測值。

3. **標定檔案位置**：`~/.cache/huggingface/lerobot/calibration/`，換機器需遷移或重標定。

4. **首次遙操作務必驗證方向**：夾爪張開 ↔ 手張開、捏合 ↔ 手閉合。

5. 每個階段的 `win.md` / `linux.md` 內均包含**該平台特有的注意事項**，請完整閱讀。

---

## 故障排查入口

階段文檔內附各平台故障排查表。常見問題：

- conda 未初始化/命令找不到

- 串口權限不足（Linux）

- 手/臂方向映射錯誤

- 手角度未標定導致開合異常

詳見各階段文檔。

