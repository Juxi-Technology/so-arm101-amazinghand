# win

# Fase 4: Acquisizione dati (Windows)

In questa fase si registra il dataset di teleoperazione: sotto controllo manuale si raccolgono campioni di “angoli delle articolazioni \+ immagini delle telecamere” per l'addestramento successivo. La qualità del dataset determina direttamente l'efficacia della politica; **l'operazione deve essere regolare e coerente**. In questa fase **tutta la registrazione è locale, senza necessità di accedere a HF**.

---

## Prerequisiti

- Aver completato la Fase 3: Teleoperazione e verificato che la direzione è corretta

- Telecamere collegate e con l'indice registrato (`lerobot-find-cameras`)

- Percorso di archiviazione locale del dataset già stabilito (in questo documento si usa l'esempio `D:\lerobot_data`, personalizzabile)

---

## Passo 1: Confermare l'indice della telecamera

```PowerShell
lerobot-find-cameras
```

Registra il numero di ciascuna telecamera. Ad esempio:

- Numero 0: telecamera del polso (wrist)

- Numero 1: telecamera superiore (top)

> **⚠️ Nota (indice della telecamera)**: `index_or_path` è l'indice della telecamera (0/1/2\.\.\.) oppure il percorso dello stream video. La numerazione varia da computer a computer; confermala sempre prima.

---

## Passo 2: Registrare il dataset (salvataggio locale, senza accesso)

```PowerShell
lerobot-record --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data --dataset.push_to_hub=false --dataset.num_episodes=20 --dataset.single_task="Pick up the cube with the dexterous hand" --display_data=true
```

> Sostituisci `<follower_arm_com>` / `<hand_com>` / `<leader_arm_com>` con i numeri COM reali; e `index_or_path` delle telecamere con l'indice delle tue telecamere.

> **💡 Descrizione**:

- `--dataset.root=D:\lerobot_data`: il dataset viene salvato nel **percorso locale** indicato, **senza necessità di accedere a HF** (se non specificato, viene salvato per impostazione predefinita in `%USERPROFILE%\.cache\huggingface\lerobot\datasets\...`).

- `--dataset.push_to_hub=false`: **disattiva il caricamento** (per impostazione predefinita tenta di inviarlo a HF e richiede l'accesso). Si passa a `true` solo quando occorre condividere il dataset.

- `--dataset.repo_id=soarm_amazing_hand_pick`: nome del dataset; in fase di addestramento lo si richiama con **lo stesso nome**.

- `--display_data=true` richiede rerun (se non installato, `pip install "rerun-sdk>=0.24.0,<0.34.0"`); in alternativa togli questo parametro (la registrazione non ne risente).

---

## Descrizione dei parametri

|Parametro|Descrizione|
|---|---|
|`--robot.cameras`|Configurazione delle telecamere. `index_or_path` è l'indice della telecamera; `width/height/fps` sono **obbligatori**|
|`--dataset.repo_id`|Nome del dataset (per l'identificazione locale)|
|`--dataset.root`|Percorso di archiviazione locale del dataset. **Obbligatorio per la registrazione puramente locale**, per evitare un percorso predefinito non controllabile|
|`--dataset.push_to_hub`|`false`=solo locale (consigliato per impostazione predefinita); `true`=invio a HF (richiede l'accesso)|
|`--dataset.num_episodes`|Numero di round di registrazione (episode)|
|`--dataset.episode_time_s`|**Numero massimo di secondi di registrazione per round** (predefinito 60). Se il compito termina prima, si può premere Enter per concludere in anticipo; superato il limite, il round termina automaticamente|
|`--dataset.single_task`|Descrizione del compito, viene scritta nei metadati del dataset|
|`--display_data=true`|Mostra in tempo reale l'immagine della registrazione (opzionale)|

---

## Regole di comportamento durante la registrazione

**Flusso di ogni round (episode)**:

1. Riporta il braccio robotico \+ la mano alla **posizione iniziale**

2. Nel terminale premi Enter per iniziare a registrare

3. Aziona il braccio master per eseguire il compito (ad esempio afferrare il cubo); **i movimenti devono essere lenti e coerenti**

4. Al termine del compito premi Enter per concludere il round (**se non premi, si registrano al massimo 60 secondi**, controllati da `--dataset.episode_time_s`; allo scadere termina automaticamente)

5. Ripeti fino a raggiungere `num_episodes`

> **⚠️ Nota 1 (posizione iniziale coerente)**: inizia ogni round dalla **stessa posizione iniziale** per evitare che la distribuzione dei dati diventi caotica. Si consiglia di fissare una postura di riposizionamento.

> **⚠️ Nota 2 (coerenza dei movimenti)**: per lo stesso compito usa traiettorie di azionamento simili (angolo di avvicinamento, posizione di presa, velocità); la politica impara più in fretta e in modo più stabile.

> **⚠️ Nota 3 (qualità della registrazione)**: meglio registrare pochi round di alta qualità che una grande quantità di campioni caotici. 20 round è il punto di partenza di ACT; per compiti complessi si consigliano 30\-50 round.

> **⚠️ Nota 4 (tempestività delle telecamere)**: durante la registrazione evita di coprire le telecamere e variazioni di luce intensa; la coerenza delle immagini influisce sulla generalizzazione.

---

## Archiviazione dei dati

- **Registrazione locale**: i dati vengono salvati nella directory indicata da `--dataset.root` (esempio `D:\lerobot_data\soarm_amazing_hand_pick`).

- **Richiamo in addestramento**: in fase di addestramento è sufficiente usare **lo stesso ****`--dataset.repo_id`**** \+ ****`--dataset.root`**, senza bisogno di spostare manualmente i file:

```PowerShell
lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data ...
```

- **Scenario con accesso a HF** (opzionale): quando occorre condividere il dataset nel cloud, passa a `--dataset.push_to_hub=true` (richiede `huggingface-cli login`). Per l'addestramento solo locale **non è necessario**.

> **⚠️ Nota (locale vs cloud)**: per impostazione predefinita il tutorial è interamente locale; `--dataset.push_to_hub=false` garantisce che non si attivi l'accesso a HF. Aggiungi `true` solo se vuoi condividere il dataset.

---

## Passo 3: Verifica tramite riproduzione (opzionale ma consigliata)

Terminata la registrazione, si può usare `lerobot-replay` per riprodurre i dati di un round e verificare la **qualità dei dati \+ se la registrazione dei movimenti del robot è corretta**. Durante la riproduzione il robot ripete automaticamente i movimenti di quel round (compresa l'apertura/chiusura della mano).

```PowerShell
lerobot-replay `
  --robot.type=so101_amazing_hand `
  --robot.port=<follower-port> `
  --robot.hand_port=<hand-port> `
  --robot.id=amazing_hand_follower `
  --dataset.repo_id=soarm_amazing_hand_pick `
  --dataset.root=D:\lerobot_data `
  --dataset.episode=0
```

> Sostituisci `<follower_arm_com>` / `<hand_com>` con i numeri COM reali; `--dataset.episode` è il numero del round da riprodurre (**parte da 0**; se hai registrato 20 round va da `0`\~`19`).

> **💡 Descrizione**: prima della riproduzione riporta il braccio slave \+ la mano **alla posizione iniziale** per evitare conflitti di movimento; durante la riproduzione il robot si muove da solo, **non intervenire manualmente**. Se i movimenti della riproduzione differiscono nettamente da quelli della registrazione, significa che la qualità dei dati ha problemi; si consiglia di registrare di nuovo quel round.

---

Dopo aver completato questa fase, passa alla Fase 5: Addestramento del modello.

---

## Risoluzione dei problemi

|Sintomo|Causa|Soluzione|
|---|---|---|
|Telecamera non trovata|Indice errato/driver mancante|Conferma con `lerobot-find-cameras`; installa OpenCV/il driver della telecamera|
|Registrazione interrotta|Timeout della porta seriale|Verifica che le porte seriali dei tre dispositivi non siano occupate e riprova|
|Immagine completamente nera/disturbata|Configurazione della telecamera errata|Controlla `index_or_path`/`fps`|
|Dataset vuoto|Registrazione non eseguita correttamente|Verifica che a ogni round si prema Enter per iniziare/terminare|

