# linux

# Etapa 2: Calibração (Linux)

Esta etapa calibra três dispositivos: o braço líder, o braço seguidor e a mão AmazingHand. A calibração é o pré-requisito para a correção da teleoperação; **é obrigatório concluir esta etapa antes de entrar na teleoperação**.

> **Ordem de calibração**: braço líder → braço seguidor \+ mão → ângulos da mão. Cada passo exige **interação no terminal** (operação física \+ teclas).

> **⚠️ Aviso geral**: os parâmetros de porta série nos comandos desta página são **espaços reservados de exemplo** e devem ser substituídos pelos caminhos de porta série reais da sua máquina (ver as portas série registadas na Etapa 1).

---

## Pré-requisitos

- Etapa 1: Configuração do ambiente concluída

- ambiente conda `lerobot` ativado

- permissões da porta série configuradas (secção 5 da Etapa 1)

- portas série dos três dispositivos registadas

- dispositivos alimentados, com alimentação independente

---

## Passo 1: Calibrar o braço líder

```Bash
lerobot-calibrate \
  --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Substitua `<leader_arm_port>` pelo caminho real da sua máquina (exemplo `/dev/ttyACM1`).

**Passos interativos**:

1. Mova **todas as juntas do braço líder para a posição intermédia** e prima Enter

2. **Empurre cada junta, uma a uma, até ao curso máximo/mínimo** e prima Enter no fim

**Verificação**: o ficheiro de calibração é guardado automaticamente em
`~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/amazing_hand_leader.json`

> **⚠️ Nota 1 (a garra deve ser calibrada)**: o curso do servo da garra n.º 6 serve de referência de normalização para `gripper.pos` (0\~100). A garra deve ser empurrada de totalmente aberta até totalmente fechada, com calibração correta, caso contrário a proporção de abertura/fecho da mão fica distorcida.

> **⚠️ Nota 2 (rotação livre)**: durante a calibração, o braço robótico deve poder girar livremente, garantindo que os servos estejam sem carga.

> **⚠️ Nota 3 (permissões)**: se aparecer `Permission denied` na porta série, execute primeiro `sudo chmod 666 /dev/ttyACM*` (ou confirme que as regras udev foram configuradas na Etapa 1).

---

## Passo 2: Calibrar o braço seguidor (ligando também a mão)

```Bash
lerobot-calibrate \
  --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower
