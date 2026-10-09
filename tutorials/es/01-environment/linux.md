# linux

# Fase 1: Preparación del entorno (Linux)

Usa **Miniforge** para crear un entorno de Python independiente e instalar LeRobot y el soporte de AmazingHand. Esta página se ejecuta en **orden estricto**; cada bloque de código puede copiarse completo.

> Versiones del entorno: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (versión personalizada de este repositorio) · Se recomienda Ubuntu 20\.04/22\.04

---

## Paso 1: Instalar Miniforge

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

> Dirección oficial (redes en el extranjero): `https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh`

---

## Paso 2: Configurar el canal nacional de conda (redes de China continental)

```Bash
conda config --remove-key channels
```

```Bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` ya no está disponible (404), no lo añadas. Si no tienes restricciones de red, puedes omitir este paso.

---

## Paso 3: Instalar las herramientas de compilación (necesario en sistemas nuevos)

Una instalación nueva de Ubuntu puede carecer de herramientas de compilación como `gcc`; al instalar paquetes como `evdev` se necesitan:

```Bash
sudo apt update
sudo apt install -y build-essential
```

---

## Paso 4: Crear el entorno virtual

```Bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```Bash
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Se espera `Python 3.12.x` \+ `64 bit`.

---

## Paso 5: Instalar ffmpeg (necesario para la decodificación de vídeo)

La grabación/reproducción de datos de vídeo de LeRobot depende de ffmpeg:

```Bash
conda install ffmpeg -c conda-forge -y
```

---

## Paso 6: Instalar las dependencias del proyecto

```Bash
cd ~/lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` incluye: `feetech-servo-sdk` (motores del brazo), `rustypot` (motores de la mano), `pygame` (GUI de calibración), `pyserial` (puerto serie).

> Si pip va lento, configura primero el canal nacional:

```Bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Paso 7: Configurar los permisos del puerto serie

```Bash
sudo chmod 666 /dev/ttyACM*
```

> Solución permanente (reglas udev, para el chip CP210x, VID `10c4`):

```Bash
sudo tee /etc/udev/rules.d/99-servo.rules << 'EOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## Paso 8: Verificar el entorno

```Bash
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> Debe mostrar `all OK` y `usage: lerobot-calibrate-amazing-hand ...`.

---

## Paso 9: Confirmar el puerto serie

```Bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

O `lerobot-find-port`. Confirma las rutas de los tres dispositivos (ejemplo `/dev/ttyACM0`/`/dev/ttyACM1`/`/dev/ttyACM2`, **debes reemplazarlas por tus valores reales**).

---

Completado → Fase 2: Calibración

---

## Solución de problemas

|Síntoma|Solución|
|---|---|
|Comando `conda` no encontrado|`source ~/.bashrc` o reabrir el terminal tras `conda init`|
|`pkgs/free` 404|Ese canal ya no está disponible, no lo añadas|
|Puerto serie `Permission denied`|Paso 7 `sudo chmod 666`|
|Dependencias no se instalan / van lentas|Configura el canal nacional de pip (indicado en el paso 6)|
|Error de compilación de `evdev` al instalar|Paso 3 `sudo apt install build-essential`|
|Entrenamiento con GPU, comprobación de CUDA `False`|Consulta el documento de entrenamiento de la fase 5|

