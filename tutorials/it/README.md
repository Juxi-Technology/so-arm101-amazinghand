# README

# Tutorial d'uso di SO\-ARM101 \+ AmazingHand

Questo tutorial è pensato per riprodurre l'intero flusso di teleoperazione, acquisizione dati e addestramento di **SO\-ARM101 braccio slave \+ mano robotica AmazingHand**, basato su LeRobot (versione personalizzata del repository ufficiale).

Il tutorial è organizzato per **fasi**; ogni fase costituisce una directory indipendente e al suo interno è suddiviso per sistema operativo in due documenti: `win.md` (Windows) e `linux.md` (Linux). Scegli il documento corrispondente in base al tuo sistema operativo.

---

## Panoramica di hardware e software

|Dispositivo|Porta seriale (esempio, da sostituire)|Modello di servomotore|Descrizione|
|---|---|---|---|
|Braccio master (Leader)|`COM54` / `/dev/ttyACM1`|Modello misto<br>`sts3125-C001、sts3215-C044、sts3215-C046`|Ingresso di teleoperazione, mantiene la pinza n. 6|
|Braccio slave (Follower)|`COM58` / `/dev/ttyACM0`|`sts3215-C018` (n. 1\-5)|Lato di esecuzione, pinza n. 6 rimossa|
|Mano robotica AmazingHand|`COM11` / `/dev/ttyACM2`|`scs0009` (8 unità, ID 1\-8)|Estremità del braccio slave, porta seriale indipendente|

> **⚠️ Il nome della porta seriale varia da macchina a macchina**: la tabella precedente è solo un esempio. Il numero COM/percorso del dispositivo è diverso su ogni computer; è indispensabile usare `lerobot-find-port` per confermare i valori reali della tua macchina e sostituire tutti i parametri segnaposto nei comandi.

> I tre dispositivi devono avere **ciascuno una porta seriale indipendente e un'alimentazione indipendente**. SCS0009 (protocollo 1) e STS3215 (protocollo 0) non sono compatibili sullo stesso bus.

---

## Struttura delle directory del tutorial

```Plaintext
tutorials/
├── README.md                          # 本文件（总览）
├── 01-environment/                    # 阶段一：环境搭建
│   ├── win.md                         #   Windows 环境搭建
│   └── linux.md                       #   Linux 环境搭建
├── 02-calibration/                    # 阶段二：标定
│   ├── win.md
│   └── linux.md
├── 03-teleoperation/                  # 阶段三：遥操作
│   ├── win.md
│   └── linux.md
├── 04-data-collection/                # 阶段四：数据采集
│   ├── win.md
│   └── linux.md
├── 05-training/                       # 阶段五：模型训练
│   ├── win.md
│   └── linux.md
└── 06-deployment/                     # 阶段六：部署与评估
    ├── win.md
    └── linux.md
```

---

## Percorso di lettura consigliato

|Passo|Fase|Windows|Linux|
|---|---|---|---|
|1|Configurazione dell'ambiente|01\-environment/win\.md|01\-environment/linux\.md|
|2|Calibrazione|02\-calibration/win\.md|02\-calibration/linux\.md|
|3|Teleoperazione|03\-teleoperation/win\.md|03\-teleoperation/linux\.md|
|4|Acquisizione dati|04\-data\-collection/win\.md|04\-data\-collection/linux\.md|
|5|Addestramento del modello|05\-training/win\.md|05\-training/linux\.md|
|6|Distribuzione e valutazione|06\-deployment/win\.md|06\-deployment/linux\.md|

---

## Riepilogo rapido delle differenze principali tra le fasi

|Aspetto|Windows|Linux|
|---|---|---|
|Ambiente Python|Miniconda \+ `conda create -n lerobot python=3.12`|Miniforge \+ lo stesso comando|
|Nome della porta seriale|`COM54` / `COM58` / `COM11` (esempio)|`/dev/ttyACM0/1/2` (esempio)|
|Permessi della porta seriale|Nessuna configurazione speciale|Richiede `sudo chmod 666 /dev/ttyACM*` o regole udev|
|Richiamo dei comandi|`lerobot-xxx` dopo l'attivazione di conda|`lerobot-xxx` dopo l'attivazione di conda|
|Addestramento con CUDA|Richiede l'installazione manuale di torch con CUDA|Supporto ufficiale, risoluzione fluida|

---

## Note generali

1. **Completa prima la fase uno, poi passa alle fasi successive**: l'ambiente è il presupposto di tutti i comandi successivi.

2. **Ogni computer deve essere ricalibrato**: in particolare gli angoli della mano (`lerobot-calibrate-amazing-hand`); gli angoli nel config sono i valori predefiniti generici ufficiali di AmazingHand e servono solo come riserva; se esiste `hand_angles.json`, vengono caricati con priorità i valori misurati sulla tua macchina.

3. **Posizione dei file di calibrazione**: `~/.cache/huggingface/lerobot/calibration/`; cambiando macchina occorre migrarli o ricalibrare.

4. **Alla prima teleoperazione verifica sempre la direzione**: apertura della pinza ↔ apertura della mano, pizzicamento ↔ chiusura della mano.

5. I file `win.md` / `linux.md` di ogni fase contengono **note specifiche di quella piattaforma**; leggili per intero.

---

## Punto di accesso per la risoluzione dei problemi

I documenti di ogni fase includono tabelle di risoluzione dei problemi per piattaforma. Problemi comuni:

- conda non inizializzato/comando non trovato

- permessi insufficienti sulla porta seriale (Linux)

- mappatura errata della direzione mano/braccio

- angoli della mano non calibrati che causano un'apertura/chiusura anomala

Per i dettagli consulta i documenti di ogni fase.

