# README

# Tutorial de uso do SO\-ARM101 \+ AmazingHand

Este tutorial aborda o fluxo completo de teleoperação, coleta de dados e treinamento para reproduzir o **braço seguidor SO\-ARM101 \+ mão dextra AmazingHand**, com base no LeRobot (versão personalizada do repositório oficial).

O tutorial é organizado por **etapas**, cada etapa em um diretório próprio, com os documentos divididos por sistema operacional em `win.md` (Windows) e `linux.md` (Linux). Escolha o documento correspondente ao seu sistema operacional para leitura.

---

## Visão geral de hardware e software

|Dispositivo|Porta serial (exemplo, substituir)|Modelo do servo|Descrição|
|---|---|---|---|
|Braço líder (Leader)|`COM54` / `/dev/ttyACM1`|Modelos mistos<br>`sts3125-C001、sts3215-C044、sts3215-C046`|Entrada da teleoperação, mantém a garra nº 6|
|Braço seguidor (Follower)|`COM58` / `/dev/ttyACM0`|`sts3215-C018` (nº 1\-5)|Lado de execução, remove a garra nº 6|
|Mão dextra AmazingHand|`COM11` / `/dev/ttyACM2`|`scs0009` (8 unidades, ID 1\-8)|Extremidade do braço seguidor, porta serial independente|

> **⚠️ O nome da porta serial varia conforme a máquina**: a tabela acima é apenas um exemplo. O número COM/caminho do dispositivo é diferente em cada computador; use `lerobot-find-port` para confirmar os valores reais da sua máquina e substituir todos os parâmetros de exemplo nos comandos.

> Os três dispositivos devem ter **porta serial própria e alimentação independente**. O SCS0009 (protocolo 1) e o STS3215 (protocolo 0) não são compatíveis no mesmo barramento.

---

## Estrutura de diretórios do tutorial

```Plaintext
tutorials/
├── README.md                          # 本文件（总览）
├── 01-environment/                    # 阶段一：环境搭建
│   ├── win.md                         #   Windows 环境搭建
│   └── linux.md                       #   Linux 环境搭建
├── 02-calibration/                    # 阶段二：标定
│   ├── win.md
│   └── linux.md
├── 03-teleoperation/                  # 阶段三：遥操作
│   ├── win.md
│   └── linux.md
├── 04-data-collection/                # 阶段四：数据采集
│   ├── win.md
│   └── linux.md
├── 05-training/                       # 阶段五：模型训练
│   ├── win.md
│   └── linux.md
└── 06-deployment/                     # 阶段六：部署与评估
    ├── win.md
    └── linux.md
```

---

## Caminho de leitura recomendado

|Passo|Etapa|Windows|Linux|
|---|---|---|---|
|1|Configuração do ambiente|01\-environment/win\.md|01\-environment/linux\.md|
|2|Calibração|02\-calibration/win\.md|02\-calibration/linux\.md|
|3|Teleoperação|03\-teleoperation/win\.md|03\-teleoperation/linux\.md|
|4|Coleta de dados|04\-data\-collection/win\.md|04\-data\-collection/linux\.md|
|5|Treinamento do modelo|05\-training/win\.md|05\-training/linux\.md|
|6|Implantação e avaliação|06\-deployment/win\.md|06\-deployment/linux\.md|

---

## Resumo das principais diferenças por etapa

|Aspeto|Windows|Linux|
|---|---|---|
|Ambiente Python|Miniconda \+ `conda create -n lerobot python=3.12`|Miniforge \+ o mesmo comando|
|Nome da porta serial|`COM54` / `COM58` / `COM11` (exemplo)|`/dev/ttyACM0/1/2` (exemplo)|
|Permissões da porta serial|Nenhuma configuração especial necessária|Requer `sudo chmod 666 /dev/ttyACM*` ou regras udev|
|Chamada de comandos|Após ativar o conda, `lerobot-xxx`|Após ativar o conda, `lerobot-xxx`|
|Treinamento com CUDA|Necessário instalar o torch CUDA manualmente|Suporte oficial, resolução fluida|

---

## Observações gerais

1. **Execute a Etapa 1 primeiro, depois avance para as etapas seguintes** — o ambiente é o pré-requisito de todos os comandos posteriores.

2. **Cada computador deve ser recalibrado**: em especial os ângulos da mão (`lerobot-calibrate-amazing-hand`); os ângulos no config são o padrão genérico oficial do AmazingHand, servindo apenas de reserva; quando `hand_angles.json` existe, os valores medidos na máquina local são carregados com prioridade.

3. **Local do arquivo de calibração**: `~/.cache/huggingface/lerobot/calibration/`; ao trocar de máquina, é necessário migrar ou recalibrar.

4. **Na primeira teleoperação, verifique sempre a direção**: garra aberta ↔ mão aberta, pinçada ↔ mão fechada.

5. Os arquivos `win.md` / `linux.md` de cada etapa contêm **notas específicas daquela plataforma**; leia na íntegra.

---

## Ponto de entrada para resolução de problemas

Os documentos das etapas incluem a tabela de resolução de problemas de cada plataforma. Problemas comuns:

- conda não inicializado/comando não encontrado

- Permissões insuficientes na porta serial (Linux)

- Mapeamento de direção da mão/braço incorreto

- Ângulos da mão não calibrados, causando abertura/fechamento anormais

Consulte os documentos de cada etapa.

