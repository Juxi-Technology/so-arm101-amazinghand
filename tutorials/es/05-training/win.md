# win

# Fase 5: Entrenamiento del modelo (Windows)

En esta fase se usa el conjunto de datos recopilado para entrenar una política (ACT, etc.) y producir un modelo desplegable. El entrenamiento es el paso que más tiempo consume; **se recomienda usar una NVIDIA GPU**.

---

## Requisitos previos

- Haber completado la Fase 4: Recolección de datos

- NVIDIA GPU (recomendada), controlador CUDA

- Conjunto de datos ya grabado (visible en la caché local)

---

## Paso 1: Confirmar el entorno de GPU

```PowerShell
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**Salida esperada**: `CUDA: True | GPU: <your_gpu_name>`

> **⚠️ Nota (CUDA torch)**: si `CUDA: False`, significa que está instalada la versión de torch para CPU. Hay que reinstalar la versión con CUDA:

```PowerShell
# Fuente oficial (redes en el extranjero)
pip install torch --index-url https://download.pytorch.org/whl/cu128

# En China continental, dar prioridad al espejo de Alibaba Cloud
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
```

> O entrena con CPU (`--policy.device=cpu`, pero mucho más lento; no es realista para tareas complejas).

---

## Paso 2: Entrenar

```PowerShell
lerobot-train `
  --dataset.repo_id=soarm_amazing_hand_pick `
  --dataset.root=D:\lerobot_data `
  --policy.type=act `
  --output_dir=outputs/train/soarm_amazing_hand_pick `
  --job_name=soarm_amazing_hand_pick `
  --policy.device=cuda `
  --wandb.enable=false `
  --policy.push_to_hub=false `
  --steps=60000
```

> **💡 Descripción**: `--dataset.repo_id` y `--dataset.root` deben ser **exactamente iguales** a los de la grabación de la fase 4 (`repo_id=soarm_amazing_hand_pick`, `root=D:\lerobot_data`); así se puede leer el conjunto de datos local sin necesidad de iniciar sesión en HF.

---

## Descripción de parámetros

|Parámetro|Descripción|
|---|---|
|`--dataset.repo_id`|Nombre del conjunto de datos (igual que al grabar)|
|`--dataset.root`|Ruta local del conjunto de datos (igual que al grabar)|
|`--policy.type`|Tipo de política; `act` es la elección habitual|
|`--output_dir`|Directorio de salida del entrenamiento (checkpoints, registros)|
|`--job_name`|Nombre de la tarea (para distinguir los registros)|
|`--policy.device`|`cuda` (GPU) o `cpu`|
|`--wandb.enable`|Registro de pesos; `false` lo desactiva (sin necesidad de cuenta de wandb)|
|`--policy.push_to_hub`|Si se envía el modelo a HF; `false` solo local|
|`--steps`|Número de pasos de entrenamiento|

---

## Descripción del proceso de entrenamiento

- **checkpoints**: se guardan automáticamente en `outputs/train/soarm_amazing_hand_pick/checkpoints/` en cada paso

- **Registros**: el terminal muestra en tiempo real métricas como la loss

- **Duración**: 60000 pasos suelen tardar varias horas en una GPU de consumo (depende de la tarjeta gráfica)

> **⚠️ Nota 1 (ajuste del número de pasos)**: `--steps=60000` es el valor típico de ACT. Para tareas simples se puede reducir a 30000 y para tareas complejas aumentar a 100000\+. Observa la convergencia de la loss.

> **⚠️ Nota 2 (reanudar tras una interrupción)**: si se interrumpe, volver a ejecutar **el comando con los mismos parámetros** continuará desde el último checkpoint.

> **⚠️ Nota 3 (wandb)**: si necesitas visualizar la curva de loss, puedes activar `--wandb.enable=true` (requiere `wandb login`). Por defecto está desactivado.

> **⚠️ Nota 4 (memoria/memoria de vídeo)**: si la memoria de vídeo es insuficiente, puedes añadir `--policy.batch_size=8` (reduce el tamaño de lote); si la memoria es insuficiente en la decodificación de vídeo, puedes reducir `width/height`.

---

Tras completar esta fase, pasa a la Fase 6: Despliegue y evaluación.

---

## Solución de problemas

|Síntoma|Causa|Solución|
|---|---|---|
|`CUDA: False`|torch para CPU|Reinstalar la versión de torch con CUDA|
|Memoria de vídeo insuficiente (OOM)|Tamaño de lote demasiado grande|`--policy.batch_size=8` o menos|
|No se encuentra el conjunto de datos|repo\_id/root inconsistentes|Confirma que `--dataset.repo_id` y `--dataset.root` son exactamente iguales a los de la grabación|
|Entrenamiento lento|Entrenamiento con CPU|Usa la GPU; o reduce `--steps`|
|Error de `wandb`|Sin iniciar sesión|`--wandb.enable=false` o `wandb login`|

