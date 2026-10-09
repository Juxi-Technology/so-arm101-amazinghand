# win

# Etapa 4: Coleta de dados (Windows)

Esta etapa grava o conjunto de dados de teleoperação: coleta amostras de "ângulo das juntas \+ imagem das câmeras" sob controle manual, para treinamento posterior. A qualidade do conjunto de dados determina diretamente o efeito da política; **a operação deve ser padronizada e consistente**. Nesta etapa, **toda a gravação é local, sem necessidade de login no HF**.

---

## Pré-requisitos

- Etapa 3: Teleoperação concluída e direção verificada como correta

- câmeras conectadas e índices registrados (`lerobot-find-cameras`)

- caminho de armazenamento do conjunto de dados local definido (o exemplo deste documento usa `D:\lerobot_data`, personalizável)

---

## Passo 1: Confirmar os índices das câmeras

```PowerShell
lerobot-find-cameras
```

Registre os números das câmeras. Por exemplo:

- Número 0: câmera de pulso (wrist)

- Número 1: câmera superior (top)

> **⚠️ Nota (índices das câmeras)**: `index_or_path` é o índice da câmera (0/1/2\.\.\.) ou o caminho do fluxo de vídeo. A numeração varia conforme o computador; confirme sempre primeiro.

---

## Passo 2: Gravar o conjunto de dados (salvo localmente, sem necessidade de login)

```PowerShell
lerobot-record --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data --dataset.push_to_hub=false --dataset.num_episodes=20 --dataset.single_task="Pick up the cube with the dexterous hand" --display_data=true
```

> Substitua `<follower_arm_com>` / `<hand_com>` / `<leader_arm_com>` pelos números COM reais; e o `index_or_path` das câmeras pelo índice das suas câmeras.

> **💡 Notas**:

- `--dataset.root=D:\lerobot_data`: o conjunto de dados é salvo no **caminho local** especificado, **sem necessidade de login no HF** (se omitido, é salvo por padrão em `%USERPROFILE%\.cache\huggingface\lerobot\datasets\...`).

- `--dataset.push_to_hub=false`: **desativa o upload** (por padrão tenta enviar para o HF, exigindo login). Só mude para `true` se precisar compartilhar o conjunto de dados.

- `--dataset.repo_id=soarm_amazing_hand_pick`: nome do conjunto de dados; no treinamento, use o **mesmo nome** para referenciá-lo.

- `--display_data=true` requer o rerun (se não estiver instalado, `pip install "rerun-sdk>=0.24.0,<0.34.0"`); ou remova esse parâmetro (a gravação não é afetada).

---

## Descrição dos parâmetros

|Parâmetro|Descrição|
|---|---|
|`--robot.cameras`|Configuração das câmeras. `index_or_path` é o índice da câmera; `width/height/fps` são **obrigatórios**|
|`--dataset.repo_id`|Nome do conjunto de dados (identificador local)|
|`--dataset.root`|Caminho de armazenamento local do conjunto de dados. **Obrigatório em gravação totalmente local**, para evitar um caminho padrão fora de controle|
|`--dataset.push_to_hub`|`false`=apenas local (recomendado por padrão); `true`=enviar para o HF (requer login)|
|`--dataset.num_episodes`|Número de episódios a gravar|
|`--dataset.episode_time_s`|**Duração máxima em segundos de cada episódio** (padrão 60). Se a tarefa terminar antes, pressione Enter para encerrar antecipadamente; se ultrapassar, o episódio termina automaticamente|
|`--dataset.single_task`|Descrição da tarefa, gravada nos metadados do conjunto de dados|
|`--display_data=true`|Exibe a imagem da gravação em tempo real (opcional)|

---

## Padrões de operação na gravação

**Fluxo de cada episódio**:

1. Reponha o braço robótico \+ a mão na **posição inicial**

2. Pressione Enter no terminal para começar a gravar

3. Opere o braço líder para executar a tarefa (por exemplo, pegar o cubo); **os movimentos devem ser lentos e consistentes**

4. Ao concluir a tarefa, pressione Enter para encerrar o episódio (**se não pressionar, grava no máximo 60 segundos**, controlado por `--dataset.episode_time_s`, encerrando automaticamente ao atingir o tempo)

5. Repita até atingir `num_episodes`

> **⚠️ Nota 1 (posição inicial consistente)**: comece cada episódio na **mesma posição inicial**, para evitar confusão na distribuição dos dados. Recomenda-se fixar uma pose de reposição.

> **⚠️ Nota 2 (consistência dos movimentos)**: use trajetórias de operação semelhantes para a mesma tarefa (ângulo de aproximação, posição de agarrar, velocidade); a política aprende mais rápido e de forma mais estável.

> **⚠️ Nota 3 (qualidade da gravação)**: é melhor gravar menos episódios de alta qualidade do que muitos exemplos confusos. 20 episódios são o ponto de partida para o ACT; tarefas complexas recomendam 30\-50 episódios.

> **⚠️ Nota 4 (tempo real das câmeras)**: durante a gravação, evite obstruir as câmeras e variações de luz forte; a consistência das imagens afeta a generalização.

---

## Armazenamento dos dados

- **Gravação local**: os dados são salvos no diretório indicado por `--dataset.root` (exemplo `D:\lerobot_data\soarm_amazing_hand_pick`).

- **Referência no treinamento**: no treinamento, basta usar **o mesmo ****`--dataset.repo_id`**** \+ ****`--dataset.root`**, sem necessidade de mover arquivos manualmente:

```PowerShell
lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data ...
```

- **Cenário com login no HF** (opcional): para compartilhar o conjunto de dados na nuvem, mude para `--dataset.push_to_hub=true` (requer `huggingface-cli login`). Apenas para treinamento local, **não é necessário**.

> **⚠️ Nota (local vs. nuvem)**: por padrão, o tutorial é totalmente local; `--dataset.push_to_hub=false` garante que o login no HF não seja acionado. Adicione `true` somente se quiser compartilhar o conjunto de dados.

---

## Passo 3: Verificação por reprodução (opcional, mas recomendada)

Depois de gravar, use `lerobot-replay` para reproduzir um episódio e verificar a **qualidade dos dados \+ se o registro dos movimentos do robô está correto**. Durante a reprodução, o robô repete automaticamente os movimentos daquele episódio (incluindo a abertura/fechamento da mão).

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

> Substitua `<follower_arm_com>` / `<hand_com>` pelos números COM reais; `--dataset.episode` é o número do episódio a reproduzir (**começa em 0**; se gravou 20 episódios, vai de `0`\~`19`).

> **💡 Notas**: antes de reproduzir, mova o braço seguidor \+ a mão **de volta à posição inicial** para evitar conflitos de movimento; durante a reprodução, o robô se move sozinho, **não interfira manualmente**. Se os movimentos reproduzidos forem claramente diferentes dos gravados, a qualidade dos dados tem problemas; recomenda-se regravar o episódio.

---

Depois de concluir esta etapa, avance para a Etapa 5: Treinamento do modelo.

---

## Resolução de problemas

|Sintoma|Causa|Solução|
|---|---|---|
|Câmera não encontrada|Índice errado/driver ausente|Confirme com `lerobot-find-cameras`; instale o OpenCV/driver da câmera|
|Gravação interrompida|Tempo limite da porta serial|Confirme que as portas seriais dos três dispositivos não estão ocupadas e tente novamente|
|Imagem totalmente preta/com artefatos|Configuração incorreta das câmeras|Verifique `index_or_path`/`fps`|
|Conjunto de dados vazio|Gravação incorreta|Confirme que pressionou Enter para iniciar/encerrar cada episódio|

