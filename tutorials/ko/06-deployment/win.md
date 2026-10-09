# win

# 단계 6: 배포 및 평가(Windows)

본 단계에서는 학습된 정책을 로드하여 로봇이 **스스로 작업을 수행**하게 하고, 평가 영상을 기록하여 효과를 검증합니다. 이것은 전체 흐름의 마무리이며, 학습 성과를 확인하는 핵심이기도 합니다.

---

## 사전 조건

- 단계 5: 모델 학습을 완료함

- 학습으로 `outputs/train/soarm_amazing_hand_pick/checkpoints/last/pretrained_model/`가 생성됨

- 카메라 인덱스를 기록함

---

## 단계 1: 모델 파일 확인

```PowerShell
# 모델 디렉터리 존재 여부 확인
dir outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model
```

`model.safetensors` 등의 모델 파일이 포함되어 있어야 합니다.

> **⚠️ 주의(모델 경로)**：`--policy.path`는 `pretrained_model` 디렉터리(설정 \+ 가중치 포함)를 가리켜야 하며, checkpoint 루트 디렉터리가 아닙니다.

---

## 단계 2: 배포 및 평가

```PowerShell
lerobot-record `
  --robot.type=so101_amazing_hand `
  --robot.port=<follower-port> `
  --robot.hand_port=<hand-port> `
  --robot.id=amazing_hand_follower `
  --robot.cameras='{
    wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},
    top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}
  }' `
  --policy.path=outputs\train\soarm_amazing_hand_pick\checkpoints\last\pretrained_model `
  --dataset.repo_id=soarm_amazing_hand_pick_eval `
  --dataset.root=D:\lerobot_data `
  --dataset.push_to_hub=false `
  --dataset.num_episodes=10 `
  --dataset.single_task="Pick up the cube with the dexterous hand" `
  --display_data=true
```

> `<follower_arm_com>` / `<hand_com>`를 실제 COM 번호로 교체합니다; 카메라 `index_or_path`를 사용자의 카메라 인덱스로 교체합니다.

> **💡 설명**：`lerobot-record`를 사용하지만**추가하지 않음 ****`--teleop.type`**，정책이 로봇을 자율적으로 제어합니다(수동 원격 조작 대체). 데이터는 평가 세트로 저장됩니다. `--dataset.root` / `--dataset.push_to_hub=false`는 단계 4와 일치하며, 순수 로컬 저장이라 HF 로그인이 필요 없습니다.

---

## 평가 조작

1. 로봇 \+ 핸드를 **시작 위치**로 리셋

2. Enter를 눌러 시작: 정책이 자율적으로 작업을 수행합니다

3. **성공적으로 집었는지** 관찰합니다(각 에피소드 종료 시 Enter를 눌러 계속)

4. `num_episodes`회 반복

**평가 지표**：성공률 = 성공 에피소드 수 / 전체 에피소드 수

> **⚠️ 주의 1(리셋 일관성)**：각 에피소드는 **동일한 시작 위치**에서 시작합니다. 그렇지 않으면 정책의 일반화가 실패하여 성공률이 실제보다 낮게 나옵니다.

> **⚠️ 주의 2(안전)**：최초 자율 실행은 **손으로 받치며/저속으로** 관찰하여 정책 동작이 합리적인지 확인하는 것을 권장합니다. 정책이 예상치 못한 동작을 할 수 있습니다.

> **⚠️ 주의 3(성공률 예상)**：ACT는 20 에피소드 데이터에서 보통 50\-80% 성공률을 보입니다. 예상보다 낮으면 돌아가서 데이터를 추가 기록하거나 학습 스텝 수를 조정하세요.

---

## 반복 최적화

평가 성공률이 만족스럽지 않으면 우선순위에 따라 조정합니다:

|우선순위|최적화 항목|조작|
|---|---|---|
|1|고품질 데이터 추가 기록|단계 4로 돌아가 더 일관된 데이터를 20\-30 에피소드 추가 기록|
|2|학습 스텝 수 증가|단계 5로 돌아가 `--steps=100000`|
|3|시작 위치 일치 확인|평가 시 각 에피소드를 엄격히 리셋|
|4|작업 설명 조정|`single_task`가 작업과 일치하는지 확인|

---

이로써 SO\-ARM101 \+ AmazingHand의 **완전한 폐루프**가 완성됩니다: 캘리브레이션 → 원격 조작 → 수집 → 학습 → 배포.

---

## 문제 해결

|현상|원인|해결|
|---|---|---|
|모델 로드 실패|경로 오류/불완전|`--policy.path`가 `pretrained_model` 디렉터리를 가리키는지 확인|
|정책이 움직이지 않음|카메라/관측 오류|카메라 인덱스가 학습 시와 일치하는지 확인; `--display_data` 화면 확인|
|정책이 제멋대로 움직임|시작 위치 불일치/데이터 품질 저하|엄격히 리셋; 데이터 추가 기록|
|학습 시와 성능이 다름|환경 차이|카메라, 조명, 물체 위치가 기록 시와 일치하는지 확인|

