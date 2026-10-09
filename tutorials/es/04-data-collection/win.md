# win

# Fase 4: Recolección de datos (Windows)

En esta fase se graba el conjunto de datos de teleoperación: bajo control manual se recopilan muestras de “ángulo de articulación \+ imagen de cámara” para el entrenamiento posterior. La calidad del conjunto de datos determina directamente el efecto de la política; **la operación debe ser normalizada y coherente**. En esta fase **todo el proceso de grabación es local, sin necesidad de iniciar sesión en HF**.

---

## Requisitos previos

- Haber completado la Fase 3: Teleoperación y verificado que la dirección es correcta

- Cámaras conectadas y con el índice registrado (`lerobot-find-cameras`)

- Ruta de almacenamiento local del conjunto de datos ya definida (en este documento se usa el ejemplo `D:\lerobot_data`, personalizable)

---

## Paso 1: Confirmar el índice de la cámara

```PowerShell
lerobot-find-cameras
```

Registra el número de cada cámara. Por ejemplo:

- Número 0: cámara de muñeca (wrist)

- Número 1: cámara superior (top)

> **⚠️ Nota (índice de la cámara)**: `index_or_path` es el índice de la cámara (0/1/2\.\.\.) o la ruta del flujo de vídeo. La numeración varía según la computadora; confírmalo siempre primero.

---

## Paso 2: Grabar el conjunto de datos (guardado local, sin necesidad de iniciar sesión)

```PowerShell
lerobot-record --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data --dataset.push_to_hub=false --dataset.num_episodes=20 --dataset.single_task="Pick up the cube with the dexterous hand" --display_data=true
```

> Sustituye `<follower_arm_com>` / `<hand_com>` / `<leader_arm_com>` por los números COM reales; y `index_or_path` de las cámaras por el índice de tus cámaras.

> **💡 Descripción**:

- `--dataset.root=D:\lerobot_data`: el conjunto de datos se guarda en la **ruta local** indicada, **sin necesidad de iniciar sesión en HF** (si no se especifica, se guarda por defecto en `%USERPROFILE%\.cache\huggingface\lerobot\datasets\...`).

- `--dataset.push_to_hub=false`: **desactiva la subida** (por defecto intenta enviarlo a HF y requiere iniciar sesión). Solo se cambia a `true` cuando se necesita compartir el conjunto de datos.

- `--dataset.repo_id=soarm_amazing_hand_pick`: nombre del conjunto de datos; al entrenar se referencia con **el mismo nombre**.

- `--display_data=true` requiere rerun (si no está instalado, `pip install "rerun-sdk>=0.24.0,<0.34.0"`); también se puede quitar este parámetro (la grabación no se ve afectada).

---

## Descripción de parámetros

|Parámetro|Descripción|
|---|---|
|`--robot.cameras`|Configuración de las cámaras. `index_or_path` es el índice de la cámara; `width/height/fps` son **obligatorios**|
|`--dataset.repo_id`|Nombre del conjunto de datos (para identificación local)|
|`--dataset.root`|Ruta de almacenamiento local del conjunto de datos. **Obligatorio para grabación puramente local**, para evitar una ruta predeterminada incontrolable|
|`--dataset.push_to_hub`|`false`=solo local (recomendado por defecto); `true`=enviar a HF (requiere iniciar sesión)|
|`--dataset.num_episodes`|Número de rondas de grabación (episode)|
|`--dataset.episode_time_s`|**Duración máxima de grabación por ronda en segundos** (por defecto 60). Si la tarea termina antes, se puede pulsar Enter para finalizar antes; al superarlo, la ronda termina automáticamente|
|`--dataset.single_task`|Descripción de la tarea, se escribe en los metadatos del conjunto de datos|
|`--display_data=true`|Muestra la imagen de grabación en tiempo real (opcional)|

---

## Normas de operación durante la grabación

**Flujo de cada ronda (episode)**:

1. Lleva el brazo robótico \+ la mano a la **posición inicial**

2. Pulsa Enter en el terminal para empezar a grabar

3. Opera el brazo maestro para ejecutar la tarea (por ejemplo, agarrar el cubo); **los movimientos deben ser lentos y coherentes**

