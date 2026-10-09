# linux

# ステージ1：環境構築（Linux）

**Miniforge** を使用して独立した Python 環境を作成し、LeRobot および AmazingHand サポートをインストールします。本ページは**厳密な順序**で実行します。各コードブロックはそのままコピーできます。

> 環境バージョン：Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2（本リポジトリのカスタム版）· 推奨 Ubuntu 20\.04/22\.04

---

## ステップ 1：Miniforge のインストール

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

> 公式アドレス（海外ネットワーク）：`https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh`

---

## ステップ 2：conda の国内ミラーを設定（中国本土ネットワーク）

```Bash
conda config --remove-key channels
```

```Bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` は提供終了（404）のため、追加しないでください。ネットワーク制限がない場合はこのステップを省略できます。

---

## ステップ 3：コンパイルツールのインストール（新しいシステムでは必須）

新規インストールした Ubuntu では `gcc` などのコンパイルツールが欠けている場合があり、`evdev` などのパッケージをインストールする際に必要です：

```Bash
sudo apt update
sudo apt install -y build-essential
```

---

## ステップ 4：仮想環境の作成

```Bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```Bash
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> 期待されるのは `Python 3.12.x` \+ `64 bit` です。

---

## ステップ 5：ffmpeg のインストール（動画デコードに必須）

LeRobot の動画データの記録/再生は ffmpeg に依存します：

```Bash
conda install ffmpeg -c conda-forge -y
```

---

## ステップ 6：プロジェクト依存関係のインストール

```Bash
cd ~/lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` に含まれるもの：`feetech-servo-sdk`（アームモーター）、`rustypot`（ハンドモーター）、`pygame`（キャリブレーション GUI）、`pyserial`（シリアルポート）。

> pip が遅い場合は先に国内ミラーを設定します：

```Bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## ステップ 7：シリアルポート権限の設定

```Bash
sudo chmod 666 /dev/ttyACM*
```

> 恒久対策（udev ルール、CP210x チップ向け、VID `10c4`）：

```Bash
sudo tee /etc/udev/rules.d/99-servo.rules << 'EOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## ステップ 8：環境の検証

```Bash
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> `all OK` と `usage: lerobot-calibrate-amazing-hand ...` が表示されるはずです。

---

## ステップ 9：シリアルポートの確認

```Bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

または `lerobot-find-port`。3 台のデバイスパスを確認します（例 `/dev/ttyACM0`/`/dev/ttyACM1`/`/dev/ttyACM2`、**実際の値に置き換えてください**）。

---

完了 → ステージ2：キャリブレーション

---

## トラブルシューティング

|現象|解決|
|---|---|
|`conda` コマンドが見つからない|`source ~/.bashrc` または `conda init` 後にターミナルを開き直す|
|`pkgs/free` 404|このチャンネルは提供終了のため、追加しない|
|シリアルポート `Permission denied`|ステップ 7 `sudo chmod 666`|
|依存関係がインストールできない/遅い|pip の国内ミラーを設定（ステップ 6 のヒント）|
|インストール時に `evdev` のコンパイルエラー|ステップ 3 `sudo apt install build-essential`|
|GPU 訓練の CUDA チェックが `False`|ステージ5 の訓練ドキュメントを参照|

