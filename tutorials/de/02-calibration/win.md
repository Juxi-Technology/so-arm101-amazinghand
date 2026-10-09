# win

# Phase 2: Kalibrierung (Windows)

In dieser Phase werden drei Geräte kalibriert: Leader-Arm, Follower-Arm und AmazingHand-Hand. Die Kalibrierung ist die Voraussetzung für die korrekte Teleoperation; **Sie müssen diese Phase abschließen, bevor Sie mit der Teleoperation beginnen können**.

> **Kalibrierungsreihenfolge**: Leader-Arm → Follower-Arm\+Hand → Handwinkel. Jeder Schritt erfordert eine **Terminal-Interaktion** (physische Bedienung \+ Tastendruck).

> **⚠️ Allgemeiner Hinweis**: Die Parameter für die serielle Schnittstelle in den Befehlen auf dieser Seite sind **Beispielplatzhalter** und müssen durch die tatsächlichen COM-Nummern Ihres Rechners ersetzt werden (siehe die in Phase 1 notierten Schnittstellen).

---

## Voraussetzungen

- Phase 1: Umgebung einrichten abgeschlossen

- conda-Umgebung `lerobot` ist aktiviert

```Plain Text
# Umgebung aktivieren
conda activate lerobot

# In lerobot wechseln
cd ../lerobot
```

- Die seriellen Schnittstellen der drei Geräte sind notiert

- Die Geräte sind eingeschaltet und werden unabhängig mit Strom versorgt

---

## Schritt 1: Leader-Arm kalibrieren

```PowerShell
lerobot-calibrate --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Ersetzen Sie `<leader_arm_com>` durch die tatsächliche COM-Nummer Ihres Rechners (Beispiel `COM54`).

**Interaktionsschritte**:

1. Bringen Sie den Leader-Arm in die **Mittelstellung aller Gelenke** und drücken Sie Enter

2. Bewegen Sie **jedes Gelenk nacheinander bis an den maximalen/minimalen Anschlag** und drücken Sie danach Enter

**Überprüfung**: Die Kalibrierungsdatei wird automatisch gespeichert unter
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\teleoperators\so_leader\amazing_hand_leader.json`

> **⚠️ Hinweis 1 (Greifer muss kalibriert werden)**: Der Bereich des Greifer-Servos Nr. 6 dient als Normalisierungsbasis für `gripper.pos` (0\~100). Der Greifer muss unbedingt von vollständig geöffnet bis vollständig geschlossen durchgefahren und korrekt kalibriert werden, andernfalls verfälscht sich anschließend das Öffnungs-/Schließverhältnis der Hand.

> **⚠️ Hinweis 2 (freie Drehung)**: Während der Kalibrierung muss sich der Roboterarm frei drehen können; stellen Sie sicher, dass die Servos unbelastet sind.

> **⚠️ Hinweis 3 (Speicherort der Kalibrierungsdatei)**: Unter Windows ist der Pfad das Benutzerverzeichnis `%USERPROFILE%\.cache\huggingface\lerobot\calibration\`.

---

## Schritt 2: Follower-Arm kalibrieren (gleichzeitig die Hand verbinden)

```PowerShell
lerobot-calibrate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower
```

> Ersetzen Sie `<follower_arm_com>` / `<hand_com>` durch die tatsächlichen COM-Nummern (Beispiel `COM58` / `COM11`).

**Interaktionsschritte**:

1. Bringen Sie den Follower-Arm mit **5 Gelenken** (ohne Nr. 6) in die Mittelstellung und drücken Sie Enter

2. Fahren Sie alle Gelenke über den vollen Weg und drücken Sie Enter

**Überprüfung**: Die Kalibrierungsdatei wird gespeichert unter
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\amazing_hand_follower.json`

> **⚠️ Hinweis 1 (Handdrehmoment wird automatisch aktiviert)**: Dieser Befehl **aktiviert beim Verbinden automatisch das Drehmoment der 8 Handservos** (das Protokoll zeigt `enabling AmazingHand torque`); dass die Hand nach Abschluss der Kalibrierung geöffnet wird, ist normal.

> **⚠️ Hinweis 2 (keine Hand-GUI)**: Für den Handwinkel wird die `RangeFinderGUI` von lerobot **nicht verwendet**; mit dem Ende der Follower-Arm-Kalibrierung ist dies abgeschlossen. Für den Handwinkel verwenden Sie das spezielle Werkzeug aus Schritt 3.

> **⚠️ Hinweis 3 (Belegung der seriellen Schnittstelle)**: Dieser Schritt belegt die serielle Schnittstelle der Hand. Führen Sie **nicht** gleichzeitig andere Prozesse aus, die diese Schnittstelle belegen.

---

## Schritt 3: Handwinkel \+ Greiferrichtung kalibrieren (spezielle GUI)

```PowerShell
lerobot-calibrate-amazing-hand --hand_port <hand-port> --leader_port <leader-port>
```

> Ersetzen Sie `<hand_com>` / `<leader_arm_com>` durch die tatsächlichen COM-Nummern (Beispiel `COM11` / `COM54`). `--leader_port` dient zur gleichzeitigen Kalibrierung der **Greiferrichtung** (siehe unten).

**GUI-Bedienung**:

1. Ziehen Sie die Schieberegler der 4 Finger (index/middle/ring/thumb), sodass die Hand **vollständig geöffnet** ist, und klicken Sie auf **`Save Open`**

