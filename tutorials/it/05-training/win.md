# win

# Fase 5: Addestramento del modello (Windows)

In questa fase si usa il dataset raccolto per addestrare una politica (ACT e simili) e produrre un modello distribuibile. L'addestramento è il passo più dispendioso in termini di tempo; **si consiglia di usare una NVIDIA GPU**.

---

## Prerequisiti

- Aver completato la Fase 4: Acquisizione dati

- NVIDIA GPU (consigliata), driver CUDA

- Dataset già registrato (visibile nella cache locale)

---

## Passo 1: Confermare l'ambiente GPU

```PowerShell
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**Output atteso**: `CUDA: True | GPU: <your_gpu_name>`

> **⚠️ Nota (CUDA torch)**: se `CUDA: False`, significa che è installata la versione di torch per CPU. Occorre reinstallare la versione con CUDA:

```PowerShell
# Sorgente ufficiale (reti all'estero)
pip install torch --index-url https://download.pytorch.org/whl/cu128

# In Cina continentale, dare priorità al mirror di Alibaba Cloud
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
```

> Oppure addestra su CPU (`--policy.device=cpu`, ma molto più lento; non realistico per compiti complessi).

---

## Passo 2: Addestrare

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

> **💡 Descrizione**: `--dataset.repo_id` e `--dataset.root` devono essere **esattamente identici** a quelli della registrazione della fase 4 (`repo_id=soarm_amazing_hand_pick`, `root=D:\lerobot_data`); così si può leggere il dataset locale senza necessità di accedere a HF.

---

## Descrizione dei parametri

|Parametro|Descrizione|
|---|---|
|`--dataset.repo_id`|Nome del dataset (uguale a quello della registrazione)|
|`--dataset.root`|Percorso locale del dataset (uguale a quello della registrazione)|
|`--policy.type`|Tipo di politica; `act` è la scelta più comune|
|`--output_dir`|Directory di output dell'addestramento (checkpoints, log)|
|`--job_name`|Nome del compito (per distinguere i log)|
|`--policy.device`|`cuda` (GPU) oppure `cpu`|
|`--wandb.enable`|Log dei pesi; `false` lo disattiva (senza bisogno di un account wandb)|
|`--policy.push_to_hub`|Se inviare il modello a HF; `false` solo locale|
|`--steps`|Numero di passi di addestramento|

---

## Descrizione del processo di addestramento

- **checkpoints**: salvati automaticamente a ogni passo in `outputs/train/soarm_amazing_hand_pick/checkpoints/`

- **Log**: il terminale mostra in tempo reale metriche come la loss

- **Durata**: 60000 passi richiedono di solito alcune ore su una GPU di fascia consumer (dipende dalla scheda grafica)

> **⚠️ Nota 1 (regolazione dei passi)**: `--steps=60000` è il valore tipico di ACT. Per compiti semplici si può ridurre a 30000 e per compiti complessi aumentare a 100000\+. Osserva la convergenza della loss.

> **⚠️ Nota 2 (riprendere dopo un'interruzione)**: in caso di interruzione, rieseguire **il comando con gli stessi parametri** riprenderà dall'ultimo checkpoint.

> **⚠️ Nota 3 (wandb)**: se hai bisogno di visualizzare la curva della loss, puoi attivare `--wandb.enable=true` (richiede `wandb login`). Per impostazione predefinita è disattivato.

> **⚠️ Nota 4 (memoria RAM/memoria video)**: se la memoria video è insufficiente puoi aggiungere `--policy.batch_size=8` (riduce la dimensione del batch); se la memoria è insufficiente nella decodifica video puoi ridurre `width/height`.

---

Dopo aver completato questa fase, passa alla Fase 6: Distribuzione e valutazione.

---

## Risoluzione dei problemi

|Sintomo|Causa|Soluzione|
|---|---|---|
|`CUDA: False`|torch per CPU|Reinstalla la versione di torch con CUDA|
|Memoria video insufficiente (OOM)|Dimensione del batch troppo grande|`--policy.batch_size=8` o inferiore|
|Dataset non trovato|repo\_id/root incoerenti|Verifica che `--dataset.repo_id` e `--dataset.root` siano esattamente identici a quelli della registrazione|
|Addestramento lento|Addestramento su CPU|Usa la GPU; oppure riduci `--steps`|
|Errore di `wandb`|Accesso non effettuato|`--wandb.enable=false` o `wandb login`|

