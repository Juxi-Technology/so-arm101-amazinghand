# win

# Fase 2: Calibración (Windows)

En esta fase se calibran los tres dispositivos: el brazo maestro, el brazo esclavo y la mano AmazingHand. La calibración es el requisito previo para la correcta teleoperación; **es obligatorio completar esta fase para pasar a la teleoperación**.

> **Orden de calibración**: brazo maestro → brazo esclavo\+mano → ángulo de la mano. Cada paso requiere **interacción en el terminal** (operación física \+ pulsación de teclas).

> **⚠️ Recordatorio general**: los parámetros de puerto serie de los comandos de esta página son **marcadores de posición de ejemplo**; debes reemplazarlos por los números COM reales de tu máquina (consulta los puertos serie registrados en la fase 1).

---

## Requisitos previos

- Haber completado la Fase 1: Preparación del entorno

- Entorno conda `lerobot` activado

```Plain Text
# Activar el entorno
conda activate lerobot

# Entrar en lerobot
cd ../lerobot
```

- Puertos serie de los tres dispositivos registrados

- Dispositivos encendidos y con alimentación independiente

---

## Paso 1: Calibrar el brazo maestro

```PowerShell
lerobot-calibrate --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Sustituye `<leader_arm_com>` por el número COM real de tu máquina (ejemplo `COM54`).

**Pasos de interacción**:

1. Lleva **todas las articulaciones del brazo maestro a la posición intermedia** y pulsa Enter

2. **Empuja cada articulación sucesivamente hasta el recorrido máximo/mínimo** y pulsa Enter al terminar

**Verificación**: el archivo de calibración se guarda automáticamente en
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\teleoperators\so_leader\amazing_hand_leader.json`

> **⚠️ Nota 1 (la pinza debe calibrarse)**: el rango del servomotor de la pinza n.º 6 se usará como base de normalización de `gripper.pos` (0\~100). La pinza debe llevarse de completamente abierta a completamente cerrada y calibrarse correctamente; de lo contrario, la proporción de apertura/cierre posterior de la mano se distorsionará.

> **⚠️ Nota 2 (giro libre)**: durante la calibración el brazo robótico debe poder girar libremente; asegúrate de que los servomotores estén sin carga.

> **⚠️ Nota 3 (ubicación del archivo de calibración)**: en Windows la ruta es el directorio de usuario `%USERPROFILE%\.cache\huggingface\lerobot\calibration\`.

---

## Paso 2: Calibrar el brazo esclavo (conectando la mano al mismo tiempo)

```PowerShell
lerobot-calibrate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower
```

> Sustituye `<follower_arm_com>` / `<hand_com>` por los números COM reales (ejemplo `COM58` / `COM11`).

**Pasos de interacción**:

1. Lleva las **5 articulaciones** del brazo esclavo (sin la n.º 6) a la posición intermedia y pulsa Enter

2. Recorre todo el recorrido de cada articulación y pulsa Enter

**Verificación**: el archivo de calibración se guarda en
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\amazing_hand_follower.json`

> **⚠️ Nota 1 (el par de la mano se activa automáticamente)**: al conectar, este comando **activa automáticamente el par de los 8 servomotores de la mano** (el registro muestra `enabling AmazingHand torque`); al finalizar la calibración la mano se abre, lo cual es normal.

> **⚠️ Nota 2 (no aparece la GUI de la mano)**: el ángulo de la mano **no** usa el `RangeFinderGUI` de lerobot; la calibración del brazo esclavo termina y ya está. Para el ángulo de la mano se usa la herramienta dedicada del paso 3.

> **⚠️ Nota 3 (ocupación del puerto serie)**: este paso ocupa el puerto serie de la mano. **No** ejecutes al mismo tiempo otros procesos que ocupen ese puerto serie.

---

## Paso 3: Calibrar el ángulo de la mano \+ la dirección de la pinza (GUI dedicada)

```PowerShell
lerobot-calibrate-amazing-hand --hand_port <hand-port> --leader_port <leader-port>
```

> Sustituye `<hand_com>` / `<leader_arm_com>` por los números COM reales (ejemplo `COM11` / `COM54`). `--leader_port` se usa para calibrar de forma sincronizada la **dirección de la pinza** (véase más abajo).

**Operación de la GUI**:

1. Arrastra los deslizadores de los 4 dedos (index/middle/ring/thumb) para que la mano quede **completamente abierta** y haz clic en **`Save Open`**

