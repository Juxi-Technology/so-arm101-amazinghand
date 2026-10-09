# win

# 階段三：遙操作（Windows）

本階段啟動遙操作閉環：主動臂控制從動臂運動、夾爪控制 AmazingHand 開合。這是驗證整套系統是否正常工作的關鍵階段。

---

## 前置條件

- 已完成 階段一：環境搭建 和 階段二：標定

- 三裝置已上電、串口已記錄

---

## 執行遙操作

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<从动臂COM> --robot.hand_port=<手COM> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<主动臂COM> --teleop.id=amazing_hand_leader
```

> 將 `<從動臂COM>` / `<手COM>` / `<主動臂COM>` 替換為你機器實際的 COM 號（示例 `COM58` / `COM11` / `COM54`）。

**預期效果**：

- 主動臂 5 關節 → 從動臂跟隨

- 主動臂夾爪 → AmazingHand 開合（比例跟隨：半捏 = 半閉）

> **💡 參數說明**：

- `--robot.type=so101_amazing_hand`：從動臂 \+ 手組合機器人

- `--robot.port`：從動臂串口

- `--robot.hand_port`：手串口

- `--teleop.type=so101_leader`：主動臂遙操作器

- `--teleop.port`：主動臂串口

---

## 首次執行必做：方向驗證

啟動後，先做**方向測試**，確認以下兩點都正確：

|測試|操作|正確現象|
|---|---|---|
|臂跟隨|轉動主動臂各關節|從動臂同向跟隨|
|手開合|張開/捏合主動臂夾爪|夾爪張開 → 手張開；夾爪捏合 → 手閉合|

> **⚠️ 注意（方向反了怎麼辦）**：

- **手開合方向反**（張開夾爪手反而閉合）：說明手角度標定不準，重新執行標定工具（含夾爪方向標定），儲存後自動生效，**無需手動改檔案**。參見 階段二：標定。

- **夾爪映射方向反**（夾爪張開手反而閉合）：同上，標定時在主動臂夾爪**張開**時點 `[Capture Open]`、**捏合**時點 `[Capture Close]`，工具自動記錄並儲存 `gripper_open_pos`/`gripper_close_pos`，啟動時自動載入。

> 修改後**重新執行遙操作**驗證。

---

## 比例跟隨驗證

方向正確後，驗證比例細膩度：

1. **緩慢**張開夾爪 → 手應**平滑**張開（無跳變）

2. 夾爪停在**中間** → 手也應停在中間

3. 快速張合 → 手快速回應，無卡頓

> **⚠️ 注意（手開合過度的歷史問題）**：若手在夾爪開一半時就閉合，多為手角度標定時"張開/握拳"位置不準。重新執行標定步驟 3（手角度 GUI），標定更精確的開合位置。

---

## 可選：帶攝像頭的可視化

加 `--robot.cameras` 接入相機、`--display_data=true` 打開 Rerun 可視化視窗（實時顯示相機圖像 \+ 關節狀態）：

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<从动臂COM> --robot.hand_port=<手COM> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<主动臂COM> --teleop.id=amazing_hand_leader --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --display_data=true
```

> **💡 說明**：

- `index_or_path` 為相機索引，先用 `lerobot-find-cameras` 確認（不同機器編號不同）。

- `fourcc: "MJPG"` 可選，可顯著降低 USB 攝像頭帶寬佔用（改用 MJPEG 壓縮），卡頓時可加。

- 相機只需一個時，刪掉對應一行（如 `top`）即可。

> **⚠️ 注意（rerun 依賴）**：`--display_data=true` 需要 rerun 可視化包，未安裝時執行：

```PowerShell
pip install "rerun-sdk>=0.24.0,<0.34.0"
```

> 需要 Rerun Viewer 可執行檔案。Windows 下若報 `Failed to find Rerun Viewer executable`，說明缺 GUI 查看器。**不影響遙操作**，去掉 `--display_data=true` 即可。

---

## 退出

按 `Ctrl+C` 停止。程式自動：

1. 解除 8 個手舵機扭矩

2. 斷開從動臂/主動臂串口

3. 斷開相機（如有）

> **⚠️ 注意**：正常退出前**不要直接關終端**，否則可能殘留串口佔用。若異常退出後串口被佔用，重插 USB 或重啟終端進程。

---

## 故障排查

|現象|原因|解決|
|---|---|---|
|手方向反|手角度或夾爪映射反|見上文"方向驗證"，交換角度或調整映射|
|手開合過度/不足|手角度標定不準|重標手角度 GUI|
|臂不跟隨|標定缺失/串口錯|確認從動臂已標定、`--robot.port` 正確|
|rerun 報錯|可視化依賴缺失|去掉 `--display_data=true`|
|串口被佔用|上次異常退出|關閉佔用進程或重插 USB|

