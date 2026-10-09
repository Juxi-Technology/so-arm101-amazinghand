# linux

# Etapa 3: Teleoperação (Linux)

Esta etapa inicia o ciclo fechado de teleoperação: o braço líder controla o movimento do braço seguidor e a garra controla a abertura/fecho da AmazingHand. Esta é a etapa decisiva para verificar se todo o sistema funciona corretamente.

---

## Pré-requisitos

- Etapa 1: Configuração do ambiente e Etapa 2: Calibração concluídas

- permissões da porta série configuradas

- os três dispositivos alimentados e as portas série registadas

---

## Executar a teleoperação

```Bash
lerobot-teleoperate \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --teleop.type=so101_leader \
  --teleop.port=<leader-port> \
  --teleop.id=amazing_hand_leader
```

> Substitua `<follower_arm_port>` / `<hand_port>` / `<leader_arm_port>` pelos caminhos reais da sua máquina (exemplo `/dev/ttyACM0` / `/dev/ttyACM2` / `/dev/ttyACM1`).

**Efeito esperado**:

- 5 juntas do braço líder → o braço seguidor acompanha

- garra do braço líder → abertura/fecho da AmazingHand (acompanhamento proporcional: meio pinçado = meio fechado)

> **💡 Descrição dos parâmetros**:

- `--robot.type=so101_amazing_hand`: robô combinado de braço seguidor \+ mão

- `--robot.port`: porta série do braço seguidor

- `--robot.hand_port`: porta série da mão

- `--teleop.type=so101_leader`: teleoperador do braço líder

- `--teleop.port`: porta série do braço líder

---

## Obrigatório na primeira execução: verificação de direção

Após o arranque, faça primeiro um **teste de direção** para confirmar que os dois pontos seguintes estão corretos:

|Teste|Operação|Comportamento correto|
|---|---|---|
|Acompanhamento do braço|Gire cada junta do braço líder|O braço seguidor acompanha na mesma direção|
|Abertura/fecho da mão|Abra/pinça a garra do braço líder|Garra aberta → mão aberta; garra pinçada → mão fechada|

> **⚠️ Nota (e se a direção estiver invertida)**:

- **Direção de abertura/fecho da mão invertida** (ao abrir a garra, a mão fecha em vez disso): indica calibração imprecisa dos ângulos da mão; execute novamente a ferramenta de calibração (incluindo a calibração da direção da garra); passa a valer automaticamente após guardar, **sem necessidade de alterar ficheiros manualmente**. Ver Etapa 2: Calibração.

- **Direção do mapeamento da garra invertida** (ao abrir a garra, a mão fecha em vez disso): o mesmo que acima; ao calibrar, clique em `[Capture Open]` com a garra do braço líder **aberta** e em `[Capture Close]` com ela **pinçada**; a ferramenta regista e guarda automaticamente `gripper_open_pos`/`gripper_close_pos`, carregados automaticamente no arranque.

> Após a alteração, **execute novamente a teleoperação** para verificar.

---

## Verificação do acompanhamento proporcional

Com a direção correta, verifique a fineza da proporção:

1. Abra a garra **lentamente** → a mão deve abrir **suavemente** (sem saltos)

2. Pare a garra **a meio** → a mão também deve parar a meio

3. Abra e feche rapidamente → a mão responde rapidamente, sem bloqueios

> **⚠️ Nota (problema histórico de abertura/fecho excessivo da mão)**: se a mão fechar quando a garra estiver apenas a meio, na maioria dos casos a posição de "aberta/fechada em punho" na calibração dos ângulos da mão está imprecisa. Execute novamente o passo 3 da calibração (GUI dos ângulos da mão) para calibrar posições de abertura/fecho mais precisas.

---

## Opcional: visualização com câmaras

Adicione `--robot.cameras` para ligar câmaras e `--display_data=true` para abrir a janela de visualização do Rerun (exibe em tempo real as imagens das câmaras \+ o estado das juntas):

```Bash
lerobot-teleoperate \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> \
  --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --teleop.type=so101_leader \
  --teleop.port=<leader-port> \
  --teleop.id=amazing_hand_leader \
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' \
  --display_data=true
```

> **💡 Notas**:

- `index_or_path` é o índice da câmara; confirme primeiro com `lerobot-find-cameras` (a numeração varia conforme a máquina).

- `fourcc: "MJPG"` é opcional e reduz significativamente o consumo de largura de banda das câmaras USB (passa a usar compressão MJPEG); pode ser adicionado em caso de bloqueios.

- Se precisar de apenas uma câmara, basta remover a linha correspondente (por exemplo, `top`).

> **⚠️ Nota (dependência do rerun e exibição)**: `--display_data=true` requer o pacote de visualização rerun; se não estiver instalado, execute:

```Bash
pip install "rerun-sdk>=0.24.0,<0.34.0"
```

> Além disso, a janela do rerun requer um servidor gráfico (sessão gráfica local ou `ssh -X`). Em ambiente sem interface gráfica, **isso não afeta a teleoperação**; basta remover `--display_data=true`.

---

## Sair

Prima `Ctrl+C` para parar. O programa automaticamente:

1. Liberta o binário dos 8 servos da mão

2. Desliga as portas série do braço seguidor/líder

3. Desliga as câmaras (se existirem)

> **⚠️ Nota**: antes de sair normalmente, **não feche o terminal diretamente** (por exemplo, com `kill -9`), caso contrário pode ficar uma porta série ocupada. Se, após uma saída anormal, a porta série ficar ocupada, encerre o processo remanescente ou volte a ligar o USB.

---

## Resolução de problemas

|Sintoma|Causa|Solução|
|---|---|---|
|`Permission denied` na porta série|Permissões não configuradas|`sudo chmod 666 /dev/ttyACM*`|
|Direção da mão invertida|Direção dos ângulos da mão ou do mapeamento da garra invertida|Ver "Verificação de direção" acima|
|Abertura/fecho excessivo/insuficiente da mão|Calibração imprecisa dos ângulos da mão|Recalibrar a GUI dos ângulos da mão|
|O braço não acompanha|Calibração ausente/porta série errada|Confirme que o braço seguidor está calibrado e que `--robot.port` está correto|
|Erro do rerun|Dependência de visualização/exibição ausente|Remova `--display_data=true`|
|Porta série ocupada|Saída anormal anterior|Encerre o processo remanescente ou volte a ligar o USB|

