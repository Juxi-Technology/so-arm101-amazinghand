# win

# Etapa 2: Calibração (Windows)

Esta etapa calibra três dispositivos: o braço líder, o braço seguidor e a mão AmazingHand. A calibração é o pré-requisito para a correção da teleoperação; **é obrigatório concluir esta etapa antes de entrar na teleoperação**.

> **Ordem de calibração**: braço líder → braço seguidor \+ mão → ângulos da mão. Cada passo exige **interação no terminal** (operação física \+ teclas).

> **⚠️ Aviso geral**: os parâmetros de porta serial nos comandos desta página são **espaços reservados de exemplo** e devem ser substituídos pelo número COM real da sua máquina (ver as portas seriais registradas na Etapa 1).

---

## Pré-requisitos

- Etapa 1: Configuração do ambiente concluída

- ambiente conda `lerobot` ativado

```Plain Text
# Ativar o ambiente
conda activate lerobot

# Entrar no lerobot
cd ../lerobot
```

- portas seriais dos três dispositivos registradas

- dispositivos alimentados, com alimentação independente

---

## Passo 1: Calibrar o braço líder

```PowerShell
lerobot-calibrate --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Substitua `<leader_arm_com>` pelo número COM real da sua máquina (exemplo `COM54`).

**Passos interativos**:

1. Mova **todas as juntas do braço líder para a posição intermediária** e pressione Enter

2. **Empurre cada junta, uma a uma, até o curso máximo/mínimo** e pressione Enter ao terminar

**Verificação**: o arquivo de calibração é salvo automaticamente em
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\teleoperators\so_leader\amazing_hand_leader.json`

> **⚠️ Nota 1 (a garra deve ser calibrada)**: o curso do servo da garra nº 6 será usado como referência de normalização de `gripper.pos` (0\~100). A garra deve ser empurrada de totalmente aberta até totalmente fechada, com calibração correta, caso contrário a proporção de abertura/fechamento da mão ficará distorcida.

> **⚠️ Nota 2 (rotação livre)**: durante a calibração, o braço robótico deve poder girar livremente, garantindo que os servos estejam sem carga.

> **⚠️ Nota 3 (local do arquivo de calibração)**: no Windows, o caminho é o diretório do usuário `%USERPROFILE%\.cache\huggingface\lerobot\calibration\`.

---

## Passo 2: Calibrar o braço seguidor (conectando também a mão)

```PowerShell
lerobot-calibrate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower
```

> Substitua `<follower_arm_com>` / `<hand_com>` pelos números COM reais (exemplo `COM58` / `COM11`).

**Passos interativos**:

1. Mova as **5 juntas** do braço seguidor (sem a nº 6) para a posição intermediária e pressione Enter

2. Percorra o curso completo de cada junta e pressione Enter

**Verificação**: o arquivo de calibração é salvo em
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\amazing_hand_follower.json`

> **⚠️ Nota 1 (torque da mão ativado automaticamente)**: ao conectar, este comando **ativa automaticamente o torque dos 8 servos da mão** (o log mostra `enabling AmazingHand torque`); ao fim da calibração a mão se abre, o que é um comportamento normal.

> **⚠️ Nota 2 (não abre GUI da mão)**: os ângulos da mão **não usam** o `RangeFinderGUI` do lerobot; a calibração termina junto com a do braço seguidor. Os ângulos da mão usam a ferramenta dedicada do passo 3.

> **⚠️ Nota 3 (ocupação da porta serial)**: este passo ocupa a porta serial da mão. **Não** execute ao mesmo tempo outros processos que ocupem essa porta serial.

---

## Passo 3: Calibrar os ângulos da mão \+ a direção da garra (GUI dedicada)

```PowerShell
lerobot-calibrate-amazing-hand --hand_port <hand-port> --leader_port <leader-port>
```

> Substitua `<hand_com>` / `<leader_arm_com>` pelos números COM reais (exemplo `COM11` / `COM54`). O `--leader_port` serve para calibrar em conjunto a **direção da garra** (ver abaixo).

**Operações na GUI**:

1. Arraste os controles deslizantes dos 4 dedos (index/middle/ring/thumb) para deixar a mão **totalmente aberta** e clique em **`Save Open`**

