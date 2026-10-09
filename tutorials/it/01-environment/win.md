# win

# Fase 1: Configurazione dell'ambiente (Windows)

Usa **Miniconda** per creare un ambiente Python indipendente e installare LeRobot e il supporto per AmazingHand. Questa pagina va eseguita in **ordine rigoroso**; ogni blocco di codice può essere copiato per intero.

> Versioni dell'ambiente: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (versione personalizzata di questo repository)

---

## Passo 1: Installare Miniconda

**Installazione da riga di comando** (PowerShell, consigliata): per le reti della Cina continentale usa lo specchio di Tsinghua:

```PowerShell
curl.exe -L -o Miniconda3-latest-Windows-x86_64.exe https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Windows-x86_64.exe
```

```PowerShell
$installDir = "C:\Users\$env:USERNAME\miniconda3"
Start-Process -Wait .\Miniconda3-latest-Windows-x86_64.exe -ArgumentList "/S", "/D=$installDir"
```

```PowerShell
C:\Users\$env:USERNAME\miniconda3\Scripts\conda.exe init powershell
```

Riapri PowerShell e verifica:

```PowerShell
conda --version
```

> **Installazione grafica** (opzionale): scarica il pacchetto di installazione dal sito ufficiale https://repo\.anaconda\.com/miniconda/Miniconda3\-latest\-Windows\-x86\_64\.exe, fai doppio clic per installare e seleziona **"Add to PATH"**.

> Se il comando `conda` non viene trovato, usa **Anaconda Prompt** (menu Start) al posto di PowerShell.

---

## Passo 2: Configurare il canale nazionale di conda (reti della Cina continentale)

**Prima svuota i canali predefiniti, poi aggiungi lo specchio di Tsinghua** (la nuova versione di Miniconda include di default il canale ufficiale `repo.anaconda.com`, che attiva il controllo dei ToS ed è lento):

```PowerShell
conda config --remove-key channels
```

```PowerShell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` non è più disponibile (404), non aggiungerlo. Se non hai restrizioni di rete, puoi saltare questo passo.

---

## Passo 3: Creare l'ambiente virtuale

```PowerShell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```PowerShell
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Attesi `Python 3.12.x` \+ `64 bit`. Se `conda activate` non mostra il prefisso `(lerobot)`, vedi la risoluzione dei problemi in fondo al documento.

---

## Passo 4: Installare ffmpeg (necessario per la decodifica video)

La registrazione/riproduzione dei dati video di LeRobot dipende da ffmpeg:

```PowerShell
conda install ffmpeg -c conda-forge -y
```

> Se la rete nazionale è lenta, puoi usare il canale conda\-forge di Tsinghua già configurato. Non installarlo provoca errori durante la registrazione dei dati o la riproduzione dei video.

---

## Passo 5: Installare le dipendenze del progetto

```PowerShell
cd D:\Project\lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` include: `feetech-servo-sdk` (motori del braccio), `rustypot` (motori della mano), `pygame` (GUI di calibrazione), `pyserial` (porta seriale).

> Se pip è lento, configura prima il canale nazionale:

```PowerShell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Passo 6: Verificare l'ambiente

```PowerShell
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> Deve mostrare `all OK` e `usage: lerobot-calibrate-amazing-hand ...`.

---

## Passo 7: Confermare la porta seriale

```PowerShell
lerobot-find-port
```

In Gestione dispositivi → Porte \(COM e LPT\) conferma il numero COM dei tre dispositivi (esempio `COM54`/`COM58`/`COM11`; **da sostituire con i tuoi valori reali**). Il numero COM cambia dopo lo scollegamento e il ricollegamento; ripeti la conferma.

---

Completato → Fase 2: Calibrazione

---

## Risoluzione dei problemi

|Sintomo|Soluzione|
|---|---|
|`conda` non è un comando|Riapri il terminale / Anaconda Prompt / `conda init powershell`|
|Errore ToS (repo\.anaconda\.com)|Passo 2: svuota i channels e lascia solo il canale di Tsinghua; oppure `conda tos accept ...`|
|`pkgs/free` 404|Quel canale non è più disponibile, non aggiungerlo|
|`conda activate` senza prefisso|Problema di criteri di esecuzione, vedi sotto|
|Dipendenze non si installano / lente|Configura il canale nazionale di pip (indicato al passo 5)|

**`conda activate` senza il prefisso ****`(lerobot)`** (frequente in Windows):

```PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "D:\Software\Miniconda3\shell\condabin\conda-hook.ps1"
conda activate lerobot
```

> Sostituisci `D:\Software\Miniconda3` con il percorso di installazione della tua Miniconda.

