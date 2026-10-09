# win

# Etapa 3: Teleoperação (Windows)

Esta etapa inicia o ciclo fechado de teleoperação: o braço líder controla o movimento do braço seguidor e a garra controla a abertura/fechamento da AmazingHand. Esta é a etapa decisiva para verificar se todo o sistema funciona corretamente.

---

## Pré-requisitos

- Etapa 1: Configuração do ambiente e Etapa 2: Calibração concluídas

- os três dispositivos alimentados e as portas seriais registradas

---

## Executar a teleoperação

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> Substitua `<follower_arm_com>` / `<hand_com>` / `<leader_arm_com>` pelos números COM reais da sua máquina (exemplo `COM58` / `COM11` / `COM54`).

**Efeito esperado**:

- 5 juntas do braço líder → o braço seguidor acompanha

- garra do braço líder → abertura/fechamento da AmazingHand (acompanhamento proporcional: meio pinçado = meio fechado)

> **💡 Descrição dos parâmetros**:

- `--robot.type=so101_amazing_hand`: robô combinado de braço seguidor \+ mão

- `--robot.port`: porta serial do braço seguidor

- `--robot.hand_port`: porta serial da mão

- `--teleop.type=so101_leader`: teleoperador do braço líder

- `--teleop.port`: porta serial do braço líder

---

## Obrigatório na primeira execução: verificação de direção

Após iniciar, faça primeiro um **teste de direção** para confirmar que os dois pontos a seguir estão corretos:

|Teste|Operação|Comportamento correto|
|---|---|---|
|Acompanhamento do braço|Gire cada junta do braço líder|O braço seguidor acompanha na mesma direção|
|Abertura/fechamento da mão|Abra/pinça a garra do braço líder|Garra aberta → mão aberta; garra pinçada → mão fechada|

> **⚠️ Nota (e se a direção estiver invertida)**:

- **Direção de abertura/fechamento da mão invertida** (ao abrir a garra, a mão fecha em vez disso): indica calibração imprecisa dos ângulos da mão; execute novamente a ferramenta de calibração (incluindo a calibração da direção da garra); passa a valer automaticamente após salvar, **sem necessidade de alterar arquivos manualmente**. Ver Etapa 2: Calibração.

- **Direção do mapeamento da garra invertida** (ao abrir a garra, a mão fecha em vez disso): o mesmo que acima; ao calibrar, clique em `[Capture Open]` com a garra do braço líder **aberta** e em `[Capture Close]` com ela **pinçada**; a ferramenta registra e salva automaticamente `gripper_open_pos`/`gripper_close_pos`, carregados automaticamente na inicialização.

> Após a alteração, **execute novamente a teleoperação** para verificar.

---

## Verificação do acompanhamento proporcional

Com a direção correta, verifique a fineza da proporção:

1. Abra a garra **lentamente** → a mão deve abrir **suavemente** (sem saltos)

2. Pare a garra **no meio** → a mão também deve parar no meio

3. Abra e feche rapidamente → a mão responde rapidamente, sem travamentos

> **⚠️ Nota (problema histórico de abertura/fechamento excessivo da mão)**: se a mão fechar quando a garra estiver apenas na metade, na maioria dos casos a posição de "aberta/fechada em punho" na calibração dos ângulos da mão está imprecisa. Execute novamente o passo 3 da calibração (GUI dos ângulos da mão) para calibrar posições de abertura/fechamento mais precisas.

---

## Opcional: visualização com câmeras

Adicione `--robot.cameras` para conectar câmeras e `--display_data=true` para abrir a janela de visualização do Rerun (exibe em tempo real as imagens das câmeras \+ o estado das juntas):

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --display_data=true
```

> **💡 Notas**:

- `index_or_path` é o índice da câmera; confirme primeiro com `lerobot-find-cameras` (a numeração varia conforme a máquina).

- `fourcc: "MJPG"` é opcional e reduz significativamente o consumo de largura de banda das câmeras USB (passa a usar compressão MJPEG); pode ser adicionado em caso de travamentos.

- Se precisar de apenas uma câmera, basta remover a linha correspondente (por exemplo, `top`).

> **⚠️ Nota (dependência do rerun)**: `--display_data=true` requer o pacote de visualização rerun; se não estiver instalado, execute:

```PowerShell
pip install "rerun-sdk>=0.24.0,<0.34.0"
```

> Requer o executável do Rerun Viewer. No Windows, se aparecer `Failed to find Rerun Viewer executable`, significa que falta o visualizador com GUI. **Isso não afeta a teleoperação**; basta remover `--display_data=true`.

---

## Sair

Pressione `Ctrl+C` para parar. O programa automaticamente:

1. Libera o torque dos 8 servos da mão

2. Desconecta as portas seriais do braço seguidor/líder

3. Desconecta as câmeras (se houver)

> **⚠️ Nota**: antes de sair normalmente, **não feche o terminal diretamente**, caso contrário pode restar uma porta serial ocupada. Se, após uma saída anormal, a porta serial ficar ocupada, reconecte o USB ou reinicie o processo do terminal.

---

## Resolução de problemas

|Sintoma|Causa|Solução|
|---|---|---|
|Direção da mão invertida|Direção dos ângulos da mão ou do mapeamento da garra invertida|Ver "Verificação de direção" acima; troque os ângulos ou ajuste o mapeamento|
|Abertura/fechamento excessivo/insuficiente da mão|Calibração imprecisa dos ângulos da mão|Recalibrar a GUI dos ângulos da mão|
|O braço não acompanha|Calibração ausente/porta serial errada|Confirme que o braço seguidor está calibrado e que `--robot.port` está correto|
|Erro do rerun|Dependência de visualização ausente|Remova `--display_data=true`|
|Porta serial ocupada|Saída anormal anterior|Encerre o processo que a ocupa ou reconecte o USB|

