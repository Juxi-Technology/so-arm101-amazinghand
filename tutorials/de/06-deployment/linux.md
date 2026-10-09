# linux

# Phase 6: Deployment und Evaluierung (Linux)

In dieser Phase laden Sie die trainierte Policy, lassen den Roboter Aufgaben **autonom ausführen** und zeichnen ein Auswertungsvideo auf, um die Wirkung zu überprüfen. Dies ist der Abschluss des gesamten Ablaufs und zugleich der entscheidende Test der Trainingsergebnisse.

---

## Voraussetzungen

- Phase 5: Modelltraining abgeschlossen

- Das Training hat `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/` erzeugt

- Die Kamera-Indizes sind notiert

---

## Schritt 1: Modelldateien bestätigen

```Bash
ls outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model
```

Es sollte Modelldateien wie `model.safetensors` enthalten.

> **⚠️ Hinweis (Modellpfad)**: `--policy.path` muss auf das Verzeichnis `pretrained_model` zeigen (enthält Konfiguration \+ Gewichte), nicht auf das Stammverzeichnis des checkpoint.

---

## Schritt 2: Deployment und Evaluierung

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
  --policy.path=outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model \
  --dataset.repo_id=soarm_amazing_hand_pick_eval \
  --dataset.root=~/lerobot_data \
  --dataset.push_to_hub=false \
  --dataset.num_episodes=10 \
  --dataset.single_task="Pick up the cube with the dexterous hand" \
  --display_data=true
```

> Ersetzen Sie `<follower_arm_port>` / `<hand_port>` durch die tatsächlichen Pfade; ersetzen Sie `index_or_path` der Kameras durch Ihre Kamera-Indizes.

> **💡 Erläuterung**: Verwenden Sie `lerobot-record`, aber **ohne ****`--teleop.type`**; die Policy steuert den Roboter dann autonom (anstelle manueller Teleoperation). Die Daten werden als Auswertungssatz gespeichert. `--dataset.root` / `--dataset.push_to_hub=false` stimmen mit Phase 4 überein; reine lokale Speicherung ohne HF-Anmeldung.

---

## Auswertungsschritte

1. Setzen Sie den Roboter \+ die Hand auf die **Startposition** zurück

2. Drücken Sie Enter zum Starten: Die Policy führt die Aufgabe autonom aus

3. Beobachten Sie, **ob erfolgreich gegriffen wurde** (drücken Sie am Ende jeder Episode Enter, um fortzufahren)

4. Wiederholen Sie dies für `num_episodes` Episoden

**Auswertungskennzahl**: Erfolgsrate = Anzahl erfolgreicher Episoden / Gesamtzahl der Episoden

> **⚠️ Hinweis 1 (Konsistenz des Resets)**: Beginnen Sie jede Episode von der **gleichen Startposition**, andernfalls schlägt die Generalisierung der Policy fehl und die Erfolgsrate fällt künstlich niedrig aus.

> **⚠️ Hinweis 2 (Sicherheit)**: Beim ersten autonomen Lauf empfiehlt es sich, **mit der Hand abzustützen / langsam** zu beobachten, um sicherzustellen, dass die Bewegungen der Policy sinnvoll sind. Die Policy kann unerwartete Bewegungen ausführen.

> **⚠️ Hinweis 3 (erwartete Erfolgsrate)**: ACT erreicht mit 20 Episoden Daten in der Regel eine Erfolgsrate von 50\-80%. Wenn sie niedriger als erwartet ausfällt, zeichnen Sie zusätzliche Daten auf oder passen Sie die Anzahl der Trainingsschritte an.

> **⚠️ Hinweis 4 (headless Umgebung)**: `--display_data=true` benötigt einen Anzeigeserver; in einer Umgebung ohne GUI entfernen Sie diesen Parameter (die Auswertung läuft weiterhin, nur ohne Echtzeitanzeige).

---

## Iterative Optimierung

Wenn die Auswertungs-Erfolgsrate nicht zufriedenstellend ist, passen Sie nach Priorität an:

|Priorität|Optimierungspunkt|Aktion|
|---|---|---|
|1|Hochwertige Daten nachträglich aufzeichnen|Zurück zu Phase 4, zeichnen Sie 20\-30 zusätzliche, konsistentere Episoden auf|
|2|Anzahl der Trainingsschritte erhöhen|Zurück zu Phase 5, `--steps=100000`|
|3|Konsistenz der Startposition prüfen|Setzen Sie bei der Auswertung jede Episode strikt zurück|
|4|Aufgabenbeschreibung anpassen|Stellen Sie sicher, dass `single_task` mit der Aufgabe übereinstimmt|

---

Damit ist der **vollständige Kreislauf** von SO\-ARM101 \+ AmazingHand abgeschlossen: Kalibrierung → Teleoperation → Erfassung → Training → Deployment.

---

## Fehlerbehebung

|Symptom|Ursache|Lösung|
|---|---|---|
|Laden des Modells fehlgeschlagen|Falscher/unvollständiger Pfad|Stellen Sie sicher, dass `--policy.path` auf das Verzeichnis `pretrained_model` zeigt|
|Policy bewegt sich nicht|Kamera/Beobachtung fehlerhaft|Stellen Sie sicher, dass die Kamera-Indizes mit denen beim Training übereinstimmen; prüfen Sie die Berechtigungen von `/dev/video*`|
|Policy bewegt sich unkontrolliert|Startposition inkonsistent / schlechte Daten|Strikt zurücksetzen; Daten nachträglich aufzeichnen|
|Verhalten weicht vom Training ab|Umgebungsunterschiede|Stellen Sie sicher, dass Kameras, Beleuchtung und Objektpositionen mit der Aufnahme übereinstimmen|

