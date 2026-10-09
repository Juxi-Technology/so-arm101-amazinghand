# linux

# 단계 5: 모델 학습(Linux)

본 단계에서는 수집한 데이터셋으로 정책(ACT 등)을 학습하여 배포 가능한 모델을 만듭니다. **Linux는 GPU 학습에 최적의 환경입니다**——CUDA 버전 torch 의존성이 자동으로 해석되어 수동 설정이 필요 없습니다.

---

## 사전 조건

- 단계 4: 데이터 수집을 완료함

- NVIDIA GPU(권장), CUDA 드라이버(`nvidia-smi`로 확인 가능)

- 데이터셋을 기록함(로컬 캐시에서 확인 가능)

---

## 단계 1: GPU 환경 확인

```Bash
# CUDA 드라이버 확인
nvidia-smi

# torch에서 CUDA 사용 가능 여부 확인
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**예상 출력**：`CUDA: True | GPU: <your_gpu_name>`

> **⚠️ 주의(CUDA torch)**：`CUDA: False`라면 CPU 버전 torch가 설치된 것입니다. CUDA 버전을 재설치하세요:

```Bash
# 공식 저장소 (해외 네트워크)
pip install torch --index-url https://download.pytorch.org/whl/cu128

# 중국 본토 네트워크에서는 알리바바 클라우드 미러 우선 사용
pip install torch --index-url https://mirrors.aliyun.com/pytorch-wheels/cu128
```

> 또는 CPU로 학습합니다(`--policy.device=cpu`, 다만 속도가 훨씬 느립니다).

> **💡 팁**：`pip install -e ".[amazinghand]"`는 Linux에서 보통 GPU 버전 torch를 해석합니다(CUDA 환경이 감지된 경우). 그렇지 않다면 위 명령으로 재설치하세요.

---

## 단계 2: 학습

```Bash
lerobot-train \
  --dataset.repo_id=soarm_amazing_hand_pick \
  --dataset.root=~/lerobot_data \
  --policy.type=act \
  --output_dir=outputs/train/soarm_amazing_hand_pick \
  --job_name=soarm_amazing_hand_pick \
  --policy.device=cuda \
  --wandb.enable=false \
  --policy.push_to_hub=false \
  --steps=60000
```

> **💡 설명**：`--dataset.repo_id`와 `--dataset.root`는 단계 4의 기록 시와 **완전히 일치**해야 합니다(`repo_id=soarm_amazing_hand_pick`, `root=~/lerobot_data`). 그러면 로컬 데이터셋을 읽을 수 있고 HF 로그인이 필요 없습니다.

---

## 매개변수 설명

|매개변수|설명|
|---|---|
|`--dataset.repo_id`|데이터셋 이름(기록 시와 일치)|
|`--dataset.root`|데이터셋 로컬 경로(기록 시와 일치)|
|`--policy.type`|정책 유형. `act`가 일반적인 선택|
|`--output_dir`|학습 출력 디렉터리(checkpoints, 로그)|
|`--job_name`|작업 이름(로그 구분용)|
|`--policy.device`|`cuda`(GPU) 또는 `cpu`|
|`--wandb.enable`|가중치 로그. `false`로 끄면 됨(wandb 계정 불필요)|
|`--policy.push_to_hub`|모델을 HF로 푸시할지 여부. `false`는 로컬만|
|`--steps`|학습 스텝 수|

---

## 학습 과정 설명

- **checkpoints**：각 스텝마다 자동으로 `outputs/train/soarm_amazing_hand_pick/checkpoints/`에 저장됩니다

- **로그**：터미널에 loss 등 지표를 실시간 표시합니다

- **소요 시간**：60000 스텝은 소비자용 GPU에서 보통 수 시간입니다(그래픽카드에 따라 다름)

> **⚠️ 주의 1(스텝 수 조정)**：`--steps=60000`은 ACT의 전형적인 값입니다. 단순한 작업은 30000으로 줄이고, 복잡한 작업은 100000\+까지 늘릴 수 있습니다. loss 수렴을 관찰하세요.

> **⚠️ 주의 2(학습 중단 후 재개)**：중단 후 **동일한 매개변수의 명령**을 다시 실행하면 마지막 checkpoint부터 계속합니다.

> **⚠️ 주의 3(wandb)**：loss 곡선을 시각화하려면 `--wandb.enable=true`를 켤 수 있습니다(`wandb login` 필요). 기본은 꺼짐입니다.

> **⚠️ 주의 4(헤드리스 서버)**：SSH/디스플레이 없는 서버에서 학습하는 경우 GUI에 의존하지 않도록 하세요(학습 자체에는 디스플레이가 필요 없습니다). `--display_data` 관련 매개변수를 사용하면 디스플레이 서버가 필요합니다.

> **⚠️ 주의 5(백그라운드 학습)**：장시간 학습에는 `nohup ... &` 또는 `tmux`로 프로세스를 유지하여 SSH 연결 끊김으로 인한 중단을 피하는 것을 권장합니다:

```Bash
tmux new -s train
lerobot-train --dataset.repo_id=...
# Ctrl+B 후 D로 분리; tmux attach -t train으로 다시 접속
```

---

본 단계를 완료한 후 단계 6: 배포 및 평가로 진행합니다.

---

## 문제 해결

|현상|원인|해결|
|---|---|---|
|`CUDA: False`|CPU 버전 torch|CUDA 버전 torch 재설치|
|VRAM 부족(OOM)|배치 크기 과대|`--policy.batch_size=8` 또는 그 이하|
|데이터셋을 찾을 수 없음|repo\_id/root 불일치|기록 시와 `--dataset.repo_id` 및 `--dataset.root`가 완전히 일치하는지 확인|
|학습 중 SSH 끊김|프로세스 강제 종료|`tmux`/`nohup`으로 백그라운드 학습|
|`wandb` 오류|미로그인|`--wandb.enable=false` 또는 `wandb login`|