2. Ziehen Sie die Schieberegler, sodass die Hand **vollständig zur Faust geballt** ist, und klicken Sie auf **`Save Close`**

3. **Öffnen Sie den Greifer des Leader-Arms** und klicken Sie auf **`Capture Open`** (die GUI zeigt `gripper.pos` in Echtzeit an; beim Öffnen sollte der Wert nahe 100 liegen)

4. **Schließen Sie den Greifer des Leader-Arms** und klicken Sie auf **`Capture Close`** (beim Schließen sollte der Wert nahe 0 liegen)

5. **Automatisches Speichern**: Nachdem alle vier obigen Werte festgelegt wurden, erscheint oben im Fenster ein grünes Banner `AUTO-SAVED to ...\hand_angles.json`, und das Terminal gibt den Pfad synchron aus

6. Schließen Sie das Fenster (das Drehmoment der Hand wird automatisch aufgehoben)

**Überprüfung**: Winkel und Greiferzuordnung werden gespeichert unter
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\hand_angles.json`

> **⚠️ Hinweis 1 (Kalibrierung erforderlich)**: **Dieser Schritt muss auf jedem neuen Computer / für jede neue Hand ausgeführt werden**. Die Winkel in der config sind die offiziellen allgemeinen Standardwerte von AmazingHand und dienen nur als Rückfalllösung; wenn `hand_angles.json` vorhanden ist, werden vorrangig Ihre gemessenen Werte geladen. Ohne Kalibrierung können Fehler bei Öffnungs-/Schließrichtung bzw. -bereich auftreten.

> **⚠️ Hinweis 2 (automatisches Laden)**: Der Roboter liest bei jedem Start `hand_angles.json` (enthält `gripper_open_pos`/`gripper_close_pos`) und überschreibt damit die Standardwerte der config; **es ist keine Codeänderung erforderlich**. Die Greiferrichtung kann je nach Leader-Arm variieren; eine einmalige Kalibrierung genügt.

> **⚠️ Hinweis 3 (Semantik der Schieberegler)**: Ein Schieberegler in Richtung `+` bewegt m1 des Fingers in Richtung `+angle` und m2 in Richtung `-angle` (gespiegelt). Beurteilen Sie Öffnen/Faustbildung anhand der **tatsächlichen Haltung der Hand** und achten Sie nicht auf die Winkelwerte.

> **⚠️ Hinweis 4 (präzise Kalibrierung)**: Überziehen Sie die Kalibrierung von „vollständig geöffnet" nicht (Finger nicht verkippen/spreizen) und drücken Sie bei „vollständig zur Faust geballt" nicht zu stark (Servos nicht dauerhaft belasten). Andernfalls fällt das Öffnen/Schließen bei der Teleoperation zu stark aus.

> **⚠️ Hinweis 5 (Reihenfolge von Capture)**: `Capture Open` / `Capture Close` entsprechen dem Öffnen/Schließen des **Greifers am Leader-Arm**, nicht der Finger der Hand. Wenn die Öffnungsrichtung der Hand umgekehrt ist, wurde hier oder beim Handwinkel höchstwahrscheinlich falsch kalibriert; kalibrieren Sie einfach neu.

> **⚠️ Hinweis 6 (GUI lässt sich nicht öffnen)**: Stellen Sie sicher, dass `pygame` installiert ist (im `amazinghand`-extra enthalten). Wenn sie sich weiterhin nicht öffnen lässt, prüfen Sie, ob eine grafische Desktop-Umgebung vorhanden ist.

---

## Neukalibrierung

Wenn nur ein bestimmter Teil neu kalibriert werden muss:

- **Nur die Hand neu kalibrieren** → nur Schritt 3 ausführen

- **Nur den Follower-Arm neu kalibrieren** → nur Schritt 2 ausführen (aktiviert dabei das Handdrehmoment)

- **Alles neu kalibrieren** → Schritt 1 → 2 → 3

> **⚠️ Hinweis**: Schritt 2 und Schritt 3 **können nicht gleichzeitig ausgeführt werden** (beide belegen die serielle Schnittstelle der Hand).

---

Nach Abschluss dieser Phase fahren Sie mit Phase 3: Teleoperation fort.

---

## Fehlerbehebung

|Symptom|Ursache|Lösung|
|---|---|---|
|Leader-Arm-Kalibrierung meldet Modellfehler 2307|Armbus verunreinigt / Schnittstellenkonflikt<br>|Stellen Sie sicher, dass die Schnittstelle der Hand nicht gleichzeitig verbunden ist; in diesem Projekt läuft die Hand über rustypot und umgeht dies|
|Bei der Handkalibrierung erscheint keine GUI|Falscher Befehl verwendet|Verwenden Sie unbedingt `lerobot-calibrate-amazing-hand` (nicht `lerobot-calibrate`)|
|Handtreiber meldet `Operation timed out`|Schnittstelle belegt / Timing|Stellen Sie sicher, dass die Schnittstelle der Hand nicht belegt ist, und versuchen Sie es erneut|
|Kalibrierungsdatei nicht gefunden|Falscher Pfad<br>|Prüfen Sie `%USERPROFILE%\.cache\huggingface\lerobot\calibration\`|
|Serielle Schnittstelle lässt sich nicht öffnen|Falsche COM-Nummer|Mit `lerobot-find-port` erneut bestätigen|

