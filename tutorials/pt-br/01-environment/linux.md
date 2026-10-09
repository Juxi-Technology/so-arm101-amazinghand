# linux

# Etapa 1: Configuração do ambiente (Linux)

Use o **Miniforge** para criar um ambiente Python isolado e instalar o LeRobot e o suporte ao AmazingHand. Esta página deve ser executada em **ordem estrita**; cada bloco de código pode ser copiado por inteiro.

> Versão do ambiente: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (versão personalizada deste repositório) · Ubuntu 20\.04/22\.04 recomendado

---

## Passo 1: Instalar o Miniforge

```Bash
wget "https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-$(uname)-$(uname -m).sh"
```

```Bash
bash Miniforge3-$(uname)-$(uname -m).sh -b
~/miniforge3/bin/conda init
source ~/.bashrc
```

```Bash
conda --version
```

> Endereço oficial (rede no exterior): `https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh`

---

## Passo 2: Configurar os mirrors domésticos do conda (rede da China continental)

```Bash
conda config --remove-key channels
```

```Bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> O `pkgs/free` foi descontinuado (404), não o adicione. Se a rede não tiver restrições, pule este passo.

---

## Passo 3: Instalar as ferramentas de compilação (necessário em sistemas novos)

Um Ubuntu recém-instalado pode não ter ferramentas de compilação como o `gcc`, necessárias ao instalar pacotes como o `evdev`:

```Bash
sudo apt update
sudo apt install -y build-essential
```

---

## Passo 4: Criar o ambiente virtual

```Bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```Bash
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Esperado: `Python 3.12.x` \+ `64 bit`.

---

## Passo 5: Instalar o ffmpeg (necessário para decodificação de vídeo)

A gravação/reprodução de dados de vídeo do LeRobot depende do ffmpeg:

```Bash
conda install ffmpeg -c conda-forge -y
```

---

## Passo 6: Instalar as dependências do projeto

```Bash
cd ~/lerobot-main
pip install -e ".[amazinghand]"
```

O `amazinghand` inclui: `feetech-servo-sdk` (motores do braço), `rustypot` (motores da mão), `pygame` (GUI de calibração), `pyserial` (porta serial).

> Se o pip estiver lento, configure primeiro um mirror doméstico:

```Bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Passo 7: Configurar as permissões da porta serial

```Bash
sudo chmod 666 /dev/ttyACM*
```

> Solução permanente (regras udev, para o chip CP210x, VID `10c4`):

```Bash
sudo tee /etc/udev/rules.d/99-servo.rules << 'EOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## Passo 8: Verificar o ambiente

```Bash
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> Deve mostrar `all OK` e `usage: lerobot-calibrate-amazing-hand ...`.

---

## Passo 9: Confirmar as portas seriais

```Bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

Ou `lerobot-find-port`. Confirme os caminhos dos três dispositivos (exemplo `/dev/ttyACM0`/`/dev/ttyACM1`/`/dev/ttyACM2`, **substitua pelos seus valores reais**).

---

Concluído → Etapa 2: Calibração

---

## Resolução de problemas

|Sintoma|Solução|
|---|---|
|Comando `conda` não encontrado|`source ~/.bashrc` ou reabrir o terminal após `conda init`|
|`pkgs/free` 404|Esse canal foi descontinuado, não o adicione|
|`Permission denied` na porta serial|Passo 7 `sudo chmod 666`|
|Dependências não instalam/lentidão|Configure o mirror doméstico do pip (aviso do passo 6)|
|Erro de compilação do `evdev` na instalação|Passo 3 `sudo apt install build-essential`|
|Verificação CUDA no treinamento com GPU retorna `False`|Ver o documento de treinamento da Etapa 5|

