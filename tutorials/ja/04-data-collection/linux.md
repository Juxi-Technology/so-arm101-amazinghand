# linux

# ステージ4：データ収集（Linux）

本ステージでは遠隔操作データセットを記録します：人手による操作のもとで"関節角 \+ カメラ画像"のサンプルを収集し、後続の訓練に供します。データセットの品質がポリシーの効果を直接左右するため、**操作は規範的かつ一貫している**必要があります。本ステージは**全工程をローカルで記録し、HF ログインは不要**です。

---

## 前提条件

- ステージ3：遠隔操作 を完了し、方向が正しいことを検証済み

- カメラを接続し、インデックスを記録済み（`lerobot-find-cameras`）

- ローカルのデータセット保存パスを決定済み（本文では例として `~/lerobot_data` を使用、カスタマイズ可能）

---

## ステップ 1：カメラインデックスの確認

```Bash
lerobot-find-cameras
```

カメラ番号を記録します。例えば：

- 0 番：手首カメラ（wrist）

- 1 番：上部カメラ（top）

> **⚠️ 注意（カメラインデックス）**：`index_or_path` はカメラのインデックス（0/1/2\.\.\.）または映像ストリームのパスです。PC ごとに番号が異なるため、必ず先に確認してください。

---

## ステップ 2：データセットの記録（ローカル保存、ログイン不要）

```Bash
lerobot-record \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' \
  --teleop.type=so101_leader \
  --teleop.port=<leader-port> \
  --teleop.id=amazing_hand_leader \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --dataset.push_to_hub=false \
  --dataset.num_episodes=20 \
  --dataset.single_task="Pick up the cube with the dexterous hand" \
  --display_data=true
```

> `<follower_arm_port>` / `<hand_port>` / `<leader_arm_port>` を実際のパスに置き換えます；カメラの `index_or_path` をあなたのカメラインデックスに置き換えます。

> **💡 説明**：

- `--dataset.root=~/lerobot_data`：データセットは指定した**ローカルパス**に保存され、**HF ログインは不要**です（記述しない場合はデフォルトで `~/.cache/huggingface/lerobot/datasets/...` に保存されます）。

- `--dataset.push_to_hub=false`：**アップロードを無効化**します（デフォルトでは HF へのプッシュを試み、ログインが必要です）。データセットを共有する必要がある場合のみ `true` に変更します。

- `--dataset.repo_id=soarm_amazing_hand_pick`：データセット名です。訓練時は**同じ名前**で参照します。

- `--display_data=true` には rerun が必要（未インストールの場合は `pip install "rerun-sdk>=0.24.0,<0.34.0"`）かつグラフィカル環境が必要です。またはこの引数を外します（記録には影響しません）。

---

## パラメータ説明

|パラメータ|説明|
|---|---|
|`--robot.cameras`|カメラ設定。`index_or_path` はカメラインデックス、`width/height/fps` は**必須**|
|`--dataset.repo_id`|データセット名（ローカル識別用）|
|`--dataset.root`|データセットのローカル保存パス。**純粋なローカル記録では必ず追加**し、デフォルトパスが制御不能になるのを避ける|
|`--dataset.push_to_hub`|`false`=ローカルのみ（デフォルト推奨）；`true`=HF へプッシュ（ログインが必要）|
|`--dataset.num_episodes`|記録するエピソード数|
|`--dataset.episode_time_s`|**各エピソードの最長記録秒数**（デフォルト 60）。タスクが早く完了したら Enter で早期終了できます；超過すると自動的にそのエピソードを終了|
|`--dataset.single_task`|タスクの説明。データセットのメタデータに書き込まれる|
|`--display_data=true`|記録画面をリアルタイム表示（任意）|

---

## 記録操作の規範

**各エピソードの流れ**：

1. ロボットアーム \+ ハンドを**開始位置**に復帰させる

2. ターミナルで Enter を押して記録を開始

3. リーダーアームを操作してタスクを実行（例：ブロックをつかむ）。**動作はゆっくり、一貫して**

4. タスク完了後に Enter を押してこのエピソードを終了（**押さない場合は最大 60 秒記録**され、`--dataset.episode_time_s` で制御、時間になると自動終了）

5. `num_episodes` に達するまで繰り返す

> **⚠️ 注意 1（開始位置の一致）**：各エピソードは**同じ開始位置**から始め、データ分布の混乱を避けます。固定のリセット姿勢を決めることを推奨します。

> **⚠️ 注意 2（動作の一貫性）**：同じタスクでは類似した操作軌道（接近角度、把持位置、速度）を使うと、ポリシーがより速く安定して学習します。

> **⚠️ 注意 3（記録品質）**：質の低いものを多く記録するより、高品質なものを少なめに記録する方が良いです。20 エピソードは ACT の出発点で、複雑なタスクは 30\-50 エピソードを推奨します。

> **⚠️ 注意 4（カメラのリアルタイム性）**：記録時はカメラの遮蔽や強い光の変化を避けてください。画像の一貫性が汎化に影響します。

---

## データの保存

- **ローカル記録**：データは `--dataset.root` で指定したディレクトリに保存されます（例 `~/lerobot_data/soarm_amazing_hand_pick`）。

- **訓練での参照**：訓練時は**同じ ****`--dataset.repo_id`**** \+ ****`--dataset.root`** を使えばよく、手動でファイルを移動する必要はありません：

```Bash
lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=~/lerobot_data ...
```

- **HF ログインのシナリオ**（任意）：データセットをクラウドに共有する必要がある場合は、`--dataset.push_to_hub=true` に変更します（`huggingface-cli login` が必要）。ローカル訓練のみなら**不要**です。

> **⚠️ 注意（ローカル vs クラウド）**：デフォルトのチュートリアルは全工程ローカルで、`--dataset.push_to_hub=false` により HF ログインがトリガーされないことを保証します。データセットを共有したい場合のみ `true` を追加します。

---

## ステップ 3：再生による検証（任意だが推奨）

記録完了後、`lerobot-replay` で特定エピソードのデータを再生し、**データ品質 \+ ロボットの動作記録が正しいか**を検証できます。再生時はロボットがそのエピソードの動作（ハンドの開閉を含む）を自動的に再現します。

```Bash
lerobot-replay \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --dataset.episode=0
```

> `<follower_arm_port>` / `<hand_port>` を実際のパスに置き換えます；`--dataset.episode` は再生するエピソード番号です（**0 から開始**、例えば 20 エピソード記録した場合は `0`\~`19`）。

> **💡 説明**：再生前にフォロワーアーム \+ ハンドを**開始位置に戻し**、動作の衝突を避けます；再生中はロボットが自ら動くので、**手動で介入しないでください**。再生動作が記録時と明らかに異なる場合は、データ品質に問題があるため、そのエピソードを再記録することを推奨します。

---

本ステージを完了したら、ステージ5：モデル訓練 に進みます。

---

## トラブルシューティング

|現象|原因|解決|
|---|---|---|
|カメラが見つからない|インデックス誤り/権限/ドライバ欠如|`lerobot-find-cameras` で確認；`/dev/video*` の権限を確認（`video` グループに追加）|
|記録が中断される|シリアルポートのタイムアウト|3 台のデバイスのシリアルポートが占有されていないことを確認し、再試行|
|画像が真っ黒/乱れる|カメラ設定の誤り|`index_or_path`/`fps` を確認|
|`/dev/video*` に権限がない|ユーザーが video グループにいない|`sudo usermod -a -G video $USER` 後に再ログイン|
|データセットが空|正しく記録されていない|各エピソードで Enter を押して開始/終了しているか確認|

