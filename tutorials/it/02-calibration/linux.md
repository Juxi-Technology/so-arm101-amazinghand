# linux

# Fase 2: Calibrazione (Linux)

In questa fase si calibrano i tre dispositivi: il braccio master, il braccio slave e la mano AmazingHand. La calibrazione è il presupposto per la correttezza della teleoperazione; **è obbligatorio completare questa fase per passare alla teleoperazione**.

> **Ordine di calibrazione**: braccio master → braccio slave\+mano → angoli della mano. Ogni passo richiede **interazione nel terminale** (operazione fisica \+ pressione di tasti).

> **⚠️ Avviso generale**: i parametri della porta seriale nei comandi di questa pagina sono **segnaposto di esempio**; devi sostituirli con i percorsi reali della porta seriale della tua macchina (vedi le porte seriali registrate nella fase 1).

---

## Prerequisiti

- Aver completato la Fase 1: Configurazione dell'ambiente

- Ambiente conda `lerobot` attivato

- Permessi della porta seriale configurati (sezione 5 della fase 1)

- Porte seriali dei tre dispositivi registrate

- Dispositivi accesi e con alimentazione indipendente

---

## Passo 1: Calibrare il braccio master

```Bash
lerobot-calibrate \
  --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Sostituisci `<leader_arm_port>` con il percorso reale della tua macchina (esempio `/dev/ttyACM1`).

**Passi di interazione**:

1. Porta **tutte le articolazioni del braccio master in posizione intermedia** e premi Enter

2. **Spingi ogni articolazione in sequenza fino alla corsa massima/minima** e premi Enter al termine

**Verifica**: il file di calibrazione viene salvato automaticamente in
`~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/amazing_hand_leader.json`

> **⚠️ Nota 1 (la pinza va calibrata)**: la corsa del servomotore della pinza n. 6 funge da base di normalizzazione per `gripper.pos` (0\~100). La pinza va portata da completamente aperta a completamente chiusa e calibrata a dovere; altrimenti la proporzione di apertura/chiusura della mano risulta distorta.

> **⚠️ Nota 2 (rotazione libera)**: durante la calibrazione il braccio robotico deve poter ruotare liberamente; assicurati che i servomotori siano a vuoto.

> **⚠️ Nota 3 (permessi)**: se compare `Permission denied` sulla porta seriale, esegui prima `sudo chmod 666 /dev/ttyACM*` (oppure verifica che le regole udev siano già configurate nella fase 1).

---

## Passo 2: Calibrare il braccio slave (collegando contemporaneamente la mano)

```Bash
lerobot-calibrate \
  --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower
