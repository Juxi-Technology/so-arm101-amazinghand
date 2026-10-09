# win

# ステージ1：環境構築（Windows）

**Miniconda** を使用して独立した Python 環境を作成し、LeRobot および AmazingHand サポートをインストールします。本ページは**厳密な順序**で実行します。各コードブロックはそのままコピーできます。

> 環境バージョン：Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2（本リポジトリのカスタム版）

---

## ステップ 1：Miniconda のインストール

**コマンドラインインストール**（PowerShell、推奨）——中国本土ネットワークでは清華ミラーを使用：

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

PowerShell を開き直して検証：

```PowerShell
conda --version
```

> **GUI インストール**（任意）：公式サイト https://repo\.anaconda\.com/miniconda/Miniconda3\-latest\-Windows\-x86\_64\.exe からインストーラーをダウンロードし、ダブルクリックでインストール、**"Add to PATH"** にチェックを入れます。

> `conda` コマンドが見つからない場合は、**Anaconda Prompt**（スタートメニュー）を PowerShell の代わりに使用します。

---

## ステップ 2：conda の国内ミラーを設定（中国本土ネットワーク）

**まずデフォルトソースを空にしてから、清華ミラーを追加します**（新しい Miniconda はデフォルトで `repo.anaconda.com` 公式ソースを伴い、ToS チェックが発生して遅くなります）：

```PowerShell
conda config --remove-key channels
```

```PowerShell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` は提供終了（404）のため、追加しないでください。ネットワーク制限がない場合はこのステップを省略できます。

---

## ステップ 3：仮想環境の作成

```PowerShell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```PowerShell
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> 期待されるのは `Python 3.12.x` \+ `64 bit` です。`conda activate` に `(lerobot)` プレフィックスが付かない場合は、文末のトラブルシューティングを参照してください。

---

## ステップ 4：ffmpeg のインストール（動画デコードに必須）

LeRobot の動画データの記録/再生は ffmpeg に依存します：

```PowerShell
conda install ffmpeg -c conda-forge -y
```

> 国内ネットワークで遅い場合は、設定済みの清華 conda\-forge チャンネルを使用できます。インストールしないと、データ記録/動画再生でエラーが発生します。

---

## ステップ 5：プロジェクト依存関係のインストール

```PowerShell
cd D:\Project\lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` に含まれるもの：`feetech-servo-sdk`（アームモーター）、`rustypot`（ハンドモーター）、`pygame`（キャリブレーション GUI）、`pyserial`（シリアルポート）。

> pip が遅い場合は先に国内ミラーを設定します：

```PowerShell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## ステップ 6：環境の検証

```PowerShell
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> `all OK` と `usage: lerobot-calibrate-amazing-hand ...` が表示されるはずです。

---

## ステップ 7：シリアルポートの確認

```PowerShell
lerobot-find-port
```

デバイスマネージャー → ポート\(COM と LPT\) で 3 台のデバイスの COM 番号を確認します（例 `COM54`/`COM58`/`COM11`、**実際の値に置き換えてください**）。COM 番号は抜き差し後に変わるため、再実行して確認します。

---

完了 → ステージ2：キャリブレーション

---

## トラブルシューティング

|現象|解決|
|---|---|
|`conda` がコマンドではない|ターミナルを開き直す / Anaconda Prompt / `conda init powershell`|
|ToS エラー（repo\.anaconda\.com）|ステップ 2 で channels を空にして清華ソースのみ残す；または `conda tos accept ...`|
|`pkgs/free` 404|このチャンネルは提供終了のため、追加しない|
|`conda activate` にプレフィックスがない|実行ポリシーの問題、下記参照|
|依存関係がインストールできない/遅い|pip の国内ミラーを設定（ステップ 5 のヒント）|

**conda activate に ****`(lerobot)`**** プレフィックスがない**（Windows でよくある）：

```PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "D:\Software\Miniconda3\shell\condabin\conda-hook.ps1"
conda activate lerobot
```

> `D:\Software\Miniconda3` はあなたの Miniconda インストールパスに置き換えてください。

