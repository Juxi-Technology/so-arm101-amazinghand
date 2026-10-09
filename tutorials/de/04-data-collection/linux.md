# linux

# Phase 4: Datenerfassung (Linux)

In dieser Phase zeichnen Sie einen Teleoperations-Datensatz auf: Unter manueller Steuerung werden Proben aus „Gelenkwinkel \+ Kamerabild" erfasst, die dem späteren Training dienen. Die Qualität des Datensatzes bestimmt direkt die Wirkung der Policy; **die Bedienung muss standardisiert und konsistent sein**. In dieser Phase **wird durchgängig lokal aufgezeichnet, ohne HF-Anmeldung**.

---

## Voraussetzungen

- Phase 3: Teleoperation abgeschlossen und die Richtung als korrekt überprüft

- Kameras sind angeschlossen und die Indizes notiert (`lerobot-find-cameras`)

- Der lokale Speicherpfad für den Datensatz ist festgelegt (in diesem Dokument als Beispiel `~/lerobot_data`; anpassbar)

---

## Schritt 1: Kamera-Indizes bestätigen

```Bash
lerobot-find-cameras
```

Notieren Sie die Kameranummern. Zum Beispiel:

- Nr. 0: Handgelenkkamera (wrist)

- Nr. 1: Kamera oben (top)

> **⚠️ Hinweis (Kamera-Index)**: `index_or_path` ist der Kamera-Index (0/1/2\.\.\.) oder der Pfad eines Videostreams. Die Nummerierung ist je nach Rechner unterschiedlich; bestätigen Sie sie unbedingt zuerst.

---

## Schritt 2: Datensatz aufzeichnen (lokal speichern, keine Anmeldung erforderlich)

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

> Ersetzen Sie `<follower_arm_port>` / `<hand_port>` / `<leader_arm_port>` durch die tatsächlichen Pfade; ersetzen Sie `index_or_path` der Kameras durch Ihre Kamera-Indizes.

> **💡 Erläuterung**:

- `--dataset.root=~/lerobot_data`: Der Datensatz wird unter dem angegebenen **lokalen Pfad** gespeichert, **ohne HF-Anmeldung** (ohne diese Angabe wird standardmäßig unter `~/.cache/huggingface/lerobot/datasets/...` gespeichert).

- `--dataset.push_to_hub=false`: **Upload deaktiviert** (standardmäßig wird ein Push zu HF versucht, was eine Anmeldung erfordert). Setzen Sie es nur dann auf `true`, wenn Sie den Datensatz teilen möchten.

- `--dataset.repo_id=soarm_amazing_hand_pick`: Name des Datensatzes; verwenden Sie beim Training **denselben Namen** zur Referenzierung.

- `--display_data=true` benötigt rerun (falls nicht installiert: `pip install "rerun-sdk>=0.24.0,<0.34.0"`) und eine grafische Umgebung; alternativ entfernen Sie diesen Parameter (die Aufnahme wird nicht beeinträchtigt).

---

## Parameterbeschreibung

|Parameter|Beschreibung|
|---|---|
|`--robot.cameras`|Kamerakonfiguration. `index_or_path` ist der Kamera-Index; `width/height/fps` sind **erforderlich**|
|`--dataset.repo_id`|Name des Datensatzes (zur lokalen Identifikation)|
|`--dataset.root`|Lokaler Speicherpfad des Datensatzes. **Bei reiner lokaler Aufnahme unbedingt angeben**, um einen unkontrollierbaren Standardpfad zu vermeiden|
|`--dataset.push_to_hub`|`false`=nur lokal (standardmäßig empfohlen); `true`=Push zu HF (Anmeldung erforderlich)|
|`--dataset.num_episodes`|Anzahl der aufzuzeichnenden Episoden|
|`--dataset.episode_time_s`|**Maximale Sekundenzahl pro Episode** (Standard 60). Bei vorzeitigem Abschluss der Aufgabe können Sie mit Enter früher beenden; bei Überschreitung wird die Episode automatisch beendet|
|`--dataset.single_task`|Aufgabenbeschreibung, wird in die Metadaten des Datensatzes geschrieben|
|`--display_data=true`|Zeigt das Aufnahmebild in Echtzeit an (optional)|

---

## Richtlinien für die Aufnahme

**Ablauf pro Episode**:

1. Setzen Sie den Roboterarm \+ die Hand auf die **Startposition** zurück

2. Drücken Sie im Terminal Enter, um die Aufnahme zu starten

3. Führen Sie die Aufgabe mit dem Leader-Arm aus (z. B. einen Würfel greifen); **die Bewegungen müssen langsam und konsistent sein**

4. Drücken Sie nach Abschluss der Aufgabe Enter, um die Episode zu beenden (**ohne Tastendruck wird höchstens 60 Sekunden aufgezeichnet**, gesteuert durch `--dataset.episode_time_s`; nach Ablauf endet sie automatisch)