```

> Sostituisci `<follower_arm_port>` / `<hand_port>` con i percorsi reali (esempio `/dev/ttyACM0` / `/dev/ttyACM2`).

**Passi di interazione**:

1. Porta le **5 articolazioni** del braccio slave (senza la n. 6) in posizione intermedia e premi Enter

2. Fai compiere a ogni articolazione l'intera corsa e premi Enter

**Verifica**: il file di calibrazione viene salvato in
`~/.cache/huggingface/lerobot/calibration/robots/so101_amazing_hand/amazing_hand_follower.json`

> **⚠️ Nota 1 (la coppia della mano si attiva automaticamente)**: al collegamento questo comando **attiva automaticamente la coppia degli 8 servomotori della mano** (il log mostra `enabling AmazingHand torque`); al termine della calibrazione la mano si apre, ed è normale.

> **⚠️ Nota 2 (non compare la GUI della mano)**: per gli angoli della mano **non** si usa il `RangeFinderGUI` di lerobot; la calibrazione del braccio slave termina e basta. Per gli angoli della mano si usa lo strumento dedicato del passo 3.

> **⚠️ Nota 3 (occupazione della porta seriale)**: questo passo occupa la porta seriale della mano. **Non** eseguire contemporaneamente altri processi che occupano quella porta seriale.

---

## Passo 3: Calibrare gli angoli della mano \+ la direzione della pinza (GUI dedicata)

```Bash
lerobot-calibrate-amazing-hand --hand_port <hand-port> --leader_port <leader-port>
```

> Sostituisci `<hand_port>` / `<leader_arm_port>` con i percorsi reali (esempio `/dev/ttyACM2` / `/dev/ttyACM1`). `--leader_port` serve per calibrare in modo sincronizzato la **direzione della pinza** (vedi sotto).

> **⚠️ Nota (ambiente senza display)**: la GUI richiede un desktop grafico. Se eseguita in un ambiente senza monitor/SSH, compare `pygame.error: video system not initialized`. Soluzioni:

- Eseguirla in una sessione grafica locale; oppure

- Eseguirla tramite inoltro X11 (`ssh -X`).

**Operazioni della GUI**:

1. Trascina i cursori delle 4 dita (index/middle/ring/thumb) per portare la mano **completamente aperta** e fai clic su **`Save Open`**

2. Trascina i cursori per portare la mano **completamente chiusa a pugno** e fai clic su **`Save Close`**

3. **Apri la pinza del braccio master** e fai clic su **`Capture Open`** (la GUI mostra `gripper.pos` in tempo reale; all'apertura deve avvicinarsi a 100)

4. **Pizzica la pinza del braccio master** e fai clic su **`Capture Close`** (al pizzicamento deve avvicinarsi a 0)

5. **Salvataggio automatico**: dopo aver impostato tutti e quattro i valori, nella parte superiore della finestra compare un banner verde `AUTO-SAVED to .../hand_angles.json` e il terminale stampa in sincrono il percorso

6. Chiudi la finestra (la mano disattiva automaticamente la coppia)

**Verifica**: gli angoli e la mappatura della pinza vengono salvati in
`~/.cache/huggingface/lerobot/calibration/robots/so101_amazing_hand/hand_angles.json`

> **⚠️ Nota 1 (calibrazione obbligatoria)**: **è obbligatorio eseguire questo passo su ogni nuovo computer e con ogni mano**. Gli angoli nel config sono i valori predefiniti generici ufficiali di AmazingHand e servono solo come riserva; se esiste `hand_angles.json`, vengono caricati con priorità i tuoi valori misurati. Non calibrare può causare errori nella direzione/corsa di apertura e chiusura.

> **⚠️ Nota 2 (caricamento automatico)**: a ogni avvio il robot legge `hand_angles.json` (che contiene `gripper_open_pos`/`gripper_close_pos`) e sovrascrive i valori predefiniti del config, **senza bisogno di modificare il codice**. La direzione della pinza varia in base al braccio master; è sufficiente calibrarla una volta.

> **⚠️ Nota 3 (semantica dei cursori)**: spostando il cursore verso `+`, quel dito muove m1 verso `+angle` e m2 verso `-angle` (a specchio). Valuta apertura/pugno in base alla **postura reale della mano**, senza badare al valore numerico dell'angolo.

> **⚠️ Nota 4 (calibrazione precisa)**: nel calibrare “completamente aperta” non esagerare (dita storte/distanziate) e nel calibrare “completamente chiusa a pugno” non comprimere eccessivamente (i servomotori resterebbero sotto sforzo continuo).

> **⚠️ Nota 5 (ordine di Capture)**: `Capture Open` / `Capture Close` corrispondono all'apertura/chiusura della **pinza del braccio master**, non alle dita della mano. Se la direzione di apertura della mano risulta invertita, quasi sempre è perché qui è stata calibrata al contrario o perché gli angoli della mano sono invertiti; è sufficiente ricalibrare.

---

## Ricalibrazione

Quando occorre ricalibrare solo una parte:

- **Ricalibrare solo la mano** → esegui solo il passo 3

- **Ricalibrare solo il braccio slave** → esegui solo il passo 2 (attiva di conseguenza la coppia della mano)

- **Ricalibrare tutto** → passi 1 → 2 → 3

> **⚠️ Nota**: i passi 2 e 3 **non possono essere eseguiti contemporaneamente** (occupano entrambi la porta seriale della mano).

---

Dopo aver completato questa fase, passa alla Fase 3: Teleoperazione.

---

## Risoluzione dei problemi

|Sintomo|Causa|Soluzione|
|---|---|---|
|Porta seriale `Permission denied`|Permessi non configurati|`sudo chmod 666 /dev/ttyACM*` o configura udev|
|La GUI di calibrazione della mano non si apre|Ambiente senza grafica|Esegui in una sessione grafica locale oppure con inoltro `ssh -X`|
|Il driver della mano segnala `Operation timed out`|Porta seriale occupata/temporizzazione|Verifica che la porta seriale della mano non sia occupata e riprova|
|La calibrazione del braccio master segnala l'errore modello 2307|Bus del braccio contaminato|Verifica che la porta seriale della mano non sia collegata contemporaneamente; in questo progetto la mano usa rustypot e il problema è evitato|

