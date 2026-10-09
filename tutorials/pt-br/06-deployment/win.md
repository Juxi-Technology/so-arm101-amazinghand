# win

# Etapa 6: Implantação e avaliação (Windows)

Esta etapa carrega a política treinada para que o robô **execute a tarefa de forma autônoma** e grava vídeos de avaliação para verificar o resultado. É a conclusão de todo o fluxo e também o momento decisivo para aferir o resultado do treinamento.

---

## Pré-requisitos

- Etapa 5: Treinamento do modelo concluída

- O treinamento gerou `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/`

- Índices das câmeras registrados

---

## Passo 1: Confirmar os arquivos do modelo

```PowerShell
# Confirmar que o diretório do modelo existe
dir outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model
```

Deve conter arquivos de modelo como `model.safetensors`.

> **⚠️ Nota (caminho do modelo)**: `--policy.path` deve apontar para o diretório `pretrained_model` (com configuração \+ pesos), e não para o diretório raiz do checkpoint.

---

## Passo 2: Implantar e avaliar

```PowerShell
lerobot-record `
  --robot.type=so101_amazing_hand `
  --robot.port=<follower-port> `
  --robot.hand_port=<hand-port> `
  --robot.id=amazing_hand_follower `
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' `
  --policy.path=outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model `
  --dataset.repo_id=soarm_amazing_hand_pick_eval `
  --dataset.root=D:\lerobot_data `
  --dataset.push_to_hub=false `
  --dataset.num_episodes=10 `
  --dataset.single_task="Pick up the cube with the dexterous hand" `
  --display_data=true
```

> Substitua `<follower_arm_com>` / `<hand_com>` pelos números COM reais; e o `index_or_path` das câmeras pelo índice das suas câmeras.

> **💡 Nota**: usa-se `lerobot-record` mas **sem adicionar ****`--teleop.type`**; a política controla o robô de forma autônoma (substituindo a teleoperação manual). Os dados são salvos como conjunto de avaliação. `--dataset.root` / `--dataset.push_to_hub=false` são iguais aos da Etapa 4; gravação totalmente local, sem necessidade de login no HF.

---

## Operações de avaliação

1. Reponha o robô \+ a mão na **posição inicial**

2. Pressione Enter para começar: a política executa a tarefa de forma autônoma

3. Observe **se a garra pega com sucesso** (pressione Enter ao fim de cada episódio para continuar)

4. Repita por `num_episodes` episódios

**Métrica de avaliação**: taxa de sucesso = episódios com sucesso / total de episódios

> **⚠️ Nota 1 (consistência da reposição)**: comece cada episódio na **mesma posição inicial**, caso contrário a generalização da política falha e a taxa de sucesso fica artificialmente baixa.

> **⚠️ Nota 2 (segurança)**: na primeira execução autônoma, recomenda-se **segurar com a mão/observar em velocidade lenta** para confirmar que os movimentos da política são razoáveis. A política pode executar movimentos inesperados.

> **⚠️ Nota 3 (expectativa de taxa de sucesso)**: o ACT normalmente atinge 50\-80% de taxa de sucesso com 20 episódios de dados. Se ficar abaixo do esperado, volte atrás para gravar mais dados ou ajuste o número de passos de treinamento.

---

## Otimização iterativa

Se a taxa de sucesso da avaliação não for satisfatória, ajuste por ordem de prioridade:

|Prioridade|Item de otimização|Ação|
|---|---|---|
|1|Gravar mais dados de alta qualidade|Volte à Etapa 4 e grave 20\-30 episódios adicionais mais consistentes|
|2|Aumentar o número de passos de treinamento|Volte à Etapa 5, `--steps=100000`|
|3|Verificar a consistência da posição inicial|Repor rigorosamente a posição em cada episódio da avaliação|
|4|Ajustar a descrição da tarefa|Garanta que `single_task` corresponde à tarefa|

---

Até aqui conclui-se o **ciclo completo** do SO\-ARM101 \+ AmazingHand: calibração → teleoperação → coleta → treinamento → implantação.

---

## Resolução de problemas

|Sintoma|Causa|Solução|
|---|---|---|
|Falha ao carregar o modelo|Caminho errado/incompleto|Confirme que `--policy.path` aponta para o diretório `pretrained_model`|
|A política não se move|Câmera/observação incorretas|Confirme que os índices das câmeras são iguais aos do treinamento; verifique a imagem de `--display_data`|
|A política se move de forma aleatória|Posição inicial inconsistente/dados ruins|Reponha rigorosamente; grave mais dados|
|Comportamento diferente do treinamento|Diferenças de ambiente|Confirme que câmeras, iluminação e posição dos objetos são iguais aos da gravação|

