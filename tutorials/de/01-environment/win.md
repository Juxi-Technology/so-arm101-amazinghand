# win

# Phase 1: Umgebung einrichten (Windows)

Verwenden Sie **Miniconda**, um eine eigenständige Python-Umgebung zu erstellen und LeRobot sowie die AmazingHand-Unterstützung zu installieren. Führen Sie die Schritte auf dieser Seite in **strikter Reihenfolge** aus; jeder Codeblock kann als Ganzes kopiert werden.

> Umgebungsversionen: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (angepasste Version dieses Repositorys)

---

## Schritt 1: Miniconda installieren

**Kommandozeileninstallation** (PowerShell, empfohlen) — verwenden Sie für Netzwerke in Festlandchina den Tsinghua-Spiegel:

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

Nach dem Neustart von PowerShell überprüfen:

```PowerShell
conda --version
```

> **Grafische Installation** (optional): Laden Sie das Installationspaket von der offiziellen Website https://repo\.anaconda\.com/miniconda/Miniconda3\-latest\-Windows\-x86\_64\.exe herunter, installieren Sie es per Doppelklick und aktivieren Sie **"Add to PATH"**.

> Wenn der Befehl `conda` nicht gefunden wird, verwenden Sie **Anaconda Prompt** (Startmenü) anstelle von PowerShell.

---

## Schritt 2: conda-Spiegel für China konfigurieren (Netzwerk in Festlandchina)

**Zuerst die Standardquellen leeren, dann den Tsinghua-Spiegel hinzufügen** (ein neues Miniconda enthält standardmäßig die offizielle Quelle `repo.anaconda.com`, was eine ToS-Prüfung auslöst und langsam ist):

```PowerShell
conda config --remove-key channels
```

```PowerShell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` ist abgeschaltet (404); nicht hinzufügen. Bei unbegrenztem Netzwerk können Sie diesen Schritt überspringen.

---

## Schritt 3: Virtuelle Umgebung erstellen

```PowerShell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```PowerShell
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Erwartet: `Python 3.12.x` \+ `64 bit`. Wenn `conda activate` kein Präfix `(lerobot)` anzeigt, siehe Fehlerbehebung am Ende.

---

## Schritt 4: ffmpeg installieren (für Videodekodierung erforderlich)

LeRobot benötigt ffmpeg zum Aufnehmen/Wiedergeben von Videodaten:

```PowerShell
conda install ffmpeg -c conda-forge -y
```

> Wenn das Netzwerk in China langsam ist, können Sie den bereits konfigurierten Tsinghua-conda\-forge-Kanal verwenden. Ohne Installation treten Fehler beim Aufnehmen von Daten/Abspielen von Videos auf.

---

## Schritt 5: Projektabhängigkeiten installieren

```PowerShell
cd D:\Project\lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` enthält: `feetech-servo-sdk` (Armmotoren), `rustypot` (Handmotoren), `pygame` (Kalibrierungs-GUI), `pyserial` (serielle Schnittstelle).

> Wenn pip langsam ist, konfigurieren Sie zuerst eine Quelle in China:

```PowerShell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Schritt 6: Umgebung überprüfen

```PowerShell
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> Es sollte `all OK` und `usage: lerobot-calibrate-amazing-hand ...` angezeigt werden.

---

## Schritt 7: Serielle Schnittstelle bestätigen

```PowerShell
lerobot-find-port
```

Bestätigen Sie im Geräte-Manager → Anschlüsse \(COM und LPT\) die COM-Nummern der drei Geräte (Beispiel `COM54`/`COM58`/`COM11`, **muss durch Ihre tatsächlichen Werte ersetzt werden**). Die COM-Nummern ändern sich nach dem Ein- und Ausstecken; führen Sie die Bestätigung erneut aus.

---

Fertig → Phase 2: Kalibrierung

---

## Fehlerbehebung

|Symptom|Lösung|
|---|---|
|`conda` ist kein Befehl|Terminal neu öffnen / Anaconda Prompt / `conda init powershell`|
|ToS-Fehler (repo\.anaconda\.com)|In Schritt 2 die channels leeren und nur die Tsinghua-Quelle behalten; oder `conda tos accept ...`|
|`pkgs/free` 404|Dieser Kanal ist abgeschaltet; nicht hinzufügen|
|`conda activate` ohne Präfix|Problem mit der Ausführungsrichtlinie, siehe unten|
|Abhängigkeiten lassen sich nicht installieren / sind langsam|pip-Quelle in China konfigurieren (Hinweis in Schritt 5)|

**conda activate zeigt kein Präfix ****`(lerobot)`**** an** (unter Windows häufig):

```PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "D:\Software\Miniconda3\shell\condabin\conda-hook.ps1"
conda activate lerobot
```

> Ersetzen Sie `D:\Software\Miniconda3` durch Ihren Miniconda-Installationspfad.

