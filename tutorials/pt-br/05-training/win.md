# win

# Etapa 5: Treinamento do modelo (Windows)

Esta etapa usa o conjunto de dados coletado para treinar a política (ACT e outras) e produzir um modelo implantável. O treinamento é a etapa mais demorada; **recomenda-se usar uma GPU NVIDIA**.

---

## Pré-requisitos

- Etapa 4: Coleta de dados concluída

- GPU NVIDIA (recomendada), driver CUDA

- Conjunto de dados gravado (visível no cache local)

---

## Passo 1: Confirmar o ambiente de GPU

```PowerShell
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**Saída esperada**: `CUDA: True | GPU: <your_gpu_name>`

> **⚠️ Nota (torch com CUDA)**: se `CUDA: False`, significa que está instalada a versão CPU do torch. É necessário reinstalar a versão CUDA:

```PowerShell
# Fonte oficial (rede no exterior)
pip install torch --index-url https://download.pytorch.org/whl/cu128

# Em redes da China Continental, prefira o espelho Aliyun
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
```

> Ou treine com CPU (`--policy.device=cpu`, mas bem mais lento; para tarefas complexas não é viável).

---

## Passo 2: Treinar

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

> **💡 Nota**: `--dataset.repo_id` e `--dataset.root` devem ser **exatamente iguais** aos usados na gravação da Etapa 4 (`repo_id=soarm_amazing_hand_pick`, `root=D:\lerobot_data`); assim é possível ler o conjunto de dados local, sem necessidade de login no HF.

---

## Descrição dos parâmetros

|Parâmetro|Descrição|
|---|---|
|`--dataset.repo_id`|Nome do conjunto de dados (igual ao da gravação)|
|`--dataset.root`|Caminho local do conjunto de dados (igual ao da gravação)|
|`--policy.type`|Tipo de política; `act` é a escolha mais comum|
|`--output_dir`|Diretório de saída do treinamento (checkpoints, logs)|
|`--job_name`|Nome da tarefa (para distinguir nos logs)|
|`--policy.device`|`cuda` (GPU) ou `cpu`|
|`--wandb.enable`|Registro de pesos; `false` desativa (sem necessidade de conta wandb)|
|`--policy.push_to_hub`|Se deve enviar o modelo para o HF; `false` significa apenas local|
|`--steps`|Número de passos de treinamento|

---

## Explicação do processo de treinamento

- **checkpoints**: salvos automaticamente a cada passo em `outputs/train/soarm_amazing_hand_pick/checkpoints/`

- **Logs**: o terminal exibe métricas como o loss em tempo real

- **Duração**: 60000 passos costumam levar algumas horas numa GPU de consumo (depende da placa gráfica)

> **⚠️ Nota 1 (ajuste do número de passos)**: `--steps=60000` é o valor típico para o ACT. Tarefas simples podem ser reduzidas para 30000; tarefas complexas podem ser aumentadas para 100000\+. Observe a convergência do loss.

> **⚠️ Nota 2 (retomar após interrupção)**: após uma interrupção, executar novamente o **comando com os mesmos parâmetros** continua a partir do último checkpoint.

> **⚠️ Nota 3 (wandb)**: para visualizar a curva de loss, ative `--wandb.enable=true` (requer `wandb login`). Desativado por padrão.

> **⚠️ Nota 4 (memória/VRAM)**: se a memória de vídeo for insuficiente, adicione `--policy.batch_size=8` (reduz o tamanho do lote); se a memória para decodificação de vídeo for insuficiente, reduza `width/height`.

---

Depois de concluir esta etapa, avance para a Etapa 6: Implantação e avaliação.

---

## Resolução de problemas

|Sintoma|Causa|Solução|
|---|---|---|
|`CUDA: False`|torch versão CPU|Reinstalar o torch versão CUDA|
|Memória de vídeo insuficiente (OOM)|Tamanho do lote muito grande|`--policy.batch_size=8` ou menos|
|Conjunto de dados não encontrado|repo\_id/root inconsistentes|Confirme que são exatamente iguais a `--dataset.repo_id` e `--dataset.root` da gravação|
|Treinamento lento|Treinamento em CPU|Use GPU; ou reduza `--steps`|
|Erro do `wandb`|Não autenticado|`--wandb.enable=false` ou `wandb login`|