```

> Substitua `<follower_arm_port>` / `<hand_port>` pelos caminhos reais (exemplo `/dev/ttyACM0` / `/dev/ttyACM2`).

**Passos interativos**:

1. Mova as **5 juntas** do braço seguidor (sem a n.º 6) para a posição intermédia e prima Enter

2. Percorra o curso completo de cada junta e prima Enter

**Verificação**: o ficheiro de calibração é guardado em
`~/.cache/huggingface/lerobot/calibration/robots/so101_amazing_hand/amazing_hand_follower.json`

> **⚠️ Nota 1 (binário da mão ativado automaticamente)**: ao ligar, este comando **ativa automaticamente o binário dos 8 servos da mão** (o log mostra `enabling AmazingHand torque`); no fim da calibração a mão abre, o que é um comportamento normal.

> **⚠️ Nota 2 (não abre GUI da mão)**: os ângulos da mão **não usam** o `RangeFinderGUI` do lerobot; a calibração termina em conjunto com a do braço seguidor. Os ângulos da mão usam a ferramenta dedicada do passo 3.

> **⚠️ Nota 3 (ocupação da porta série)**: este passo ocupa a porta série da mão. **Não** execute em simultâneo outros processos que ocupem essa porta série.

---

## Passo 3: Calibrar os ângulos da mão \+ a direção da garra (GUI dedicada)

```Bash
lerobot-calibrate-amazing-hand --hand_port <hand-port> --leader_port <leader-port>
```

> Substitua `<hand_port>` / `<leader_arm_port>` pelos caminhos reais (exemplo `/dev/ttyACM2` / `/dev/ttyACM1`). O `--leader_port` serve para calibrar em conjunto a **direção da garra** (ver abaixo).

> **⚠️ Nota (ambiente sem display)**: a GUI requer um ambiente de trabalho gráfico. Se for executada em ambiente sem monitor/SSH, ocorre o erro `pygame.error: video system not initialized`. Soluções:

- Executar numa sessão gráfica local; ou

- Executar através de reencaminhamento X11 (`ssh -X`).

**Operações na GUI**:

1. Arraste os cursores dos 4 dedos (index/middle/ring/thumb) para deixar a mão **totalmente aberta** e clique em **`Save Open`**

2. Arraste o cursor para deixar a mão **totalmente fechada em punho** e clique em **`Save Close`**

3. **Abra a garra do braço líder** e clique em **`Capture Open`** (a GUI mostra `gripper.pos` em tempo real; ao abrir, deve aproximar-se de 100)

4. **Feche a garra do braço líder** e clique em **`Capture Close`** (ao fechar, deve aproximar-se de 0)

5. **Guardado automático**: depois de definir os quatro valores acima, aparece uma faixa verde no topo da janela com `AUTO-SAVED to .../hand_angles.json`, e o terminal imprime o caminho em simultâneo

6. Feche a janela (a mão liberta o binário automaticamente)

**Verificação**: os ângulos e o mapeamento da garra são guardados em
`~/.cache/huggingface/lerobot/calibration/robots/so101_amazing_hand/hand_angles.json`

> **⚠️ Nota 1 (calibração obrigatória)**: **cada computador novo/cada mão nova deve executar este passo**. Os ângulos no config são o padrão genérico oficial do AmazingHand, servindo apenas de reserva; quando `hand_angles.json` existe, os seus valores medidos são carregados com prioridade. Não calibrar pode causar erros na direção/alcance de abertura e fecho.

> **⚠️ Nota 2 (carregamento automático)**: a cada arranque, o robô lê `hand_angles.json` (contendo `gripper_open_pos`/`gripper_close_pos`) e substitui os valores padrão do config, **sem necessidade de alterar o código**. A direção da garra varia conforme o braço líder; basta calibrar uma vez.

> **⚠️ Nota 3 (semântica do cursor)**: mover o cursor no sentido `+` faz o m1 desse dedo ir para `+angle` e o m2 para `-angle` (espelhado). Baseie-se na **pose real da mão** para determinar aberta/fechada em punho, sem se preocupar com os valores numéricos dos ângulos.

> **⚠️ Nota 4 (calibração precisa)**: ao calibrar "totalmente aberta", não exagere (dedos tortos/afastados); ao calibrar "totalmente fechada em punho", não aperte em excesso (servos sob pressão contínua).

> **⚠️ Nota 5 (ordem dos Capture)**: `Capture Open` / `Capture Close` correspondem à abertura/fecho da **garra do braço líder**, não aos dedos da mão. Se a direção de abertura da mão ficar invertida, provavelmente a calibração aqui ou a dos ângulos da mão ficou invertida; basta recalibrar.

---

## Recalibração

Quando precisar de recalibrar apenas uma parte:

- **Apenas a mão** → executar somente o passo 3

- **Apenas o braço seguidor** → executar somente o passo 2 (ativará também o binário da mão)

- **Tudo** → passos 1 → 2 → 3

> **⚠️ Nota**: os passos 2 e 3 **não podem ser executados em simultâneo** (ambos ocupam a porta série da mão).

---

Depois de concluir esta etapa, avance para a Etapa 3: Teleoperação.

---

## Resolução de problemas

|Sintoma|Causa|Solução|
|---|---|---|
|`Permission denied` na porta série|Permissões não configuradas|`sudo chmod 666 /dev/ttyACM*` ou configurar udev|
|A GUI de calibração da mão não abre|Ambiente sem interface gráfica|Executar numa sessão gráfica local ou usar reencaminhamento `ssh -X`|
|O controlador da mão devolve `Operation timed out`|Porta série ocupada/temporização|Confirme que a porta série da mão não está ocupada e tente novamente|
|Calibração do braço líder devolve erro de modelo 2307|Barramento do braço poluído|Confirme que a porta série da mão não está ligada em simultâneo; neste projeto a mão usa rustypot, o que já contorna o problema|