5. Wiederholen Sie dies, bis `num_episodes` erreicht ist

> **⚠️ Hinweis 1 (gleiche Startposition)**: Beginnen Sie jede Episode von der **gleichen Startposition**, um eine uneinheitliche Datenverteilung zu vermeiden. Es empfiehlt sich, eine feste Reset-Haltung zu verwenden.

> **⚠️ Hinweis 2 (Konsistenz der Bewegungen)**: Verwenden Sie für dieselbe Aufgabe ähnliche Bewegungsbahnen (Annäherungswinkel, Greifposition, Geschwindigkeit); die Policy lernt so schneller und stabiler.

> **⚠️ Hinweis 3 (Aufnahmequalität)**: Zeichnen Sie lieber wenige Episoden mit hoher Qualität auf als viele ungeordnete Proben. 20 Episoden sind der Ausgangspunkt für ACT; für komplexe Aufgaben werden 30\-50 Episoden empfohlen.

> **⚠️ Hinweis 4 (Echtzeitfähigkeit der Kamera)**: Vermeiden Sie beim Aufzeichnen Verdeckungen der Kamera und starke Lichtänderungen; die Konsistenz der Bilder beeinflusst die Generalisierung.

---

## Datenspeicherung

- **Lokale Aufnahme**: Die Daten werden im durch `--dataset.root` angegebenen Verzeichnis gespeichert (Beispiel `~/lerobot_data/soarm_amazing_hand_pick`).

- **Trainingsreferenz**: Verwenden Sie beim Training **denselben ****`--dataset.repo_id`**** \+ ****`--dataset.root`**, Dateien müssen nicht manuell verschoben werden:

```Bash
lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=~/lerobot_data ...
```

- **Szenario mit HF-Anmeldung** (optional): Wenn Sie den Datensatz in die Cloud teilen möchten, ändern Sie es zu `--dataset.push_to_hub=true` (erfordert `huggingface-cli login`). Für reines lokales Training **nicht erforderlich**.

> **⚠️ Hinweis (lokal vs. Cloud)**: Standardmäßig ist das Tutorial durchgängig lokal; `--dataset.push_to_hub=false` stellt sicher, dass keine HF-Anmeldung ausgelöst wird. Setzen Sie `true` nur, wenn Sie den Datensatz teilen möchten.

---

## Schritt 3: Wiedergabeüberprüfung (optional, aber empfohlen)

Nach Abschluss der Aufnahme können Sie mit `lerobot-replay` eine Episode wiedergeben, um **die Datenqualität \+ die korrekte Aufzeichnung der Roboterbewegungen** zu überprüfen. Bei der Wiedergabe spielt der Roboter die Bewegungen dieser Episode automatisch nach (einschließlich Öffnen/Schließen der Hand).

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

> Ersetzen Sie `<follower_arm_port>` / `<hand_port>` durch die tatsächlichen Pfade; `--dataset.episode` ist die Nummer der wiederzugebenden Episode (**beginnend bei 0**; bei 20 aufgezeichneten Episoden also `0`\~`19`).

> **💡 Erläuterung**: Bringen Sie vor der Wiedergabe den Follower-Arm \+ die Hand **zurück in die Startposition**, um Bewegungskonflikte zu vermeiden; während der Wiedergabe bewegt sich der Roboter von selbst, **greifen Sie nicht manuell ein**. Wenn die wiedergegebenen Bewegungen deutlich von der Aufnahme abweichen, weist dies auf eine mangelnde Datenqualität hin; es wird empfohlen, die Episode neu aufzuzeichnen.

---

Nach Abschluss dieser Phase fahren Sie mit Phase 5: Modelltraining fort.

---

## Fehlerbehebung

|Symptom|Ursache|Lösung|
|---|---|---|
|Kamera nicht gefunden|Falscher Index / Berechtigungen / fehlender Treiber|Mit `lerobot-find-cameras` bestätigen; Berechtigungen von `/dev/video*` prüfen (zur Gruppe `video` hinzufügen)|
|Aufnahme abgebrochen|Zeitüberschreitung der seriellen Schnittstelle|Stellen Sie sicher, dass die seriellen Schnittstellen der drei Geräte nicht belegt sind, und versuchen Sie es erneut|
|Bild vollständig schwarz/verzerrt|Falsche Kamerakonfiguration|`index_or_path`/`fps` prüfen|
|Keine Berechtigung für `/dev/video*`|Benutzer ist nicht in der Gruppe video|`sudo usermod -a -G video $USER`, danach neu anmelden|
|Datensatz ist leer|Nicht korrekt aufgezeichnet|Stellen Sie sicher, dass zu Beginn/Ende jeder Episode Enter gedrückt wird|

