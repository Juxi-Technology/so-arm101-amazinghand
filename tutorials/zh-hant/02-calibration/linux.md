# linux

# 階段二：標定（Linux）

本階段對三個裝置進行標定：主動臂、從動臂、AmazingHand 手。標定是遙操作正確性的前提，**必須完成本階段才能進入遙操作**。

> **標定順序**：主動臂 → 從動臂\+手 → 手角度。每步都需**終端交互**（物理操作 \+ 按鍵）。

> **⚠️ 通用提醒**：本頁命令中的串口參數為**示例佔位**，必須替換為你機器實際的串口路徑（見階段一記錄的串口）。

---

## 前置條件

- 已完成 階段一：環境搭建

- conda 環境 `lerobot` 已啟用

- 串口權限已配置（階段一第 5 節）

- 三裝置串口已記錄

- 裝置已上電、獨立供電

---

## 步驟 1：標定主動臂

```Bash
lerobot-calibrate \
  --teleop.type=so101_leader --teleop.port=<主动臂串口> --teleop.id=amazing_hand_leader
```

> 將 `<主動臂串口>` 替換為你機器的實際路徑（示例 `/dev/ttyACM1`）。

**交互步驟**：

1. 將主動臂**所有關節移到中間位**，按 Enter

2. 將**每個關節依次推到最大/最小範圍**，完成後按 Enter

**驗證**：標定檔案自動儲存到
`~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/amazing_hand_leader.json`

> **⚠️ 注意 1（夾爪必標）**：6 號夾爪舵機範圍作為 `gripper.pos`（0\~100）歸一化基準。夾爪務必從全開推到全閉，標定到位，否則手開合比例失真。

> **⚠️ 注意 2（自由轉動）**：標定時機械臂需能自由轉動，確保舵機空載。

> **⚠️ 注意 3（權限）**：若報串口 `Permission denied`，先執行 `sudo chmod 666 /dev/ttyACM*`（或確認階段一已配 udev 規則）。

---

## 步驟 2：標定從動臂（同時連接手）

```Bash
lerobot-calibrate \
  --robot.type=so101_amazing_hand --robot.port=<从动臂串口> --robot.hand_port=<手串口> --robot.id=amazing_hand_follower
```

> 將 `<從動臂串口>` / `<手串口>` 替換為實際路徑（示例 `/dev/ttyACM0` / `/dev/ttyACM2`）。

**交互步驟**：

1. 將從動臂 **5 個關節**（無 6 號）移到中間位，按 Enter

2. 將各關節走全行程，按 Enter

**驗證**：標定檔案儲存到
`~/.cache/huggingface/lerobot/calibration/robots/so101_amazing_hand/amazing_hand_follower.json`

> **⚠️ 注意 1（手扭矩自動啟用）**：此命令連接時**自動啟用 8 個手舵機扭矩**（日誌顯示 `enabling AmazingHand torque`），標定結束手會張開，屬正常現象。

> **⚠️ 注意 2（不會彈手 GUI）**：手角度**不使用** lerobot 的 `RangeFinderGUI`，從動臂標定結束即完成。手角度用步驟 3 的專用工具。

> **⚠️ 注意 3（串口佔用）**：此步驟佔用手串口。**不要**同時執行其他佔用該串口的進程。

---

## 步驟 3：標定手角度 \+ 夾爪方向（專用 GUI）

```Bash
lerobot-calibrate-amazing-hand --hand_port <手串口> --leader_port <主动臂串口>
```

> 將 `<手串口>` / `<主動臂串口>` 替換為實際路徑（示例 `/dev/ttyACM2` / `/dev/ttyACM1`）。`--leader_port` 用於同步標定**夾爪方向**（見下）。

> **⚠️ 注意（無顯示環境）**：GUI 需要圖形桌面。若在無顯示器/SSH 環境執行，會報 `pygame.error: video system not initialized`。解決方案：

- 在本地圖形會話執行；或

- 透過 X11 轉發（`ssh -X`）執行。

**GUI 操作**：

1. 拖動 4 根手指滑塊（index/middle/ring/thumb），使手**完全張開**，點擊 **`Save Open`**

2. 拖動滑塊使手**完全握拳**，點擊 **`Save Close`**

3. **主動臂夾爪張開**，點擊 **`Capture Open`**（GUI 實時顯示 `gripper.pos`，張開時應接近 100）

4. **主動臂夾爪捏合**，點擊 **`Capture Close`**（捏合時應接近 0）

5. **自動儲存**：以上四個值都設定後，視窗頂部彈出綠色橫幅 `AUTO-SAVED to .../hand_angles.json`，終端同步列印路徑

6. 關閉視窗（手自動解除扭矩）

**驗證**：角度與夾爪映射儲存到
`~/.cache/huggingface/lerobot/calibration/robots/so101_amazing_hand/hand_angles.json`

> **⚠️ 注意 1（必須標定）**：**每台新電腦/每隻手都必須執行本步驟**。config 裡的角度是 AmazingHand 官方通用預設，僅作後備；`hand_angles.json` 存在時優先載入你的實測值。不標定可能導致開合方向/範圍錯誤。

> **⚠️ 注意 2（自動載入）**：機器人每次啟動讀取 `hand_angles.json`（含 `gripper_open_pos`/`gripper_close_pos`）覆蓋 config 預設值，**無需改代碼**。夾爪方向會因主動臂而異，標定一次即可。

> **⚠️ 注意 3（滑塊語義）**：滑塊向 `+` 方向使該指 m1 向 `+angle`、m2 向 `-angle`（鏡像）。以**手的實際姿態**判斷張開/握拳，不必關注角度數值。

> **⚠️ 注意 4（精確標定）**：標定"完全張開"時不要過度（手指歪斜/散開），"完全握拳"時不要過度擠壓（舵機持續受壓）。

> **⚠️ 注意 5（Capture 順序）**：`Capture Open` / `Capture Close` 對應**主動臂夾爪**的開合，不是手手指。若手張開方向反了，多半是這裡標反或手角度標反，重標即可。

---

## 重標定

只需重標某一部分時：

- **只重標手** → 僅執行步驟 3

- **只重標從動臂** → 僅執行步驟 2（會順帶啟用手扭矩）

- **全部重標** → 步驟 1 → 2 → 3

> **⚠️ 注意**：步驟 2 和步驟 3 **不能同時執行**（都佔用手串口）。

---

完成本階段後，進入 階段三：遙操作。

---

## 故障排查

|現象|原因|解決|
|---|---|---|
|串口 `Permission denied`|權限未配置|`sudo chmod 666 /dev/ttyACM*` 或配 udev|
|標定手 GUI 打不開|無圖形環境|本地圖形會話執行，或 `ssh -X` 轉發|
|手驅動報 `Operation timed out`|串口忙碌/時序|確認手串口未被佔用，重試|
|主動臂標定報 2307 型號錯誤|臂總線被污染|確認未同時連手串口；本項目手走 rustypot 已規避|

