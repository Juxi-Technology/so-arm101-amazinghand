# linux

# Phase 3: Teleoperation (Linux)

In dieser Phase starten Sie den geschlossenen Regelkreis der Teleoperation: Der Leader-Arm steuert die Bewegung des Follower-Arms, der Greifer steuert das Öffnen und Schließen des AmazingHand. Dies ist die entscheidende Phase, um zu überprüfen, ob das gesamte System ordnungsgemäß funktioniert.

---

## Voraussetzungen

- Phase 1: Umgebung einrichten und Phase 2: Kalibrierung abgeschlossen

- Berechtigungen für die serielle Schnittstelle konfiguriert

- Die drei Geräte sind eingeschaltet und die seriellen Schnittstellen wurden notiert

---

## Teleoperation ausführen

```Bash
lerobot-teleoperate \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --teleop.type=so101_leader \
  --teleop.port=<leader-port> \
  --teleop.id=amazing_hand_leader
```

> Ersetzen Sie `<follower_arm_port>` / `<hand_port>` / `<leader_arm_port>` durch die tatsächlichen Pfade Ihres Rechners (Beispiel `/dev/ttyACM0` / `/dev/ttyACM2` / `/dev/ttyACM1`).

**Erwartetes Ergebnis**:

- 5 Gelenke des Leader-Arms → Follower-Arm folgt

- Greifer des Leader-Arms → Öffnen/Schließen des AmazingHand (proportionale Nachführung: halb zusammengedrückt = halb geschlossen)

> **💡 Parameterbeschreibung**:

- `--robot.type=so101_amazing_hand`: kombinierter Roboter aus Follower-Arm \+ Hand

- `--robot.port`: serielle Schnittstelle des Follower-Arms

- `--robot.hand_port`: serielle Schnittstelle der Hand

- `--teleop.type=so101_leader`: Teleoperator des Leader-Arms

- `--teleop.port`: serielle Schnittstelle des Leader-Arms

---

## Bei der ersten Ausführung erforderlich: Richtungsüberprüfung

Führen Sie nach dem Start zuerst einen **Richtungstest** durch und bestätigen Sie, dass die folgenden beiden Punkte korrekt sind:

|Test|Aktion|Korrektes Verhalten|
|---|---|---|
|Arm folgt|Drehen Sie die einzelnen Gelenke des Leader-Arms|Der Follower-Arm folgt in derselben Richtung|
|Hand öffnet/schließt|Öffnen/Schließen des Greifers am Leader-Arm|Greifer öffnet → Hand öffnet; Greifer schließt → Hand schließt|

> **⚠️ Hinweis (was tun, wenn die Richtung umgekehrt ist)**:

- **Öffnungs-/Schließrichtung der Hand umgekehrt** (beim Öffnen des Greifers schließt sich die Hand): Dies deutet auf eine ungenaue Kalibrierung des Handwinkels hin. Führen Sie das Kalibrierungswerkzeug erneut aus (einschließlich der Kalibrierung der Greiferrichtung); nach dem Speichern wird es automatisch wirksam, **ohne dass Dateien manuell geändert werden müssen**. Siehe Phase 2: Kalibrierung.

- **Greiferzuordnungsrichtung umgekehrt** (beim Öffnen des Greifers schließt sich die Hand): Wie oben; klicken Sie bei der Kalibrierung auf `[Capture Open]`, wenn der Greifer des Leader-Arms **geöffnet** ist, und auf `[Capture Close]`, wenn er **geschlossen** ist; das Werkzeug zeichnet `gripper_open_pos`/`gripper_close_pos` automatisch auf, speichert sie und lädt sie beim Start automatisch.

> Führen Sie nach der Änderung **die Teleoperation erneut aus**, um sie zu überprüfen.

---

## Überprüfung der proportionalen Nachführung

Nachdem die Richtung korrekt ist, überprüfen Sie die Feinheit der Proportionalität:

1. Greifer **langsam** öffnen → die Hand sollte sich **gleichmäßig** öffnen (ohne Sprünge)

