# linux

# Fase 6: Despliegue y evaluación (Linux)

En esta fase se carga la política ya entrenada para que el robot **ejecute la tarea de forma autónoma** y se graba un vídeo de evaluación para verificar el efecto. Es el cierre de todo el flujo y también la clave para comprobar los resultados del entrenamiento.

---

## Requisitos previos

- Haber completado la Fase 5: Entrenamiento del modelo

- Salida del entrenamiento `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/`

- Índice de la cámara registrado

---

## Paso 1: Confirmar los archivos del modelo

```Bash
ls outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model
```

Debe contener archivos del modelo como `model.safetensors`.

> **⚠️ Nota (ruta del modelo)**: `--policy.path` debe apuntar al directorio `pretrained_model` (que contiene la configuración \+ los pesos), no al directorio raíz del checkpoint.

---

## Paso 2: Despliegue y evaluación

```Bash
lerobot-record \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' \
  --policy.path=outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model \
  --dataset.repo_id=soarm_amazing_hand_pick_eval \
  --dataset.root=~/lerobot_data \
  --dataset.push_to_hub=false \
  --dataset.num_episodes=10 \
  --dataset.single_task="Pick up the cube with the dexterous hand" \
  --display_data=true
```

> Sustituye `<follower_arm_port>` / `<hand_port>` por las rutas reales; y `index_or_path` de las cámaras por el índice de tus cámaras.

> **💡 Descripción**: se usa `lerobot-record` pero **sin añadir ****`--teleop.type`**; la política controlará el robot de forma autónoma (en lugar de la teleoperación manual). Los datos se guardan como conjunto de evaluación. `--dataset.root` / `--dataset.push_to_hub=false` son iguales que en la fase 4; el guardado puramente local no requiere iniciar sesión en HF.

---

## Operación de evaluación

1. Lleva el robot \+ la mano a la **posición inicial**

2. Pulsa Enter para empezar: la política ejecuta la tarea de forma autónoma

3. Observa **si el agarre se realiza con éxito** (al terminar cada ronda, pulsa Enter para continuar)

4. Repite `num_episodes` rondas

**Métrica de evaluación**: tasa de éxito = rondas exitosas / rondas totales

> **⚠️ Nota 1 (coherencia de la reposición)**: empieza cada ronda desde la **misma posición inicial**; de lo contrario la política fallará en la generalización y la tasa de éxito saldrá artificialmente baja.

> **⚠️ Nota 2 (seguridad)**: en la primera ejecución autónoma se recomienda observar **sujetando el robot/velocidad lenta** para confirmar que los movimientos de la política son razonables. La política puede realizar movimientos inesperados.

> **⚠️ Nota 3 (tasa de éxito esperada)**: ACT suele alcanzar una tasa de éxito del 50\-80% con 20 rondas de datos. Si es inferior a lo esperado, vuelve atrás para grabar más datos o ajusta el número de pasos de entrenamiento.

> **⚠️ Nota 4 (entorno sin cabeza)**: `--display_data=true` requiere un servidor de visualización; sin GUI, quita este parámetro (la evaluación continúa, solo que no se muestra en tiempo real).

---

## Optimización iterativa

Si la tasa de éxito de la evaluación no es satisfactoria, ajusta por orden de prioridad:

|Prioridad|Elemento de optimización|Operación|
|---|---|---|
|1|Grabar datos de alta calidad adicionales|Vuelve a la Fase 4 y graba 20\-30 rondas más de datos más coherentes|
|2|Aumentar el número de pasos de entrenamiento|Vuelve a la Fase 5, `--steps=100000`|
|3|Comprobar la coherencia de la posición inicial|Reponer estrictamente en cada ronda durante la evaluación|
|4|Ajustar la descripción de la tarea|Asegúrate de que `single_task` coincide con la tarea|

---

Con esto se completa el **ciclo completo** de SO\-ARM101 \+ AmazingHand: calibración → teleoperación → recolección → entrenamiento → despliegue.

---

## Solución de problemas

|Síntoma|Causa|Solución|
|---|---|---|
|Fallo al cargar el modelo|Ruta incorrecta/incompleta|Confirma que `--policy.path` apunta al directorio `pretrained_model`|
|La política no se mueve|Error de cámara/observación|Confirma que el índice de la cámara es igual que al entrenar; comprueba los permisos de `/dev/video*`|
|La política se mueve de forma errática|Posición inicial incoherente/datos deficientes|Reponer estrictamente; grabar datos adicionales|
|El rendimiento no coincide con el del entrenamiento|Diferencias del entorno|Confirma que la cámara, la iluminación y la posición de los objetos coinciden con los de la grabación|

