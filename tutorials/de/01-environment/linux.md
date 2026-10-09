# linux

# Phase 1: Umgebung einrichten (Linux)

Verwenden Sie **Miniforge**, um eine eigenständige Python-Umgebung zu erstellen und LeRobot sowie die AmazingHand-Unterstützung zu installieren. Führen Sie die Schritte auf dieser Seite in **strikter Reihenfolge** aus; jeder Codeblock kann als Ganzes kopiert werden.

> Umgebungsversionen: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (angepasste Version dieses Repositorys) · empfohlen Ubuntu 20\.04/22\.04

---

## Schritt 1: Miniforge installieren

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

> Offizielle Adresse (Auslandsnetzwerk): `https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh`

---

## Schritt 2: conda-Spiegel für China konfigurieren (Netzwerk in Festlandchina)

```Bash
conda config --remove-key channels
```

```Bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` ist abgeschaltet (404); nicht hinzufügen. Bei unbegrenztem Netzwerk können Sie diesen Schritt überspringen.

---

## Schritt 3: Kompilierwerkzeuge installieren (bei neuen Systemen erforderlich)

Ein frisch installiertes Ubuntu kann Kompilierwerkzeuge wie `gcc` vermissen; diese werden für die Installation von Paketen wie `evdev` benötigt:

```Bash
sudo apt update
sudo apt install -y build-essential
```

---

## Schritt 4: Virtuelle Umgebung erstellen

```Bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```Bash
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Erwartet: `Python 3.12.x` \+ `64 bit`.

---

## Schritt 5: ffmpeg installieren (für Videodekodierung erforderlich)

LeRobot benötigt ffmpeg zum Aufnehmen/Wiedergeben von Videodaten:

```Bash
conda install ffmpeg -c conda-forge -y
```

---

## Schritt 6: Projektabhängigkeiten installieren

```Bash
cd ~/lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` enthält: `feetech-servo-sdk` (Armmotoren), `rustypot` (Handmotoren), `pygame` (Kalibrierungs-GUI), `pyserial` (serielle Schnittstelle).

> Wenn pip langsam ist, konfigurieren Sie zuerst eine Quelle in China:

```Bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Schritt 7: Berechtigungen für die serielle Schnittstelle konfigurieren

```Bash
sudo chmod 666 /dev/ttyACM*
```

> Dauerhafte Lösung (udev-Regel, für den CP210x-Chip, VID `10c4`):

```Bash
sudo tee /etc/udev/rules.d/99-servo.rules << 'EOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## Schritt 8: Umgebung überprüfen

```Bash
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> Es sollte `all OK` und `usage: lerobot-calibrate-amazing-hand ...` angezeigt werden.

---

## Schritt 9: Serielle Schnittstelle bestätigen

```Bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

Oder `lerobot-find-port`. Bestätigen Sie die Pfade der drei Geräte (Beispiel `/dev/ttyACM0`/`/dev/ttyACM1`/`/dev/ttyACM2`, **muss durch Ihre tatsächlichen Werte ersetzt werden**).

---

Fertig → Phase 2: Kalibrierung

---

## Fehlerbehebung

|Symptom|Lösung|
|---|---|
|`conda`-Befehl nicht gefunden|Nach `source ~/.bashrc` oder `conda init` das Terminal neu öffnen|
|`pkgs/free` 404|Dieser Kanal ist abgeschaltet; nicht hinzufügen|
|Serielle Schnittstelle `Permission denied`|Schritt 7 `sudo chmod 666`|
|Abhängigkeiten lassen sich nicht installieren / sind langsam|pip-Quelle in China konfigurieren (Hinweis in Schritt 6)|
|Installation meldet `evdev`-Kompilierfehler|Schritt 3 `sudo apt install build-essential`|
|CUDA-Prüfung beim GPU-Training `False`|Siehe Trainingsdokument in Phase 5|

