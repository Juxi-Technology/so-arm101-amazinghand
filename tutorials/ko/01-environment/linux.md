# linux

# 단계 1: 환경 구축(Linux)

**Miniforge**를 사용하여 독립된 Python 환경을 만들고 LeRobot 및 AmazingHand 지원을 설치합니다. 본 페이지는 **엄격한 순서**대로 실행하며, 각 코드 블록은 통째로 복사할 수 있습니다.

> 환경 버전: Python 3\.12 · PyTorch ≥ 2\.10 · LeRobot 0\.6\.2(본 리포지토리 커스텀 버전) · 권장 Ubuntu 20\.04/22\.04

---

## 단계 1: Miniforge 설치

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

> 공식 주소(해외 네트워크): `https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh`

---

## 단계 2: conda 국내 미러 설정(중국 본토 네트워크)

```Bash
conda config --remove-key channels
```

```Bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
```

> `pkgs/free`는 서비스 종료(404)되었으므로 추가하지 마세요. 네트워크 제한이 없으면 이 단계를 건너뛸 수 있습니다.

---

## 단계 3: 컴파일 도구 설치(새 시스템에 필수)

새로 설치한 Ubuntu에는 `gcc` 등 컴파일 도구가 없을 수 있으며, `evdev` 등의 패키지를 설치할 때 필요합니다:

```Bash
sudo apt update
sudo apt install -y build-essential
```

---

## 단계 4: 가상 환경 생성

```Bash
conda create -y -n lerobot python=3.12
conda activate lerobot
```

```Bash
python --version
python -c "import struct; print(struct.calcsize('P')*8, 'bit')"
```

> 예상 결과는 `Python 3.12.x` \+ `64 bit`입니다.

---

## 단계 5: ffmpeg 설치(비디오 디코딩 필수)

LeRobot의 비디오 데이터 기록/재생은 ffmpeg에 의존합니다:

```Bash
conda install ffmpeg -c conda-forge -y
```

---

## 단계 6: 프로젝트 의존성 설치

```Bash
cd ~/lerobot-main
pip install -e ".[amazinghand]"
```

`amazinghand` 구성: `feetech-servo-sdk`(암 모터), `rustypot`(핸드 모터), `pygame`(캘리브레이션 GUI), `pyserial`(시리얼 포트).

> pip가 느리면 먼저 국내 미러를 설정합니다:

```Bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 단계 7: 시리얼 포트 권한 설정

```Bash
sudo chmod 666 /dev/ttyACM*
```

> 영구 해결책(udev 규칙, CP210x 칩 대상, VID `10c4`):

```Bash
sudo tee /etc/udev/rules.d/99-servo.rules << 'EOF'
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"
EOF
sudo udevadm control --reload-rules && sudo udevadm trigger
```

---

## 단계 8: 환경 검증

```Bash
python -c "import scservo_sdk, rustypot, pygame, serial, lerobot; print('all OK')"
lerobot-calibrate-amazing-hand --help
```

> `all OK`와 `usage: lerobot-calibrate-amazing-hand ...`가 표시되어야 합니다.

---

## 단계 9: 시리얼 포트 확인

```Bash
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null
```

또는 `lerobot-find-port`. 3개 장치의 경로를 확인합니다(예시 `/dev/ttyACM0`/`/dev/ttyACM1`/`/dev/ttyACM2`, **실제 값으로 교체해야 합니다**).

---

완료 → 단계 2: 캘리브레이션

---

## 문제 해결

|현상|해결|
|---|---|
|`conda` 명령을 찾을 수 없음|`source ~/.bashrc` 또는 `conda init` 후 터미널 다시 열기|
|`pkgs/free` 404|해당 채널은 서비스 종료되었으므로 추가하지 마세요|
|시리얼 포트 `Permission denied`|단계 7 `sudo chmod 666`|
|의존성 설치 불가/느림|pip 국내 미러 설정(단계 6 안내)|
|설치 시 `evdev` 컴파일 오류|단계 3 `sudo apt install build-essential`|
|GPU 학습 시 CUDA 체크가 `False`|단계 5 학습 문서 참조|