4. Al terminar la tarea, pulsa Enter para finalizar la ronda (**si no se pulsa, se graban como máximo 60 segundos**, controlado por `--dataset.episode_time_s`; al llegar al tiempo, termina automáticamente)

5. Repite hasta alcanzar `num_episodes`

> **⚠️ Nota 1 (posición inicial coherente)**: empieza cada ronda desde la **misma posición inicial** para evitar que la distribución de los datos se vuelva caótica. Se recomienda fijar una postura de reposición.

> **⚠️ Nota 2 (coherencia de los movimientos)**: usa trayectorias de operación similares para la misma tarea (ángulo de aproximación, posición de agarre, velocidad); la política aprenderá más rápido y de forma más estable.

> **⚠️ Nota 3 (calidad de la grabación)**: es mejor grabar menos rondas de alta calidad que una gran cantidad de muestras caóticas. 20 rondas es el punto de partida de ACT; para tareas complejas se recomiendan 30\-50 rondas.

> **⚠️ Nota 4 (tiempo real de la cámara)**: durante la grabación evita tapar la cámara y cambios de luz intensa; la coherencia de las imágenes afecta a la generalización.

---

## Almacenamiento de los datos

- **Grabación local**: los datos se guardan en el directorio indicado por `--dataset.root` (ejemplo `D:\lerobot_data\soarm_amazing_hand_pick`).

- **Referencia para el entrenamiento**: al entrenar basta con usar **el mismo ****`--dataset.repo_id`**** \+ ****`--dataset.root`**, sin necesidad de mover los archivos manualmente:

```PowerShell
lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data ...
```

- **Escenario con inicio de sesión en HF** (opcional): cuando se necesita compartir el conjunto de datos en la nube, se cambia a `--dataset.push_to_hub=true` (requiere `huggingface-cli login`). Para entrenar solo en local **no es necesario**.

> **⚠️ Nota (local vs nube)**: el tutorial es local de principio a fin por defecto; `--dataset.push_to_hub=false` garantiza que no se active el inicio de sesión en HF. Solo se añade `true` si se quiere compartir el conjunto de datos.

---

## Paso 3: Verificación por reproducción (opcional pero recomendada)

Una vez finalizada la grabación, se puede usar `lerobot-replay` para reproducir una ronda de datos y verificar la **calidad de los datos \+ si el registro de movimientos del robot es correcto**. Durante la reproducción, el robot repite automáticamente los movimientos de esa ronda (incluida la apertura/cierre de la mano).

```PowerShell
lerobot-replay `
  --robot.type=so101_amazing_hand `
  --robot.port=<follower-port> `
  --robot.hand_port=<hand-port> `
  --robot.id=amazing_hand_follower `
  --dataset.repo_id=soarm_amazing_hand_pick `
  --dataset.root=D:\lerobot_data `
  --dataset.episode=0
```

> Sustituye `<follower_arm_com>` / `<hand_com>` por los números COM reales; `--dataset.episode` es el número de la ronda que se quiere reproducir (**empieza en 0**; si se grabaron 20 rondas, va de `0`\~`19`).

> **💡 Descripción**: antes de reproducir, lleva el brazo esclavo \+ la mano **a la posición inicial** para evitar conflictos de movimiento; durante la reproducción el robot se moverá por sí solo, **no intervengas manualmente**. Si los movimientos de la reproducción difieren claramente de los de la grabación, significa que la calidad de los datos tiene problemas; se recomienda volver a grabar esa ronda.

---

Tras completar esta fase, pasa a la Fase 5: Entrenamiento del modelo.

---

## Solución de problemas

|Síntoma|Causa|Solución|
|---|---|---|
|No se encuentra la cámara|Índice incorrecto/falta el controlador|Confírmalo con `lerobot-find-cameras`; instala OpenCV/el controlador de la cámara|
|Grabación interrumpida|Tiempo de espera del puerto serie|Confirma que los puertos serie de los tres dispositivos no están ocupados y reintenta|
|Imagen totalmente negra/con artefactos|Configuración de la cámara incorrecta|Comprueba `index_or_path`/`fps`|
|Conjunto de datos vacío|No se grabó correctamente|Confirma que en cada ronda se pulsa Enter para empezar/terminar|

