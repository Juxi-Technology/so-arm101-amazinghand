# win

# 단계 1: 환경 구축(Windows)

**Miniconda**를 사용하여 독립된 Python 환경을 만들고 LeRobot 및 AmazingHand 지원을 설치합니다. 본 페이지는 **엄격한 순서**대로 실행하며, 각 코드 블록은 통째로 복사할 수 있습니다.

> 환경 버전: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2(본 리포지토리 커스텀 버전)

---

## 단계 1: Miniconda 설치

**명령줄 설치**(PowerShell, 권장)——중국 본토 네트워크에서는 칭화 미러 사용:

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

PowerShell을 다시 연 뒤 검증:

```PowerShell
conda --version
```

> **GUI 설치**(선택): 공식 사이트 https://repo\.anaconda\.com/miniconda/Miniconda3\-latest\-Windows\-x86\_64\.exe 에서 설치 패키지를 다운로드하고 더블클릭하여 설치, **"Add to PATH"** 를 체크합니다.

> `conda` 명령을 찾을 수 없으면 **Anaconda Prompt**(시작 메뉴)를 PowerShell 대신 사용합니다.

---

## 단계 2: conda 국내 미러 설정(중국 본토 네트워크)

**먼저 기본 소스를 비우고 칭화 미러를 추가합니다**(새 Miniconda는 기본적으로 `repo.anaconda.com` 공식 소스를 포함하여 ToS 검사를 유발하고 느립니다):

```PowerShell
conda config --remove-key channels
```

```PowerShell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free`는 서비스 종료(404)되었으므로 추가하지 마세요. 네트워크 제한이 없으면 이 단계를 건너뛸 수 있습니다.

---

## 단계 3: 가상 환경 생성

```PowerShell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```PowerShell
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> 예상 결과는 `Python 3.12.x` \+ `64 bit`입니다. `conda activate`에 `(lerobot)` 프리픽스가 없으면 문서 말미의 문제 해결을 참조하세요.

---

## 단계 4: ffmpeg 설치(비디오 디코딩 필수)

LeRobot의 비디오 데이터 기록/재생은 ffmpeg에 의존합니다:

```PowerShell
conda install ffmpeg -c conda-forge -y
```

> 국내 네트워크가 느리면 설정해 둔 칭화 conda\-forge 채널을 사용할 수 있습니다. 설치하지 않으면 데이터 기록/비디오 재생 시 오류가 발생합니다.

---

## 단계 5: 프로젝트 의존성 설치

```PowerShell
cd D:\Project\lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` 구성: `feetech-servo-sdk`(암 모터), `rustypot`(핸드 모터), `pygame`(캘리브레이션 GUI), `pyserial`(시리얼 포트).

> pip가 느리면 먼저 국내 미러를 설정합니다:

```PowerShell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 단계 6: 환경 검증

```PowerShell
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> `all OK`와 `usage: lerobot-calibrate-amazing-hand ...`가 표시되어야 합니다.

---

## 단계 7: 시리얼 포트 확인

```PowerShell
lerobot-find-port
```

장치 관리자 → 포트\(COM 및 LPT\)에서 3개 장치의 COM 번호를 확인합니다(예시 `COM54`/`COM58`/`COM11`, **실제 값으로 교체해야 합니다**). COM 번호는 분리/연결 후 바뀌므로 다시 실행하여 확인합니다.

---

완료 → 단계 2: 캘리브레이션

---

## 문제 해결

|현상|해결|
|---|---|
|`conda`가 명령이 아님|터미널 다시 열기 / Anaconda Prompt / `conda init powershell`|
|ToS 오류(repo\.anaconda\.com)|단계 2에서 channels를 비우고 칭화 소스만 남기기; 또는 `conda tos accept ...`|
|`pkgs/free` 404|해당 채널은 서비스 종료되었으므로 추가하지 마세요|
|`conda activate`에 프리픽스 없음|실행 정책 문제, 아래 참조|
|의존성 설치 불가/느림|pip 국내 미러 설정(단계 5 안내)|

**conda activate에 `(lerobot)` 프리픽스가 없음**(Windows에서 흔함):

```PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "D:\Software\Miniconda3\shell\condabin\conda-hook.ps1"
conda activate lerobot
```

> `D:\Software\Miniconda3`는 사용자의 Miniconda 설치 경로로 교체하세요.

