# win

# Fase 3: Teleoperación (Windows)

En esta fase se inicia el bucle cerrado de teleoperación: el brazo maestro controla el movimiento del brazo esclavo y la pinza controla la apertura/cierre de AmazingHand. Es la fase clave para verificar si todo el sistema funciona correctamente.

---

## Requisitos previos

- Haber completado la Fase 1: Preparación del entorno y la Fase 2: Calibración

- Dispositivos encendidos y puertos serie registrados

---

## Ejecutar la teleoperación

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Sustituye `<follower_arm_com>` / `<hand_com>` / `<leader_arm_com>` por los números COM reales de tu máquina (ejemplo `COM58` / `COM11` / `COM54`).

**Efecto esperado**:

- Las 5 articulaciones del brazo maestro → el brazo esclavo las sigue

- La pinza del brazo maestro → apertura/cierre de AmazingHand (seguimiento proporcional: medio pinzado = medio cierre)

> **💡 Descripción de parámetros**:

- `--robot.type=so101_amazing_hand`: robot combinado de brazo esclavo \+ mano

- `--robot.port`: puerto serie del brazo esclavo

- `--robot.hand_port`: puerto serie de la mano

- `--teleop.type=so101_leader`: teleoperador del brazo maestro

- `--teleop.port`: puerto serie del brazo maestro

---

## Obligatorio en la primera ejecución: verificación de la dirección

Tras el arranque, realiza primero una **prueba de dirección** para confirmar que los dos puntos siguientes son correctos:

|Prueba|Operación|Fenómeno correcto|
|---|---|---|
|Seguimiento del brazo|Gira cada articulación del brazo maestro|El brazo esclavo sigue en la misma dirección|
|Apertura/cierre de la mano|Abre/pinza la pinza del brazo maestro|Pinza abierta → mano abierta; pinza pinzada → mano cerrada|

> **⚠️ Nota (qué hacer si la dirección está invertida)**:

- **Dirección de apertura/cierre de la mano invertida** (al abrir la pinza la mano se cierra): indica que la calibración del ángulo de la mano es imprecisa; vuelve a ejecutar la herramienta de calibración (incluida la calibración de la dirección de la pinza); tras guardar, surte efecto automáticamente, **sin necesidad de modificar archivos manualmente**. Consulta la Fase 2: Calibración.

- **Dirección del mapeo de la pinza invertida** (al abrir la pinza la mano se cierra): igual que arriba; al calibrar, pulsa `[Capture Open]` con la pinza del brazo maestro **abierta** y `[Capture Close]` al **pinzar**; la herramienta registra y guarda automáticamente `gripper_open_pos`/`gripper_close_pos`, que se cargan automáticamente al arrancar.

> Tras modificarlo, **vuelve a ejecutar la teleoperación** para verificar.

---

## Verificación del seguimiento proporcional

Una vez correcta la dirección, verifica la finura de la proporción:

1. Abre la pinza **lentamente** → la mano debe abrirse de forma **suave** (sin saltos)

2. Deja la pinza en el **punto medio** → la mano también debe detenerse en el punto medio

3. Abre y cierra rápido → la mano responde rápido, sin tirones

> **⚠️ Nota (problema histórico de apertura/cierre excesivo de la mano)**: si la mano se cierra cuando la pinza solo está a medio abrir, lo más probable es que las posiciones de “abierta/cerrada en puño” no fueran precisas al calibrar el ángulo de la mano. Vuelve a ejecutar el paso 3 de calibración (GUI del ángulo de la mano) para calibrar posiciones de apertura/cierre más precisas.

---

## Opcional: visualización con cámara

Añade `--robot.cameras` para conectar cámaras y `--display_data=true` para abrir la ventana de visualización de Rerun (muestra en tiempo real la imagen de la cámara \+ el estado de las articulaciones):

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --display_data=true
```

> **💡 Descripción**:

- `index_or_path` es el índice de la cámara; confírmalo primero con `lerobot-find-cameras` (la numeración varía según la máquina).

- `fourcc: "MJPG"` es opcional y puede reducir notablemente el ancho de banda que ocupa la cámara USB (pasa a usar compresión MJPEG); puedes añadirlo si hay tirones.

- Si solo necesitas una cámara, elimina la línea correspondiente (por ejemplo `top`).

> **⚠️ Nota (dependencia de rerun)**: `--display_data=true` requiere el paquete de visualización rerun; si no está instalado, ejecuta:

```PowerShell
pip install "rerun-sdk>=0.24.0,<0.34.0"
```

> Se necesita el ejecutable Rerun Viewer. En Windows, si aparece `Failed to find Rerun Viewer executable`, significa que falta el visor con GUI. **No afecta a la teleoperación**; basta con quitar `--display_data=true`.

---

## Salir

Pulsa `Ctrl+C` para detener. El programa realiza automáticamente:

1. Libera el par de los 8 servomotores de la mano

2. Desconecta los puertos serie del brazo esclavo/brazo maestro

3. Desconecta las cámaras (si las hay)

> **⚠️ Nota**: antes de una salida normal, **no cierres el terminal directamente**, ya que puede quedar el puerto serie ocupado de forma residual. Si tras una salida anómala el puerto serie queda ocupado, vuelve a conectar el USB o reinicia el proceso del terminal.

---

## Solución de problemas

|Síntoma|Causa|Solución|
|---|---|---|
|Dirección de la mano invertida|Ángulo de la mano o mapeo de la pinza invertidos|Consulta “Verificación de la dirección” más arriba; intercambia los ángulos o ajusta el mapeo|
|Apertura/cierre excesivo o insuficiente de la mano|Calibración del ángulo de la mano imprecisa|Recalibrar el ángulo de la mano con la GUI|
|El brazo no sigue|Falta de calibración/puerto serie incorrecto|Confirma que el brazo esclavo está calibrado y que `--robot.port` es correcto|
|Error de rerun|Falta la dependencia de visualización|Quita `--display_data=true`|
|Puerto serie ocupado|Salida anómala anterior|Cierra el proceso que lo ocupa o vuelve a conectar el USB|

