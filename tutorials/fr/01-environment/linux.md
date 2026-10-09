# linux

# Phase 1 : Configuration de l'environnement (Linux)

Utilisez **Miniforge** pour créer un environnement Python isolé et installer LeRobot ainsi que le support AmazingHand. Cette page doit être exécutée dans un **ordre strict** ; chaque bloc de code peut être copié dans son intégralité.

> Versions de l'environnement : Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (version personnalisée de ce dépôt) · Ubuntu 20\.04/22\.04 recommandé

---

## Étape 1 : Installer Miniforge

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

> Adresse officielle (réseau hors Chine) : `https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh`

---

## Étape 2 : Configurer un miroir conda (réseau Chine continentale)

```Bash
conda config --remove-key channels
```

```Bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> Le canal `pkgs/free` a été retiré (404), ne l'ajoutez pas. Si votre réseau n'est pas restreint, vous pouvez ignorer cette étape.

---

## Étape 3 : Installer les outils de compilation (nécessaire sur un système neuf)

Une installation récente d'Ubuntu peut manquer d'outils de compilation comme `gcc`, nécessaires pour installer des paquets tels que `evdev` :

```Bash
sudo apt update
sudo apt install -y build-essential
```

---

## Étape 4 : Créer l'environnement virtuel

```Bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```Bash
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Attendu : `Python 3.12.x` \+ `64 bit`.

---

## Étape 5 : Installer ffmpeg (nécessaire pour le décodage vidéo)

LeRobot dépend de ffmpeg pour l'enregistrement et la relecture des données vidéo :

```Bash
conda install ffmpeg -c conda-forge -y
```

---

## Étape 6 : Installer les dépendances du projet

```Bash
cd ~/lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` inclut : `feetech-servo-sdk` (moteurs du bras), `rustypot` (moteurs de la main), `pygame` (GUI de calibration), `pyserial` (port série).

> Si pip est lent, configurez d'abord un miroir :

```Bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Étape 7 : Configurer les permissions du port série

```Bash
sudo chmod 666 /dev/ttyACM*
```

> Solution permanente (règle udev, pour la puce CP210x, VID `10c4`) :

```Bash
sudo tee /etc/udev/rules.d/99-servo.rules << 'EOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## Étape 8 : Vérifier l'environnement

```Bash
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> Doit afficher `all OK` et `usage: lerobot-calibrate-amazing-hand ...`.

---

## Étape 9 : Vérifier les ports série

```Bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

Ou `lerobot-find-port`. Vérifiez les chemins des trois équipements (exemple `/dev/ttyACM0`/`/dev/ttyACM1`/`/dev/ttyACM2`, **à remplacer par vos valeurs réelles**).

---

Terminé → Phase 2 : Calibration

---

## Dépannage

|Symptôme|Solution|
|---|---|
|Commande `conda` introuvable|`source ~/.bashrc` ou rouvrir le terminal après `conda init`|
|`pkgs/free` 404|Ce canal a été retiré, ne l'ajoutez pas|
|Port série `Permission denied`|Étape 7 `sudo chmod 666`|
|Dépendances non installables/lentes|Configurer un miroir pip (voir l'astuce de l'étape 6)|
|Erreur de compilation `evdev` à l'installation|Étape 3 `sudo apt install build-essential`|
|Vérification CUDA de l'entraînement GPU `False`|Voir le document d'entraînement de la phase 5|

