# linux

# Fase 1: Configurazione dell'ambiente (Linux)

Usa **Miniforge** per creare un ambiente Python indipendente e installare LeRobot e il supporto per AmazingHand. Questa pagina va eseguita in **ordine rigoroso**; ogni blocco di codice può essere copiato per intero.

> Versioni dell'ambiente: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (versione personalizzata di questo repository) · Si consiglia Ubuntu 20\.04/22\.04

---

## Passo 1: Installare Miniforge

```Bash
wget "https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-$(uname)-$(uname -m).sh"
```

```Bash
bash Miniforge3-$(uname)-$(uname -m).sh -b
~/miniforge3/bin/conda init
source ~/.bashrc
```

```Bash
conda --version
```

> Indirizzo ufficiale (reti estere): `https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh`

---

## Passo 2: Configurare il canale nazionale di conda (reti della Cina continentale)

```Bash
conda config --remove-key channels
```

```Bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` non è più disponibile (404), non aggiungerlo. Se non hai restrizioni di rete, puoi saltare questo passo.

---

## Passo 3: Installare gli strumenti di compilazione (necessari sui sistemi nuovi)

Una nuova installazione di Ubuntu può non avere strumenti di compilazione come `gcc`; per installare pacchetti come `evdev` servono:

```Bash
sudo apt update
sudo apt install -y build-essential
```

---

## Passo 4: Creare l'ambiente virtuale

```Bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```Bash
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Attesi `Python 3.12.x` \+ `64 bit`.

---

## Passo 5: Installare ffmpeg (necessario per la decodifica video)

La registrazione/riproduzione dei dati video di LeRobot dipende da ffmpeg:

```Bash
conda install ffmpeg -c conda-forge -y
```

---

## Passo 6: Installare le dipendenze del progetto

```Bash
cd ~/lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` include: `feetech-servo-sdk` (motori del braccio), `rustypot` (motori della mano), `pygame` (GUI di calibrazione), `pyserial` (porta seriale).

> Se pip è lento, configura prima il canale nazionale:

```Bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Passo 7: Configurare i permessi della porta seriale

```Bash
sudo chmod 666 /dev/ttyACM*
```

> Soluzione permanente (regole udev, per il chip CP210x, VID `10c4`):

```Bash
sudo tee /etc/udev/rules.d/99-servo.rules << 'EOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## Passo 8: Verificare l'ambiente

```Bash
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> Deve mostrare `all OK` e `usage: lerobot-calibrate-amazing-hand ...`.

---

## Passo 9: Confermare la porta seriale

```Bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

Oppure `lerobot-find-port`. Conferma i percorsi dei tre dispositivi (esempio `/dev/ttyACM0`/`/dev/ttyACM1`/`/dev/ttyACM2`, **da sostituire con i tuoi valori reali**).

---

Completato → Fase 2: Calibrazione

---

## Risoluzione dei problemi

|Sintomo|Soluzione|
|---|---|
|Comando `conda` non trovato|`source ~/.bashrc` oppure riapri il terminale dopo `conda init`|
|`pkgs/free` 404|Quel canale non è più disponibile, non aggiungerlo|
|Porta seriale `Permission denied`|Passo 7 `sudo chmod 666`|
|Dipendenze non si installano / lente|Configura il canale nazionale di pip (indicato al passo 6)|
|Errore di compilazione di `evdev` durante l'installazione|Passo 3 `sudo apt install build-essential`|
|Addestramento su GPU, controllo CUDA `False`|Vedi il documento di addestramento della fase 5|

