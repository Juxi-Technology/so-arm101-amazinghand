# linux

# Etapa 5: Treino do modelo (Linux)

Esta etapa usa o conjunto de dados recolhido para treinar a política (ACT e outras) e produzir um modelo implementável. **O Linux é o melhor ambiente para treino em GPU** — as dependências do torch CUDA são resolvidas automaticamente, sem configuração manual.

---

## Pré-requisitos

- Etapa 4: Recolha de dados concluída

- GPU NVIDIA (recomendada), controlador CUDA (verificável com `nvidia-smi`)

- Conjunto de dados gravado (visível na cache local)

---

## Passo 1: Confirmar o ambiente de GPU

```Bash
# Confirmar o controlador CUDA
nvidia-smi

# Confirmar que o torch pode usar CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**Saída esperada**: `CUDA: True | GPU: <your_gpu_name>`

> **⚠️ Nota (torch com CUDA)**: se `CUDA: False`, significa que está instalada a versão CPU do torch. Reinstale a versão CUDA:

```Bash
# Fonte oficial (rede no estrangeiro)
pip install torch --index-url https://download.pytorch.org/whl/cu128

# Em redes da China Continental, dê preferência ao espelho Aliyun
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
```

> Ou treine com CPU (`--policy.device=cpu`, mas bem mais lento).

> **💡 Dica**: `pip install -e ".[amazinghand]"` no Linux normalmente já resolve a versão GPU do torch (caso um ambiente CUDA seja detetado). Caso contrário, reinstale com os comandos acima.

---

## Passo 2: Treinar

```Bash
lerobot-train \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --policy.type=act \
  --output_dir=outputs/train/soarm_amazing_hand_pick \
  --job_name=soarm_amazing_hand_pick \
  --policy.device=cuda \
  --wandb.enable=false \
  --policy.push_to_hub=false \
  --steps=60000
```

> **💡 Nota**: `--dataset.repo_id` e `--dataset.root` devem ser **exatamente iguais** aos usados na gravação da Etapa 4 (`repo_id=soarm_amazing_hand_pick`, `root=~/lerobot_data`); assim é possível ler o conjunto de dados local, sem necessidade de iniciar sessão no HF.

---

## Descrição dos parâmetros

|Parâmetro|Descrição|
|---|---|
|`--dataset.repo_id`|Nome do conjunto de dados (igual ao da gravação)|
|`--dataset.root`|Caminho local do conjunto de dados (igual ao da gravação)|
|`--policy.type`|Tipo de política; `act` é a escolha mais comum|
|`--output_dir`|Diretório de saída do treino (checkpoints, logs)|
|`--job_name`|Nome da tarefa (para distinguir nos logs)|
|`--policy.device`|`cuda` (GPU) ou `cpu`|
|`--wandb.enable`|Registo de pesos; `false` desativa (sem necessidade de conta wandb)|
|`--policy.push_to_hub`|Se deve enviar o modelo para o HF; `false` significa apenas local|
|`--steps`|Número de passos de treino|

---

## Explicação do processo de treino

- **checkpoints**: guardados automaticamente a cada passo em `outputs/train/soarm_amazing_hand_pick/checkpoints/`

- **Logs**: o terminal exibe métricas como o loss em tempo real

- **Duração**: 60000 passos costumam levar algumas horas numa GPU de consumo (depende da placa gráfica)

> **⚠️ Nota 1 (ajuste do número de passos)**: `--steps=60000` é o valor típico para o ACT. Tarefas simples podem ser reduzidas para 30000; tarefas complexas podem ser aumentadas para 100000\+. Observe a convergência do loss.

> **⚠️ Nota 2 (retomar após interrupção)**: após uma interrupção, executar novamente o **comando com os mesmos parâmetros** continua a partir do último checkpoint.

> **⚠️ Nota 3 (wandb)**: para visualizar a curva de loss, ative `--wandb.enable=true` (requer `wandb login`). Desativado por predefinição.

> **⚠️ Nota 4 (servidor sem interface gráfica)**: se treinar num servidor SSH/sem monitor, garanta que não depende de GUI (o treino em si não requer display). Se usar parâmetros relacionados com `--display_data`, será necessário um servidor gráfico.

> **⚠️ Nota 5 (treino em segundo plano)**: para treinos longos, recomenda-se usar `nohup ... &` ou `tmux` para manter o processo, evitando interrupções por desconexão SSH:

```Bash
tmux new -s train
lerobot-train --dataset.repo_id=...
# Ctrl+B e depois D para desligar; tmux attach -t train para voltar a entrar
```

---

Depois de concluir esta etapa, avance para a Etapa 6: Implementação e avaliação.

---

## Resolução de problemas

|Sintoma|Causa|Solução|
|---|---|---|
|`CUDA: False`|torch versão CPU|Reinstalar o torch versão CUDA|
|Memória gráfica insuficiente (OOM)|Tamanho do lote demasiado grande|`--policy.batch_size=8` ou menos|
|Conjunto de dados não encontrado|repo\_id/root inconsistentes|Confirme que são exatamente iguais a `--dataset.repo_id` e `--dataset.root` da gravação|
|SSH cai a meio do treino|Processo terminado|Treinar em segundo plano com `tmux`/`nohup`|
|Erro do `wandb`|Não autenticado|`--wandb.enable=false` ou `wandb login`|

