# win

# ステージ6：デプロイと評価（Windows）

本ステージでは訓練済みのポリシーを読み込み、ロボットに**自律的にタスクを実行**させ、評価動画を記録して効果を検証します。これはフロー全体の締めくくりであり、訓練成果を確認する要でもあります。

---

## 前提条件

- ステージ5：モデル訓練 を完了している

- 訓練により `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/` が生成されている

- カメラのインデックスを記録済み

---

## ステップ 1：モデルファイルの確認

```PowerShell
# モデルディレクトリの存在を確認
dir outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model
```

`model.safetensors` などのモデルファイルが含まれているはずです。

> **⚠️ 注意（モデルパス）**：`--policy.path` は `pretrained_model` ディレクトリ（設定 \+ 重みを含む）を指す必要があり、checkpoint のルートディレクトリではありません。

---

## ステップ 2：デプロイと評価

```PowerShell
lerobot-record `
  --robot.type=so101_amazing_hand `
  --robot.port=<follower-port> `
  --robot.hand_port=<hand-port> `
  --robot.id=amazing_hand_follower `
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' `
  --policy.path=outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model `
  --dataset.repo_id=soarm_amazing_hand_pick_eval `
  --dataset.root=D:\lerobot_data `
  --dataset.push_to_hub=false `
  --dataset.num_episodes=10 `
  --dataset.single_task="Pick up the cube with the dexterous hand" `
  --display_data=true
```

> `<follower_arm_com>` / `<hand_com>` を実際の COM 番号に置き換えます；カメラの `index_or_path` をあなたのカメラインデックスに置き換えます。

> **💡 説明**：`lerobot-record` を使用しますが**付けません ****`--teleop.type`**、ポリシーがロボットを自律的に制御します（人手による遠隔操作の代わり）。データは評価セットとして保存されます。`--dataset.root` / `--dataset.push_to_hub=false` はステージ4 と一致し、純粋なローカル保存で HF ログインは不要です。

---

## 評価操作

1. ロボット \+ ハンドを**開始位置**に復帰させる

2. Enter を押して開始：ポリシーが自律的にタスクを実行します

3. **把持に成功したか**を観察します（各エピソード終了時に Enter を押して続行）

4. `num_episodes` 回繰り返す

**評価指標**：成功率 = 成功したエピソード数 / 総エピソード数

> **⚠️ 注意 1（リセットの一貫性）**：各エピソードは**同じ開始位置**から始めます。そうしないとポリシーの汎化が失敗し、成功率が実際より低く出ます。

> **⚠️ 注意 2（安全）**：初回の自律実行は**手で支えながら/低速で**観察し、ポリシーの動作が妥当か確認することを推奨します。ポリシーは予期しない動作をする可能性があります。

> **⚠️ 注意 3（成功率の目安）**：ACT は 20 エピソードのデータで通常 50\-80% の成功率です。期待より低い場合は、戻ってデータを追加記録するか、訓練ステップ数を調整してください。

---

## 反復最適化

評価の成功率が芳しくない場合は、優先度に従って調整します：

|優先度|最適化項目|操作|
|---|---|---|
|1|高品質データの追加記録|ステージ4 に戻り、より一貫したデータを 20\-30 エピソード追加記録する|
|2|訓練ステップ数の増加|ステージ5 に戻り、`--steps=100000`|
|3|開始位置の一致を確認|評価時に各エピソードを厳密にリセットする|
|4|タスク説明の調整|`single_task` がタスクと一致していることを確認する|

---

これで SO\-ARM101 \+ AmazingHand の**完全なクローズドループ**が完成します：キャリブレーション → 遠隔操作 → 収集 → 訓練 → デプロイ。

---

## トラブルシューティング

|現象|原因|解決|
|---|---|---|
|モデルの読み込みに失敗|パスが誤り/不完全|`--policy.path` が `pretrained_model` ディレクトリを指しているか確認|
|ポリシーが動かない|カメラ/観測の誤り|カメラインデックスが訓練時と一致しているか確認；`--display_data` の画面を確認|
|ポリシーが勝手に動く|開始位置の不一致/データ品質が低い|厳密にリセット；データを追加記録|
|訓練時と挙動が異なる|環境の違い|カメラ、照明、物体の位置が記録時と一致しているか確認|

