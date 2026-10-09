# README

# SO\-ARM101 \+ AmazingHand Tutorial

Dieses Tutorial dient der Reproduktion des gesamten Ablaufs aus Teleoperation, Datenerfassung und Training für den **SO\-ARM101 Follower-Arm \+ die AmazingHand-Dexterous-Hand** und basiert auf LeRobot (angepasste Version des offiziellen Repositorys).

Das Tutorial ist nach **Phasen** gegliedert; jede Phase bildet ein eigenes Verzeichnis und ist intern nach Betriebssystem in die beiden Dokumente `win.md` (Windows) und `linux.md` (Linux) aufgeteilt. Bitte wählen Sie das zu Ihrem Betriebssystem passende Dokument zum Lesen.

---

## Hardware- und Softwareübersicht

|Gerät|Serielle Schnittstelle (Beispiel, muss ersetzt werden)|Servo-Modell|Beschreibung|
|---|---|---|---|
|Leader-Arm (Leader)|`COM54` / `/dev/ttyACM1`|gemischte Modelle<br>`sts3125-C001、sts3215-C044、sts3215-C046`|Teleoperationseingabe, Greifer Nr. 6 bleibt erhalten|
|Follower-Arm (Follower)|`COM58` / `/dev/ttyACM0`|`sts3215-C018` (Nr. 1\-5)|Ausführende Seite, Greifer Nr. 6 wurde entfernt|
|AmazingHand Dexterous-Hand|`COM11` / `/dev/ttyACM2`|`scs0009` (8 Stück, ID 1\-8)|Am Ende des Follower-Arms, eigene serielle Schnittstelle|

> **⚠️ Die Namen der seriellen Schnittstellen sind je nach Rechner unterschiedlich**: Die obige Tabelle ist ein Beispiel. Die COM-Nummern/Gerätepfade sind auf jedem Computer unterschiedlich; bestätigen Sie unbedingt mit `lerobot-find-port` die tatsächlichen Werte Ihres Rechners und ersetzen Sie alle Platzhalterparameter in den Befehlen.

> Die drei Geräte benötigen **jeweils eine eigene serielle Schnittstelle und eigene Stromversorgung**. SCS0009 (Protokoll 1) und STS3215 (Protokoll 0) sind nicht mit demselben Bus kompatibel.

---

## Verzeichnisstruktur des Tutorials

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

## Empfohlener Lesepfad

|Schritt|Phase|Windows|Linux|
|---|---|---|---|
|1|Umgebung einrichten|01\-environment/win\.md|01\-environment/linux\.md|
|2|Kalibrierung|02\-calibration/win\.md|02\-calibration/linux\.md|
|3|Teleoperation|03\-teleoperation/win\.md|03\-teleoperation/linux\.md|
|4|Datenerfassung|04\-data\-collection/win\.md|04\-data\-collection/linux\.md|
|5|Modelltraining|05\-training/win\.md|05\-training/linux\.md|
|6|Deployment und Evaluierung|06\-deployment/win\.md|06\-deployment/linux\.md|

---

## Kurzübersicht der wichtigsten Unterschiede je Phase

|Aspekt|Windows|Linux|
|---|---|---|
|Python-Umgebung|Miniconda \+ `conda create -n lerobot python=3.12`|Miniforge \+ derselbe Befehl|
|Name der seriellen Schnittstelle|`COM54` / `COM58` / `COM11` (Beispiel)|`/dev/ttyACM0/1/2` (Beispiel)|
|Berechtigungen der seriellen Schnittstelle|Keine besondere Konfiguration erforderlich|`sudo chmod 666 /dev/ttyACM*` oder udev-Regel erforderlich|
|Befehlsaufruf|Nach Aktivierung von conda `lerobot-xxx`|Nach Aktivierung von conda `lerobot-xxx`|
|CUDA-Training|CUDA-torch muss manuell installiert werden|Offiziell unterstützt, reibungslose Auflösung|

---

## Allgemeine Hinweise

1. **Schließen Sie zuerst Phase 1 ab, bevor Sie zu den weiteren Phasen übergehen** – die Umgebung ist die Voraussetzung für alle nachfolgenden Befehle.

2. **Auf jedem Computer muss neu kalibriert werden**: insbesondere der Handwinkel (`lerobot-calibrate-amazing-hand`). Die Winkel in der config sind die offiziellen allgemeinen Standardwerte von AmazingHand und dienen nur als Rückfalllösung; wenn `hand_angles.json` vorhanden ist, werden vorrangig die auf diesem Rechner gemessenen Werte geladen.

3. **Speicherort der Kalibrierungsdateien**: `~/.cache/huggingface/lerobot/calibration/`; bei einem Rechnerwechsel müssen sie übertragen oder neu kalibriert werden.

4. **Überprüfen Sie bei der ersten Teleoperation unbedingt die Richtung**: Greifer öffnet ↔ Hand öffnet, Greifer schließt ↔ Hand schließt.

5. In `win.md` / `linux.md` jeder Phase sind **plattformspezifische Hinweise** enthalten; bitte lesen Sie sie vollständig.

---

## Einstieg in die Fehlerbehebung

In den Phasendokumenten ist jeweils eine Fehlerbehebungstabelle für die einzelne Plattform enthalten. Häufige Probleme:

- conda ist nicht initialisiert / Befehl wird nicht gefunden

- Unzureichende Berechtigungen für die serielle Schnittstelle (Linux)

- Fehlerhafte Richtungszuordnung von Hand/Arm

- Nicht kalibrierter Handwinkel führt zu fehlerhaftem Öffnen/Schließen

Weitere Details finden Sie in den Dokumenten der jeweiligen Phasen.

