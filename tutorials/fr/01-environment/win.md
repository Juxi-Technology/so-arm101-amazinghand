# win

# Phase 1 : Configuration de l'environnement (Windows)

Utilisez **Miniconda** pour créer un environnement Python isolé et installer LeRobot ainsi que le support AmazingHand. Cette page doit être exécutée dans un **ordre strict** ; chaque bloc de code peut être copié dans son intégralité.

> Versions de l'environnement : Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (version personnalisée de ce dépôt)

---

## Étape 1 : Installer Miniconda

**Installation en ligne de commande** (PowerShell, recommandé) — pour un réseau en Chine continentale, utilisez le miroir de Tsinghua :

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

Après avoir rouvert PowerShell, vérifiez :

```PowerShell
conda --version
```

> **Installation graphique** (facultative) : téléchargez le programme d'installation depuis le site officiel https://repo\.anaconda\.com/miniconda/Miniconda3\-latest\-Windows\-x86\_64\.exe, lancez-le par double-clic et cochez **"Add to PATH"**.

> Si la commande `conda` est introuvable, utilisez **Anaconda Prompt** (menu Démarrer) à la place de PowerShell.

---

## Étape 2 : Configurer un miroir conda (réseau Chine continentale)

**Videz d'abord les canaux par défaut, puis ajoutez le miroir de Tsinghua** (une nouvelle installation de Miniconda inclut par défaut le canal officiel `repo.anaconda.com`, ce qui déclenche une vérification des ToS et ralentit les téléchargements) :

```PowerShell
conda config --remove-key channels
```

```PowerShell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> Le canal `pkgs/free` a été retiré (404), ne l'ajoutez pas. Si votre réseau n'est pas restreint, vous pouvez ignorer cette étape.

---

## Étape 3 : Créer l'environnement virtuel

```PowerShell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```PowerShell
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Attendu : `Python 3.12.x` \+ `64 bit`. Si `conda activate` n'affiche pas le préfixe `(lerobot)`, voir le dépannage en fin de document.

---

## Étape 4 : Installer ffmpeg (nécessaire pour le décodage vidéo)

LeRobot dépend de ffmpeg pour l'enregistrement et la relecture des données vidéo :

```PowerShell
conda install ffmpeg -c conda-forge -y
```

> Si le réseau est lent, vous pouvez utiliser le canal conda\-forge de Tsinghua déjà configuré. Ne pas l'installer provoquera des erreurs lors de l'enregistrement des données ou de la lecture des vidéos.

---

## Étape 5 : Installer les dépendances du projet

```PowerShell
cd D:\Project\lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` inclut : `feetech-servo-sdk` (moteurs du bras), `rustypot` (moteurs de la main), `pygame` (GUI de calibration), `pyserial` (port série).

> Si pip est lent, configurez d'abord un miroir :

```PowerShell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Étape 6 : Vérifier l'environnement

```PowerShell
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> Doit afficher `all OK` et `usage: lerobot-calibrate-amazing-hand ...`.

---

## Étape 7 : Vérifier les ports série

```PowerShell
lerobot-find-port
```

Dans le Gestionnaire de périphériques → Ports \(COM et LPT\), vérifiez les numéros de COM des trois équipements (exemple `COM54`/`COM58`/`COM11`, **à remplacer par vos valeurs réelles**). Les numéros de COM changent après un débranchement/rebranchement ; relancez la commande pour confirmer.

---

Terminé → Phase 2 : Calibration

---

## Dépannage

|Symptôme|Solution|
|---|---|
|`conda` n'est pas reconnu comme commande|Rouvrir le terminal / Anaconda Prompt / `conda init powershell`|
|Erreur ToS (repo\.anaconda\.com)|Étape 2 : vider les channels et ne garder que le miroir de Tsinghua ; ou `conda tos accept ...`|
|`pkgs/free` 404|Ce canal a été retiré, ne l'ajoutez pas|
|`conda activate` sans préfixe|Problème de stratégie d'exécution, voir ci-dessous|
|Dépendances non installables/lentes|Configurer un miroir pip (voir l'astuce de l'étape 5)|

**conda activate sans le ****`(lerobot)`**** préfixe** (fréquent sous Windows) :

```PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "D:\Software\Miniconda3\shell\condabin\conda-hook.ps1"
conda activate lerobot
```

> Remplacez `D:\Software\Miniconda3` par le chemin d'installation de votre Miniconda.

