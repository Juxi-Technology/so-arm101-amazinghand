# win

# Fase 1: Preparación del entorno (Windows)

Usa **Miniconda** para crear un entorno de Python independiente e instalar LeRobot y el soporte de AmazingHand. Esta página se ejecuta en **orden estricto**; cada bloque de código puede copiarse completo.

> Versiones del entorno: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (versión personalizada de este repositorio)

---

## Paso 1: Instalar Miniconda

**Instalación por línea de comandos** (PowerShell, recomendada): para redes de China continental, usa el espejo de Tsinghua:

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

Reabre PowerShell y verifica:

```PowerShell
conda --version
```

> **Instalación gráfica** (opcional): descarga el paquete de instalación desde el sitio oficial https://repo\.anaconda\.com/miniconda/Miniconda3\-latest\-Windows\-x86\_64\.exe, haz doble clic para instalar y marca **"Add to PATH"**.

> Si no se encuentra el comando `conda`, usa **Anaconda Prompt** (menú Inicio) en lugar de PowerShell.

---

## Paso 2: Configurar el canal nacional de conda (redes de China continental)

**Primero vacía los canales predeterminados y luego añade el espejo de Tsinghua** (la nueva versión de Miniconda incluye por defecto el canal oficial `repo.anaconda.com`, lo que activa la comprobación de ToS y resulta lento):

```PowerShell
conda config --remove-key channels
```

```PowerShell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free` ya no está disponible (404), no lo añadas. Si no tienes restricciones de red, puedes omitir este paso.

---

## Paso 3: Crear el entorno virtual

```PowerShell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```PowerShell
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Se espera `Python 3.12.x` \+ `64 bit`. Si `conda activate` no muestra el prefijo `(lerobot)`, consulta la solución de problemas al final del documento.

---

## Paso 4: Instalar ffmpeg (necesario para la decodificación de vídeo)

La grabación/reproducción de datos de vídeo de LeRobot depende de ffmpeg:

```PowerShell
conda install ffmpeg -c conda-forge -y
```

> Si la red nacional va lenta, puedes usar el canal conda\-forge de Tsinghua ya configurado. No instalarlo provocará errores al grabar datos o reproducir vídeo.

---

## Paso 5: Instalar las dependencias del proyecto

```PowerShell
cd D:\Project\lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` incluye: `feetech-servo-sdk` (motores del brazo), `rustypot` (motores de la mano), `pygame` (GUI de calibración), `pyserial` (puerto serie).

> Si pip va lento, configura primero el canal nacional:

```PowerShell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Paso 6: Verificar el entorno

```PowerShell
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> Debe mostrar `all OK` y `usage: lerobot-calibrate-amazing-hand ...`.

---

## Paso 7: Confirmar el puerto serie

```PowerShell
lerobot-find-port
```

En el Administrador de dispositivos → Puertos \(COM y LPT\) confirma el número COM de los tres dispositivos (ejemplo `COM54`/`COM58`/`COM11`; **debes reemplazarlos por tus valores reales**). El número COM cambia al desconectar y volver a conectar; vuelve a ejecutar la confirmación.

---

Completado → Fase 2: Calibración

---

## Solución de problemas

|Síntoma|Solución|
|---|---|
|`conda` no es un comando|Reabre el terminal / Anaconda Prompt / `conda init powershell`|
|Error de ToS (repo\.anaconda\.com)|Paso 2: vacía los channels y deja solo el canal de Tsinghua; o `conda tos accept ...`|
|`pkgs/free` 404|Ese canal ya no está disponible, no lo añadas|
|`conda activate` sin prefijo|Problema de la política de ejecución, consulta más abajo|
|Dependencias no se instalan / van lentas|Configura el canal nacional de pip (indicado en el paso 5)|

**`conda activate` sin el prefijo ****`(lerobot)`** (habitual en Windows):

```PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "D:\Software\Miniconda3\shell\condabin\conda-hook.ps1"
conda activate lerobot
```

> Sustituye `D:\Software\Miniconda3` por la ruta de instalación de tu Miniconda.

