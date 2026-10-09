# win

# Etapa 1: Configuração do ambiente (Windows)

Utilize o **Miniconda** para criar um ambiente Python isolado e instalar o LeRobot e o suporte ao AmazingHand. Esta página deve ser executada em **ordem estrita**; cada bloco de código pode ser copiado por inteiro.

> Versão do ambiente: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2 (versão personalizada deste repositório)

---

## Passo 1: Instalar o Miniconda

**Instalação por linha de comandos** (PowerShell, recomendado) — para redes da China continental, utilize o mirror da Tsinghua:

```PowerShell
curl.exe -L -o Miniconda3-latest-Windows-x86_64.exe https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Windows-x86_64.exe
```

```PowerShell
$installDir = "C:\Users\$env:USERNAME\miniconda3"
Start-Process -Wait .\Miniconda3-latest-Windows-x86_64.exe -ArgumentList "/S", "/D=$installDir"
```

```PowerShell
C:\Users\$env:USERNAME\miniconda3\Scripts\conda.exe init powershell
```

Reabra o PowerShell e verifique:

```PowerShell
conda --version
```

> **Instalação gráfica** (opcional): transfira o instalador de https://repo\.anaconda\.com/miniconda/Miniconda3\-latest\-Windows\-x86\_64\.exe, clique duas vezes para instalar e marque **"Add to PATH"**.

> Se o comando `conda` não for encontrado, utilize o **Anaconda Prompt** (menu Iniciar) em vez do PowerShell.

---

## Passo 2: Configurar os mirrors domésticos do conda (rede da China continental)

**Primeiro limpe os canais padrão, depois adicione o mirror da Tsinghua** (um Miniconda novo traz o canal oficial `repo.anaconda.com` por padrão, o que dispara a verificação de ToS e deixa tudo lento):

```PowerShell
conda config --remove-key channels
```

```PowerShell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> O `pkgs/free` foi descontinuado (404), não o adicione. Se a rede não tiver restrições, salte este passo.

---

## Passo 3: Criar o ambiente virtual

```PowerShell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```PowerShell
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> Esperado: `Python 3.12.x` \+ `64 bit`. Se `conda activate` não mostrar o prefixo `(lerobot)`, ver a resolução de problemas no fim do documento.

---

## Passo 4: Instalar o ffmpeg (necessário para descodificação de vídeo)

A gravação/reprodução de dados de vídeo do LeRobot depende do ffmpeg:

```PowerShell
conda install ffmpeg -c conda-forge -y
```

> Se a rede doméstica estiver lenta, pode utilizar o canal conda\-forge da Tsinghua já configurado. Não instalar causará erro na gravação de dados/reprodução de vídeo.

---

## Passo 5: Instalar as dependências do projeto

```PowerShell
cd D:\Project\lerobot-main
pip install -e ".[amazinghand]"
```

O `amazinghand` inclui: `feetech-servo-sdk` (motores do braço), `rustypot` (motores da mão), `pygame` (GUI de calibração), `pyserial` (porta série).

> Se o pip estiver lento, configure primeiro um mirror doméstico:

```PowerShell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## Passo 6: Verificar o ambiente

```PowerShell
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> Deve mostrar `all OK` e `usage: lerobot-calibrate-amazing-hand ...`.

---

## Passo 7: Confirmar as portas série

```PowerShell
lerobot-find-port
```

No Gestor de Dispositivos → Portas \(COM e LPT\), confirme os números COM dos três dispositivos (exemplo `COM54`/`COM58`/`COM11`, **substitua pelos seus valores reais**). O número COM muda após reconectar; execute novamente para confirmar.

---

Concluído → Etapa 2: Calibração

---

## Resolução de problemas

|Sintoma|Solução|
|---|---|
|`conda` não é um comando|Reabrir o terminal / Anaconda Prompt / `conda init powershell`|
|Erro de ToS (repo\.anaconda\.com)|Passo 2: limpar os channels e deixar apenas o mirror da Tsinghua; ou `conda tos accept ...`|
|`pkgs/free` 404|Esse canal foi descontinuado, não o adicione|
|`conda activate` sem prefixo|Problema de política de execução, ver abaixo|
|Dependências não instalam/lentidão|Configure o mirror doméstico do pip (aviso do passo 5)|

**conda activate sem o ****`(lerobot)`**** prefixo** (comum no Windows):

```PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "D:\Software\Miniconda3\shell\condabin\conda-hook.ps1"
conda activate lerobot
```

> Substitua `D:\Software\Miniconda3` pelo caminho de instalação do seu Miniconda.