2. Arraste o controle deslizante para deixar a mão **totalmente fechada em punho** e clique em **`Save Close`**

3. **Abra a garra do braço líder** e clique em **`Capture Open`** (a GUI mostra `gripper.pos` em tempo real; ao abrir, deve se aproximar de 100)

4. **Feche a garra do braço líder** e clique em **`Capture Close`** (ao fechar, deve se aproximar de 0)

5. **Gravação automática**: depois de definir os quatro valores acima, aparece uma faixa verde no topo da janela com `AUTO-SAVED to ...\hand_angles.json`, e o terminal imprime o caminho em simultâneo

6. Feche a janela (a mão libera o torque automaticamente)

**Verificação**: os ângulos e o mapeamento da garra são salvos em
`C:\Users\<username>\.cache\huggingface\lerobot\calibration\robots\so101_amazing_hand\hand_angles.json`

> **⚠️ Nota 1 (calibração obrigatória)**: **cada computador novo/cada mão nova deve executar este passo**. Os ângulos no config são o padrão genérico oficial do AmazingHand, servindo apenas de reserva; quando `hand_angles.json` existe, os seus valores medidos são carregados com prioridade. Não calibrar pode causar erros na direção/alcance de abertura e fechamento.

> **⚠️ Nota 2 (carregamento automático)**: a cada inicialização, o robô lê `hand_angles.json` (contendo `gripper_open_pos`/`gripper_close_pos`) e substitui os valores padrão do config, **sem necessidade de alterar o código**. A direção da garra varia conforme o braço líder; basta calibrar uma vez.

> **⚠️ Nota 3 (semântica do controle deslizante)**: mover o controle deslizante no sentido `+` faz o m1 desse dedo ir para `+angle` e o m2 para `-angle` (espelhado). Baseie-se na **pose real da mão** para determinar aberta/fechada em punho, sem se preocupar com os valores numéricos dos ângulos.

> **⚠️ Nota 4 (calibração precisa)**: ao calibrar "totalmente aberta", não exagere (dedos tortos/afastados); ao calibrar "totalmente fechada em punho", não aperte em excesso (servos sob pressão contínua). Caso contrário, na teleoperação a abertura/fechamento passará do ponto.

> **⚠️ Nota 5 (ordem dos Capture)**: `Capture Open` / `Capture Close` correspondem à abertura/fechamento da **garra do braço líder**, não aos dedos da mão. Se a direção de abertura da mão ficar invertida, provavelmente a calibração aqui ou a dos ângulos da mão ficou invertida; basta recalibrar.

> **⚠️ Nota 6 (a GUI não abre)**: confirme que o `pygame` está instalado (incluído no extra `amazinghand`). Se ainda não abrir, verifique se existe um ambiente de área de trabalho gráfica.

---

## Recalibração

Quando precisar recalibrar apenas uma parte:

- **Apenas a mão** → executar somente o passo 3

- **Apenas o braço seguidor** → executar somente o passo 2 (ativará também o torque da mão)

- **Tudo** → passos 1 → 2 → 3

> **⚠️ Nota**: os passos 2 e 3 **não podem ser executados ao mesmo tempo** (ambos ocupam a porta serial da mão).

---

Depois de concluir esta etapa, avance para a Etapa 3: Teleoperação.

---

## Resolução de problemas

|Sintoma|Causa|Solução|
|---|---|---|
|Calibração do braço líder retorna erro de modelo 2307|Barramento do braço poluído/conflito de porta serial<br>|Confirme que a porta serial da mão não está conectada ao mesmo tempo; neste projeto a mão usa rustypot, o que já contorna o problema|
|Calibração da mão sem GUI|Comando errado|Deve usar `lerobot-calibrate-amazing-hand` (não `lerobot-calibrate`)|
|O driver da mão retorna `Operation timed out`|Porta serial ocupada/temporização|Confirme que a porta serial da mão não está ocupada e tente novamente|
|Arquivo de calibração não encontrado|Caminho errado<br>|Verifique `%USERPROFILE%\.cache\huggingface\lerobot\calibration\`|
|A porta serial não abre|Número COM errado|Use `lerobot-find-port` para confirmar novamente|