2. Greifer in der **Mitte** anhalten → die Hand sollte ebenfalls in der Mitte anhalten

3. Schnelles Öffnen/Schließen → die Hand reagiert schnell, ohne Stocken

> **⚠️ Hinweis (bekanntes Problem übermäßigen Öffnens/Schließens der Hand)**: Wenn sich die Hand bereits schließt, wenn der Greifer halb geöffnet ist, liegt meist eine ungenaue Position für „Öffnen/Faustbildung" bei der Kalibrierung des Handwinkels vor. Führen Sie Schritt 3 der Kalibrierung (GUI für den Handwinkel) erneut aus und kalibrieren Sie präzisere Öffnungs-/Schließpositionen.

---

## Optional: Visualisierung mit Kameras

Fügen Sie `--robot.cameras` hinzu, um Kameras anzubinden, und `--display_data=true`, um das Rerun-Visualisierungsfenster zu öffnen (zeigt Kamerabilder \+ Gelenkzustände in Echtzeit an):

```Bash
lerobot-teleoperate \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --teleop.type=so101_leader \
  --teleop.port=<leader-port> \
  --teleop.id=amazing_hand_leader \
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' \
  --display_data=true
```

> **💡 Erläuterung**:

- `index_or_path` ist der Kamera-Index; bestätigen Sie ihn zuerst mit `lerobot-find-cameras` (die Nummerierung ist je nach Rechner unterschiedlich).

- `fourcc: "MJPG"` ist optional und kann die Bandbreitennutzung von USB-Kameras erheblich senken (Umstellung auf MJPEG-Kompression); bei Ruckeln können Sie es hinzufügen.

- Wenn nur eine Kamera benötigt wird, löschen Sie einfach die entsprechende Zeile (z. B. `top`).

> **⚠️ Hinweis (rerun-Abhängigkeit und Anzeige)**: `--display_data=true` benötigt das rerun-Visualisierungspaket; wenn es nicht installiert ist, führen Sie aus:

```Bash
pip install "rerun-sdk>=0.24.0,<0.34.0"
```

> Außerdem benötigt das rerun-Fenster einen Anzeigeserver (lokale grafische Sitzung oder `ssh -X`). In einer Umgebung ohne Grafik **beeinträchtigt dies die Teleoperation nicht**; entfernen Sie einfach `--display_data=true`.

---

## Beenden

Drücken Sie `Ctrl+C` zum Stoppen. Das Programm führt automatisch Folgendes aus:

1. Aufheben des Drehmoments der 8 Handservos

2. Trennen der seriellen Schnittstellen von Follower-Arm/Leader-Arm

3. Trennen der Kameras (falls vorhanden)

> **⚠️ Hinweis**: **Schließen Sie das Terminal nicht direkt** vor einem ordnungsgemäßen Beenden (z. B. mit `kill -9`), da sonst eine Belegung der seriellen Schnittstelle zurückbleiben kann. Wenn die Schnittstelle nach einem abnormalen Beenden belegt ist, schließen Sie den zurückgebliebenen Prozess oder schließen Sie USB erneut an.

---

## Fehlerbehebung

|Symptom|Ursache|Lösung|
|---|---|---|
|Serielle Schnittstelle `Permission denied`|Berechtigungen nicht konfiguriert|`sudo chmod 666 /dev/ttyACM*`|
|Richtung der Hand umgekehrt|Handwinkel oder Greiferzuordnung umgekehrt|Siehe oben „Richtungsüberprüfung"|
|Hand öffnet/schließt zu stark/zu wenig|Handwinkel ungenau kalibriert|GUI für den Handwinkel neu kalibrieren|
|Arm folgt nicht|Kalibrierung fehlt / falsche Schnittstelle|Stellen Sie sicher, dass der Follower-Arm kalibriert und `--robot.port` korrekt ist|
|rerun meldet Fehler|Visualisierungsabhängigkeit/Anzeige fehlt|`--display_data=true` entfernen|
|Serielle Schnittstelle belegt|Abnormales Beenden beim letzten Mal|Zurückgebliebenen Prozess schließen oder USB erneut anschließen|

