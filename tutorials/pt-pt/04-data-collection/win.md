# win

# Etapa 4: Recolha de dados (Windows)

Esta etapa grava o conjunto de dados de teleoperação: recolhe amostras de "ângulo das juntas \+ imagem das câmaras" sob controlo manual, para treino posterior. A qualidade do conjunto de dados determina diretamente o efeito da política; **a operação deve ser padronizada e consistente**. Nesta etapa, **toda a gravação é local, sem necessidade de iniciar sessão no HF**.

---

## Pré-requisitos

- Etapa 3: Teleoperação concluída e direção verificada como correta

- câmaras ligadas e índices registados (`lerobot-find-cameras`)

- caminho de armazenamento do conjunto de dados local definido (o exemplo deste documento usa `D:\lerobot_data`, personalizável)

---

## Passo 1: Confirmar os índices das câmaras

```PowerShell
lerobot-find-cameras
```

Registe os números das câmaras. Por exemplo:

- Número 0: câmara de pulso (wrist)

- Número 1: câmara superior (top)

> **⚠️ Nota (índices das câmaras)**: `index_or_path` é o índice da câmara (0/1/2\.\.\.) ou o caminho do fluxo de vídeo. A numeração varia conforme o computador; confirme sempre primeiro.

---

## Passo 2: Gravar o conjunto de dados (guardado localmente, sem necessidade de autenticação)

```PowerShell
lerobot-record --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data --dataset.push_to_hub=false --dataset.num_episodes=20 --dataset.single_task="Pick up the cube with the dexterous hand" --display_data=true
```

> Substitua `<follower_arm_com>` / `<hand_com>` / `<leader_arm_com>` pelos números COM reais; e o `index_or_path` das câmaras pelo índice das suas câmaras.

> **💡 Notas**:

- `--dataset.root=D:\lerobot_data`: o conjunto de dados é guardado no **caminho local** especificado, **sem necessidade de iniciar sessão no HF** (se omitido, é guardado por predefinição em `%USERPROFILE%\.cache\huggingface\lerobot\datasets\...`).

- `--dataset.push_to_hub=false`: **desativa o upload** (por predefinição tenta enviar para o HF, exigindo autenticação). Só altere para `true` se precisar de partilhar o conjunto de dados.

- `--dataset.repo_id=soarm_amazing_hand_pick`: nome do conjunto de dados; no treino, use o **mesmo nome** para o referenciar.

- `--display_data=true` requer o rerun (se não estiver instalado, `pip install "rerun-sdk>=0.24.0,<0.34.0"`); ou remova esse parâmetro (a gravação não é afetada).

---

## Descrição dos parâmetros

|Parâmetro|Descrição|
|---|---|
|`--robot.cameras`|Configuração das câmaras. `index_or_path` é o índice da câmara; `width/height/fps` são **obrigatórios**|
|`--dataset.repo_id`|Nome do conjunto de dados (identificador local)|
|`--dataset.root`|Caminho de armazenamento local do conjunto de dados. **Obrigatório em gravação totalmente local**, para evitar um caminho predefinido fora de controlo|
|`--dataset.push_to_hub`|`false`=apenas local (recomendado por predefinição); `true`=enviar para o HF (requer autenticação)|
|`--dataset.num_episodes`|Número de episódios a gravar|
|`--dataset.episode_time_s`|**Duração máxima em segundos de cada episódio** (predefinição 60). Se a tarefa terminar antes, prima Enter para encerrar antecipadamente; se ultrapassar, o episódio termina automaticamente|
|`--dataset.single_task`|Descrição da tarefa, gravada nos metadados do conjunto de dados|
|`--display_data=true`|Exibe a imagem da gravação em tempo real (opcional)|

---

## Padrões de operação na gravação

**Fluxo de cada episódio**:

1. Reponha o braço robótico \+ a mão na **posição inicial**

2. Prima Enter no terminal para começar a gravar

3. Opere o braço líder para executar a tarefa (por exemplo, agarrar o cubo); **os movimentos devem ser lentos e consistentes**

4. Ao concluir a tarefa, prima Enter para encerrar o episódio (**se não premir, grava no máximo 60 segundos**, controlado por `--dataset.episode_time_s`, encerrando automaticamente ao atingir o tempo)

5. Repita até atingir `num_episodes`

> **⚠️ Nota 1 (posição inicial consistente)**: comece cada episódio na **mesma posição inicial**, para evitar confusão na distribuição dos dados. Recomenda-se fixar uma pose de reposição.

> **⚠️ Nota 2 (consistência dos movimentos)**: utilize trajetórias de operação semelhantes para a mesma tarefa (ângulo de aproximação, posição de agarrar, velocidade); a política aprende mais rapidamente e de forma mais estável.

> **⚠️ Nota 3 (qualidade da gravação)**: é preferível gravar menos episódios de alta qualidade do que muitos exemplos confusos. 20 episódios são o ponto de partida para o ACT; tarefas complexas recomendam 30\-50 episódios.

> **⚠️ Nota 4 (tempo real das câmaras)**: durante a gravação, evite obstruir as câmaras e variações de luz forte; a consistência das imagens afeta a generalização.

---

## Armazenamento dos dados

- **Gravação local**: os dados são guardados no diretório indicado por `--dataset.root` (exemplo `D:\lerobot_data\soarm_amazing_hand_pick`).

- **Referência no treino**: no treino, basta usar **o mesmo ****`--dataset.repo_id`**** \+ ****`--dataset.root`**, sem necessidade de mover ficheiros manualmente:

```PowerShell
lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data ...
```

- **Cenário com autenticação no HF** (opcional): para partilhar o conjunto de dados na nuvem, altere para `--dataset.push_to_hub=true` (requer `huggingface-cli login`). Apenas para treino local, **não é necessário**.

> **⚠️ Nota (local vs. nuvem)**: por predefinição, o tutorial é totalmente local; `--dataset.push_to_hub=false` garante que a autenticação no HF não é acionada. Adicione `true` apenas se quiser partilhar o conjunto de dados.

---

## Passo 3: Verificação por reprodução (opcional, mas recomendada)

Depois de gravar, use `lerobot-replay` para reproduzir um episódio e verificar a **qualidade dos dados \+ se o registo dos movimentos do robô está correto**. Durante a reprodução, o robô repete automaticamente os movimentos desse episódio (incluindo a abertura/fecho da mão).

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

> **💡 Notas**: antes de reproduzir, mova o braço seguidor \+ a mão **de volta à posição inicial** para evitar conflitos de movimento; durante a reprodução, o robô move-se sozinho, **não interfira manualmente**. Se os movimentos reproduzidos forem claramente diferentes dos gravados, a qualidade dos dados tem problemas; recomenda-se regravar o episódio.

---

Depois de concluir esta etapa, avance para a Etapa 5: Treino do modelo.

---

## Resolução de problemas

|Sintoma|Causa|Solução|
|---|---|---|
|Câmara não encontrada|Índice errado/controlador ausente|Confirme com `lerobot-find-cameras`; instale o OpenCV/controlador da câmara|
|Gravação interrompida|Tempo limite da porta série|Confirme que as portas série dos três dispositivos não estão ocupadas e tente novamente|
|Imagem totalmente preta/com artefactos|Configuração incorreta das câmaras|Verifique `index_or_path`/`fps`|
|Conjunto de dados vazio|Gravação incorreta|Confirme que premiu Enter para iniciar/encerrar cada episódio|

