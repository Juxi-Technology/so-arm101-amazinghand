# linux

# Fase 3: Teleoperazione (Linux)

In questa fase si avvia il ciclo chiuso di teleoperazione: il braccio master controlla il movimento del braccio slave e la pinza controlla l'apertura/chiusura di AmazingHand. È la fase chiave per verificare se l'intero sistema funziona correttamente.

---

## Prerequisiti

- Aver completato la Fase 1: Configurazione dell'ambiente e la Fase 2: Calibrazione

- Permessi della porta seriale configurati

- Dispositivi accesi e porte seriali registrate

---

## Eseguire la teleoperazione

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

> Sostituisci `<follower_arm_port>` / `<hand_port>` / `<leader_arm_port>` con i percorsi reali della tua macchina (esempio `/dev/ttyACM0` / `/dev/ttyACM2` / `/dev/ttyACM1`).

**Effetto previsto**:

- Le 5 articolazioni del braccio master → il braccio slave segue

- La pinza del braccio master → apertura/chiusura di AmazingHand (seguito proporzionale: mezzo pizzicamento = mezza chiusura)

> **💡 Descrizione dei parametri**:

- `--robot.type=so101_amazing_hand`: robot combinato braccio slave \+ mano

- `--robot.port`: porta seriale del braccio slave

- `--robot.hand_port`: porta seriale della mano

- `--teleop.type=so101_leader`: teleoperatore del braccio master

- `--teleop.port`: porta seriale del braccio master

---

## Obbligatorio alla prima esecuzione: verifica della direzione

Dopo l'avvio esegui prima un **test di direzione** per confermare che entrambi i punti seguenti siano corretti:

|Test|Operazione|Fenomeno corretto|
|---|---|---|
|Seguito del braccio|Ruota le articolazioni del braccio master|Il braccio slave segue nella stessa direzione|
|Apertura/chiusura della mano|Apri/pizzica la pinza del braccio master|Pinza aperta → mano aperta; pinza pizzicata → mano chiusa|

> **⚠️ Nota (cosa fare se la direzione è invertita)**:

- **Direzione di apertura/chiusura della mano invertita** (aprendo la pinza la mano si chiude): indica che la calibrazione degli angoli della mano non è precisa; riesegui lo strumento di calibrazione (compresa la calibrazione della direzione della pinza); dopo il salvataggio ha effetto automaticamente, **senza bisogno di modificare i file manualmente**. Vedi la Fase 2: Calibrazione.

- **Direzione della mappatura della pinza invertita** (aprendo la pinza la mano si chiude): come sopra; in fase di calibrazione premi `[Capture Open]` con la pinza del braccio master **aperta** e `[Capture Close]` al **pizzicamento**; lo strumento registra e salva automaticamente `gripper_open_pos`/`gripper_close_pos`, che vengono caricati automaticamente all'avvio.

> Dopo la modifica, **riesegui la teleoperazione** per verificare.

---

## Verifica del seguito proporzionale

Una volta corretta la direzione, verifica la finezza della proporzione:

1. Apri la pinza **lentamente** → la mano deve aprirsi in modo **fluido** (senza salti)

2. Lascia la pinza a **metà** → anche la mano deve fermarsi a metà

3. Apri e chiudi rapidamente → la mano risponde rapidamente, senza impuntamenti

> **⚠️ Nota (problema storico di apertura/chiusura eccessiva della mano)**: se la mano si chiude quando la pinza è solo a metà apertura, quasi sempre è perché le posizioni di “apertura/pugno” non erano accurate durante la calibrazione degli angoli della mano. Riesegui il passo 3 della calibrazione (GUI degli angoli della mano) per calibrare posizioni di apertura/chiusura più precise.

---

## Opzionale: visualizzazione con telecamera

Aggiungi `--robot.cameras` per collegare le telecamere e `--display_data=true` per aprire la finestra di visualizzazione Rerun (mostra in tempo reale l'immagine della telecamera \+ lo stato delle articolazioni):

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

> **💡 Descrizione**:

- `index_or_path` è l'indice della telecamera; confermalo prima con `lerobot-find-cameras` (la numerazione varia da macchina a macchina).

- `fourcc: "MJPG"` è opzionale e può ridurre sensibilmente la banda occupata dalla telecamera USB (passa alla compressione MJPEG); puoi aggiungerlo in caso di impuntamenti.

- Se serve una sola telecamera, elimina la riga corrispondente (ad esempio `top`).

> **⚠️ Nota (dipendenza rerun e visualizzazione)**: `--display_data=true` richiede il pacchetto di visualizzazione rerun; se non è installato esegui:

```Bash
pip install "rerun-sdk>=0.24.0,<0.34.0"
```

> Inoltre la finestra rerun richiede un server di visualizzazione (sessione grafica locale oppure `ssh -X`). Senza ambiente grafico **non influisce sulla teleoperazione**; è sufficiente togliere `--display_data=true`.

---

## Uscita

Premi `Ctrl+C` per fermare. Il programma provvede automaticamente a:

1. Disattivare la coppia degli 8 servomotori della mano

2. Scollegare le porte seriali del braccio slave/braccio master

3. Scollegare le telecamere (se presenti)

> **⚠️ Nota**: prima di un'uscita regolare **non chiudere direttamente il terminale** (ad esempio con `kill -9`), altrimenti può restare un'occupazione residua della porta seriale. Se dopo un'uscita anomala la porta seriale resta occupata, chiudi il processo residuo o ricollega l'USB.

---

## Risoluzione dei problemi

|Sintomo|Causa|Soluzione|
|---|---|---|
|Porta seriale `Permission denied`|Permessi non configurati|`sudo chmod 666 /dev/ttyACM*`|
|Direzione della mano invertita|Angoli della mano o mappatura della pinza invertiti|Vedi “Verifica della direzione” sopra|
|Apertura/chiusura della mano eccessiva o insufficiente|Calibrazione degli angoli della mano imprecisa|Ricalibra gli angoli della mano con la GUI|
|Il braccio non segue|Calibrazione mancante/porta seriale errata|Verifica che il braccio slave sia calibrato e che `--robot.port` sia corretto|
|Errore rerun|Dipendenza di visualizzazione/display mancanti|Togli `--display_data=true`|
|Porta seriale occupata|Uscita anomala precedente|Chiudi il processo residuo o ricollega l'USB|