2. Arrastra los deslizadores para que la mano quede **completamente cerrada en puño** y haz clic en **`Save Close`**

3. **Abre la pinza del brazo maestro** y haz clic en **`Capture Open`** (la GUI muestra `gripper.pos` en tiempo real; al abrir debe acercarse a 100)

4. **Pinza la pinza del brazo maestro** y haz clic en **`Capture Close`** (al pinzar debe acercarse a 0)

5. **Guardado automático**: una vez establecidos los cuatro valores anteriores, en la parte superior de la ventana aparece un banner verde `AUTO-SAVED to ...\hand_angles.json` y el terminal imprime la ruta de forma sincronizada

6. Cierra la ventana (la mano libera el par automáticamente)

**Verificación**: el ángulo y el mapeo de la pinza se guardan en
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\hand_angles.json`

> **⚠️ Nota 1 (calibración obligatoria)**: **es obligatorio ejecutar este paso en cada computadora nueva y con cada mano**. Los ángulos del config son los valores predeterminados genéricos oficiales de AmazingHand y solo sirven como respaldo; si existe `hand_angles.json`, se cargan con prioridad tus valores medidos. No calibrar puede provocar errores de dirección/rango de apertura y cierre.

> **⚠️ Nota 2 (carga automática)**: el robot lee `hand_angles.json` (que contiene `gripper_open_pos`/`gripper_close_pos`) en cada arranque y sobrescribe los valores predeterminados del config, **sin necesidad de modificar el código**. La dirección de la pinza varía según el brazo maestro; basta con calibrar una vez.

> **⚠️ Nota 3 (semántica de los deslizadores)**: al mover el deslizador hacia `+`, ese dedo mueve m1 hacia `+angle` y m2 hacia `-angle` (espejo). Juzga la apertura/cierre por la **postura real de la mano**, sin fijarte en el valor numérico del ángulo.

> **⚠️ Nota 4 (calibración precisa)**: al calibrar “completamente abierta” no te excedas (dedos torcidos/separados) y al calibrar “completamente cerrada en puño” no aprietes en exceso (los servomotores quedarían bajo presión continua). De lo contrario, durante la teleoperación la apertura/cierre se pasará de la cuenta.

> **⚠️ Nota 5 (orden de Capture)**: `Capture Open` / `Capture Close` corresponden a la apertura/cierre de la **pinza del brazo maestro**, no a los dedos de la mano. Si la dirección de apertura de la mano sale invertida, lo más probable es que se haya calibrado al revés aquí o que el ángulo de la mano esté invertido; basta con recalibrar.

> **⚠️ Nota 6 (la GUI no abre)**: confirma que `pygame` está instalado (incluido en el extra `amazinghand`). Si aun así no abre, comprueba si hay un entorno de escritorio gráfico.

---

## Recalibración

Cuando solo se necesite recalibrar una parte:

- **Recalibrar solo la mano** → ejecuta únicamente el paso 3

- **Recalibrar solo el brazo esclavo** → ejecuta únicamente el paso 2 (activa el par de la mano de paso)

- **Recalibrar todo** → pasos 1 → 2 → 3

> **⚠️ Nota**: los pasos 2 y 3 **no pueden ejecutarse a la vez** (ambos ocupan el puerto serie de la mano).

---

Tras completar esta fase, pasa a la Fase 3: Teleoperación.

---

## Solución de problemas

|Síntoma|Causa|Solución|
|---|---|---|
|La calibración del brazo maestro informa del error de modelo 2307|Bus del brazo contaminado/conflicto de puerto serie<br>|Confirma que no se conecta al mismo tiempo el puerto serie de la mano; en este proyecto la mano usa rustypot y se ha evitado|
|La calibración de la mano no muestra ninguna GUI|Se usó un comando incorrecto|Hay que usar `lerobot-calibrate-amazing-hand` (no `lerobot-calibrate`)|
|El controlador de la mano informa `Operation timed out`|Puerto serie ocupado/sincronización|Confirma que el puerto serie de la mano no está ocupado y reintenta|
|No se encuentra el archivo de calibración|Ruta incorrecta<br>|Comprueba `%USERPROFILE%\.cache\huggingface\lerobot\calibration\`|
|El puerto serie no abre|Número COM incorrecto|Vuelve a confirmarlo con `lerobot-find-port`|

