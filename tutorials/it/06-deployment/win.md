# win

# Fase 6: Distribuzione e valutazione (Windows)

In questa fase si carica la politica addestrata per far **eseguire il compito in autonomia** al robot e si registra un video di valutazione per verificarne l'efficacia. È la conclusione dell'intero flusso e anche il momento chiave per verificare i risultati dell'addestramento.

---

## Prerequisiti

- Aver completato la Fase 5: Addestramento del modello

- Output dell'addestramento `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/`

- Indice della telecamera registrato

---

## Passo 1: Confermare i file del modello

```PowerShell
# Verificare che la directory del modello esista
dir outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model
```

Deve contenere file del modello come `model.safetensors`.

> **⚠️ Nota (percorso del modello)**: `--policy.path` deve puntare alla directory `pretrained_model` (che contiene la configurazione \+ i pesi), non alla directory radice del checkpoint.

---

## Passo 2: Distribuzione e valutazione

```PowerShell
lerobot-record `
  --robot.type=so101_amazing_hand `
  --robot.port=<follower-port> `
  --robot.hand_port=<hand-port> `
  --robot.id=amazing_hand_follower `
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' `
  --policy.path=outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model `
  --dataset.repo_id=soarm_amazing_hand_pick_eval `
  --dataset.root=D:\lerobot_data `
  --dataset.push_to_hub=false `
  --dataset.num_episodes=10 `
  --dataset.single_task="Pick up the cube with the dexterous hand" `
  --display_data=true
```

> Sostituisci `<follower_arm_com>` / `<hand_com>` con i numeri COM reali; e `index_or_path` delle telecamere con l'indice delle tue telecamere.

> **💡 Descrizione**: si usa `lerobot-record` ma **senza aggiungere ****`--teleop.type`**; la politica controllerà il robot in autonomia (al posto della teleoperazione manuale). I dati vengono salvati come set di valutazione. `--dataset.root` / `--dataset.push_to_hub=false` sono uguali a quelli della fase 4; il salvataggio puramente locale non richiede l'accesso a HF.

---

## Operazioni di valutazione

1. Riporta il robot \+ la mano alla **posizione iniziale**

2. Premi Enter per iniziare: la politica esegue il compito in autonomia

3. Osserva **se la presa riesce** (alla fine di ogni round premi Enter per continuare)

4. Ripeti per `num_episodes` round

**Metrica di valutazione**: tasso di successo = round riusciti / round totali

> **⚠️ Nota 1 (coerenza del riposizionamento)**: inizia ogni round dalla **stessa posizione iniziale**; altrimenti la politica fallisce la generalizzazione e il tasso di successo risulta artificialmente basso.

> **⚠️ Nota 2 (sicurezza)**: alla prima esecuzione autonoma si consiglia di osservare **tenendo il robot/andando piano** per confermare che i movimenti della politica siano ragionevoli. La politica può compiere movimenti imprevisti.

> **⚠️ Nota 3 (tasso di successo atteso)**: ACT con 20 round di dati raggiunge di solito un tasso di successo del 50\-80%. Se è inferiore al previsto, torna indietro per registrare altri dati o regola il numero di passi di addestramento.

---

## Ottimizzazione iterativa

Se il tasso di successo della valutazione non è soddisfacente, regola in ordine di priorità:

|Priorità|Voce di ottimizzazione|Operazione|
|---|---|---|
|1|Registrare dati aggiuntivi di alta qualità|Torna alla Fase 4 e registra 20\-30 round di dati più coerenti|
|2|Aumentare i passi di addestramento|Torna alla Fase 5, `--steps=100000`|
|3|Controllare la coerenza della posizione iniziale|Riposiziona rigorosamente a ogni round durante la valutazione|
|4|Regolare la descrizione del compito|Assicurati che `single_task` corrisponda al compito|

---

Con questo si completa il **ciclo completo** di SO\-ARM101 \+ AmazingHand: calibrazione → teleoperazione → acquisizione → addestramento → distribuzione.

---

## Risoluzione dei problemi

|Sintomo|Causa|Soluzione|
|---|---|---|
|Caricamento del modello non riuscito|Percorso errato/incompleto|Verifica che `--policy.path` punti alla directory `pretrained_model`|
|La politica non si muove|Errore di telecamera/osservazione|Verifica che l'indice della telecamera sia uguale a quello dell'addestramento; controlla l'immagine di `--display_data`|
|La politica si muove in modo errato|Posizione iniziale incoerente/dati scadenti|Riposiziona rigorosamente; registra dati aggiuntivi|
|Prestazioni diverse da quelle dell'addestramento|Differenze ambientali|Verifica che telecamera, illuminazione e posizione degli oggetti siano uguali a quelle della registrazione|

