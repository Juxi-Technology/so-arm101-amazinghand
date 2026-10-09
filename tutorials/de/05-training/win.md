# win

# Phase 5: Modelltraining (Windows)

In dieser Phase trainieren Sie mit dem erfassten Datensatz eine Policy (z. B. ACT) und erzeugen ein einsetzbares Modell. Das Training ist der zeitaufwändigste Schritt; **es wird die Verwendung einer NVIDIA GPU empfohlen**.

---

## Voraussetzungen

- Phase 4: Datenerfassung abgeschlossen

- NVIDIA GPU (empfohlen), CUDA-Treiber

- Der Datensatz ist aufgezeichnet (im lokalen Cache sichtbar)

---

## Schritt 1: GPU-Umgebung bestätigen

```PowerShell
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**Erwartete Ausgabe**: `CUDA: True | GPU: <your_gpu_name>`

> **⚠️ Hinweis (CUDA-torch)**: Wenn `CUDA: False`, ist die CPU-Version von torch installiert. Die CUDA-Version muss neu installiert werden:

```PowerShell
# Offizielle Quelle (Auslandsnetzwerk)
pip install torch --index-url https://download.pytorch.org/whl/cu128

# Für Netzwerke in Festlandchina bevorzugt den Alibaba-Cloud-Mirror verwenden
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
```

> Oder trainieren Sie mit der CPU (`--policy.device=cpu`, aber deutlich langsamer und für komplexe Aufgaben unrealistisch).

---

## Schritt 2: Training

```PowerShell
lerobot-train `
  --dataset.repo_id=soarm_amazing_hand_pick `
  --dataset.root=D:\lerobot_data `
  --policy.type=act `
  --output_dir=outputs/train/soarm_amazing_hand_pick `
  --job_name=soarm_amazing_hand_pick `
  --policy.device=cuda `
  --wandb.enable=false `
  --policy.push_to_hub=false `
  --steps=60000
```

> **💡 Erläuterung**: `--dataset.repo_id` und `--dataset.root` müssen mit denen bei der Aufnahme in Phase 4 **vollständig übereinstimmen** (`repo_id=soarm_amazing_hand_pick`, `root=D:\lerobot_data`), damit der lokale Datensatz gelesen werden kann, ohne HF-Anmeldung.

---

## Parameterbeschreibung

|Parameter|Beschreibung|
|---|---|
|`--dataset.repo_id`|Name des Datensatzes (identisch mit der Aufnahme)|
|`--dataset.root`|Lokaler Pfad des Datensatzes (identisch mit der Aufnahme)|
|`--policy.type`|Policy-Typ; `act` ist eine gängige Wahl|
|`--output_dir`|Ausgabeverzeichnis des Trainings (Checkpoints, Protokolle)|
|`--job_name`|Auftragsname (zur Unterscheidung in den Protokollen)|
|`--policy.device`|`cuda` (GPU) oder `cpu`|
|`--wandb.enable`|Gewichtsprotokollierung; `false` deaktiviert sie (kein wandb-Konto erforderlich)|
|`--policy.push_to_hub`|Ob das Modell zu HF gepusht wird; `false` bedeutet nur lokal|
|`--steps`|Anzahl der Trainingsschritte|

---

## Erläuterung des Trainingsablaufs

- **checkpoints**: Werden nach jedem Schritt automatisch unter `outputs/train/soarm_amazing_hand_pick/checkpoints/` gespeichert

- **Protokolle**: Das Terminal zeigt Kennzahlen wie loss in Echtzeit an

- **Dauer**: 60000 Schritte dauern auf einer Consumer-GPU in der Regel mehrere Stunden (genau je nach Grafikkarte)

> **⚠️ Hinweis 1 (Anpassung der Schrittzahl)**: `--steps=60000` ist ein typischer Wert für ACT. Bei einfachen Aufgaben kann auf 30000 reduziert, bei komplexen Aufgaben auf 100000\+ erhöht werden. Beobachten Sie die Konvergenz des loss.

> **⚠️ Hinweis 2 (Fortsetzen nach Trainingsunterbrechung)**: Wenn Sie nach einer Unterbrechung **denselben Befehl mit denselben Parametern** erneut ausführen, wird vom letzten checkpoint aus fortgesetzt.

> **⚠️ Hinweis 3 (wandb)**: Wenn Sie die loss-Kurve visualisieren möchten, können Sie `--wandb.enable=true` aktivieren (erfordert `wandb login`). Standardmäßig deaktiviert.

> **⚠️ Hinweis 4 (Arbeitsspeicher/VRAM)**: Bei unzureichendem VRAM können Sie `--policy.batch_size=8` hinzufügen (Batch-Größe verringern); bei unzureichendem Arbeitsspeicher für die Videodekodierung können Sie `width/height` verringern.

---

Nach Abschluss dieser Phase fahren Sie mit Phase 6: Deployment und Evaluierung fort.

---

## Fehlerbehebung

|Symptom|Ursache|Lösung|
|---|---|---|
|`CUDA: False`|CPU-Version von torch|CUDA-Version von torch neu installieren|
|VRAM unzureichend (OOM)|Batch-Größe zu groß|`--policy.batch_size=8` oder niedriger|
|Datensatz nicht gefunden|repo\_id/root stimmen nicht überein|Stellen Sie sicher, dass `--dataset.repo_id` und `--dataset.root` mit der Aufnahme vollständig übereinstimmen|
|Training ist langsam|Training auf der CPU|GPU verwenden; oder `--steps` verringern|
|`wandb` meldet Fehler|Nicht angemeldet|`--wandb.enable=false` oder `wandb login`|

