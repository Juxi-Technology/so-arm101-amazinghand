# win

# 단계 4: 데이터 수집(Windows)

본 단계에서는 원격 조작 데이터셋을 기록합니다: 사람이 조작하는 가운데 "관절각 \+ 카메라 이미지" 샘플을 수집하여 이후 학습에 사용합니다. 데이터셋 품질이 정책의 효과를 직접 좌우하므로, **조작은 규범적이고 일관되어야 합니다**. 본 단계는 **전 과정을 로컬에서 기록하며 HF 로그인이 필요 없습니다**.

---

## 사전 조건

- 단계 3: 원격 조작을 완료하고 방향이 올바른지 검증함

- 카메라를 연결하고 인덱스를 기록함(`lerobot-find-cameras`)

- 로컬 데이터셋 저장 경로를 결정함(본문 예시는 `D:\lerobot_data`, 사용자 정의 가능)

---

## 단계 1: 카메라 인덱스 확인

```PowerShell
lerobot-find-cameras
```

카메라 번호를 기록합니다. 예를 들어:

- 0번: 손목 카메라(wrist)

- 1번: 상단 카메라(top)

> **⚠️ 주의(카메라 인덱스)**：`index_or_path`는 카메라 인덱스(0/1/2\.\.\.) 또는 비디오 스트림 경로입니다. PC마다 번호가 다르므로 반드시 먼저 확인하세요.

---

## 단계 2: 데이터셋 기록(로컬 저장, 로그인 불필요)

```PowerShell
lerobot-record --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data --dataset.push_to_hub=false --dataset.num_episodes=20 --dataset.single_task="Pick up the cube with the dexterous hand" --display_data=true
```

> `<follower_arm_com>` / `<hand_com>` / `<leader_arm_com>`를 실제 COM 번호로 교체합니다; 카메라 `index_or_path`를 사용자의 카메라 인덱스로 교체합니다.

> **💡 설명**：

- `--dataset.root=D:\lerobot_data`：데이터셋을 지정한 **로컬 경로**에 저장하며, **HF 로그인이 필요 없습니다**(작성하지 않으면 기본적으로 `%USERPROFILE%\.cache\huggingface\lerobot\datasets\...`에 저장됩니다).

- `--dataset.push_to_hub=false`：**업로드를 비활성화**합니다(기본적으로 HF로 푸시를 시도하며 로그인이 필요합니다). 데이터셋을 공유해야 할 때만 `true`로 변경합니다.

- `--dataset.repo_id=soarm_amazing_hand_pick`：데이터셋 이름입니다. 학습 시 **동일한 이름**으로 참조합니다.

- `--display_data=true`에는 rerun이 필요합니다(미설치 시 `pip install "rerun-sdk>=0.24.0,<0.34.0"`). 또는 해당 인자를 제거합니다(기록에는 영향 없음).

---

## 매개변수 설명

|매개변수|설명|
|---|---|
|`--robot.cameras`|카메라 설정. `index_or_path`는 카메라 인덱스, `width/height/fps`는 **필수**|
|`--dataset.repo_id`|데이터셋 이름(로컬 식별용)|
|`--dataset.root`|데이터셋 로컬 저장 경로. **순수 로컬 기록 시 반드시 추가**하여 기본 경로가 제어 불가능해지는 것을 방지|
|`--dataset.push_to_hub`|`false`=로컬만(기본 권장); `true`=HF로 푸시(로그인 필요)|
|`--dataset.num_episodes`|기록 에피소드 수|
|`--dataset.episode_time_s`|**에피소드당 최대 기록 초**(기본 60). 작업이 일찍 끝나면 Enter로 조기 종료할 수 있고, 초과하면 해당 에피소드가 자동 종료됨|
|`--dataset.single_task`|작업 설명. 데이터셋 메타데이터에 기록됨|
|`--display_data=true`|기록 화면을 실시간 표시(선택)|

---

## 기록 조작 규범

**에피소드별 흐름**：

1. 로봇 암 \+ 핸드를 **시작 위치**로 리셋

2. 터미널에서 Enter를 눌러 기록 시작

3. 리더 암을 조작하여 작업 수행(예: 블록 집기). **동작은 느리고 일관되게**

4. 작업 완료 후 Enter를 눌러 이 에피소드를 종료(**누르지 않으면 최대 60초 기록**되며, `--dataset.episode_time_s`로 제어되고 시간이 되면 자동 종료)

5. `num_episodes`에 도달할 때까지 반복

> **⚠️ 주의 1(시작 위치 일치)**：각 에피소드는 **동일한 시작 위치**에서 시작하여 데이터 분포의 혼란을 방지합니다. 고정된 리셋 자세를 정하는 것을 권장합니다.

> **⚠️ 주의 2(동작 일관성)**：동일한 작업에는 유사한 조작 궤적(접근 각도, 파지 위치, 속도)을 사용하면 정책이 더 빠르고 안정적으로 학습합니다.

> **⚠️ 주의 3(기록 품질)**：품질이 낮은 것을 많이 기록하기보다 고품질을 적게 기록하는 편이 낫습니다. 20 에피소드는 ACT의 출발점이며, 복잡한 작업은 30\-50 에피소드를 권장합니다.

> **⚠️ 주의 4(카메라 실시간성)**：기록 시 카메라 가림이나 강한 빛 변화를 피하세요. 이미지 일관성이 일반화에 영향을 줍니다.

---

## 데이터 저장

- **로컬 기록**：데이터는 `--dataset.root`로 지정한 디렉터리에 저장됩니다(예시 `D:\lerobot_data\soarm_amazing_hand_pick`).

- **학습 참조**：학습 시 **동일한 ****`--dataset.repo_id`**** \+ ****`--dataset.root`** 를 사용하면 되며, 수동으로 파일을 옮길 필요가 없습니다:

```PowerShell
lerobot-train --dataset.repo_id=soarm_amazing_hand_pick --dataset.root=D:\lerobot_data ...
```

- **HF 로그인 시나리오**(선택)：데이터셋을 클라우드에 공유해야 할 때 `--dataset.push_to_hub=true`로 변경합니다(`huggingface-cli login` 필요). 로컬 학습만이라면 **필요하지 않습니다**.

> **⚠️ 주의(로컬 vs 클라우드)**：기본 튜토리얼은 전 과정 로컬이며, `--dataset.push_to_hub=false`로 HF 로그인이 트리거되지 않음을 보장합니다. 데이터셋을 공유하고 싶을 때만 `true`를 추가합니다.

---

## 단계 3: 재생 검증(선택이지만 권장)

기록 완료 후 `lerobot-replay`로 특정 에피소드의 데이터를 재생하여 **데이터 품질 \+ 로봇 동작 기록이 올바른지**를 검증할 수 있습니다. 재생 시 로봇이 해당 에피소드의 동작(핸드 개폐 포함)을 자동으로 재현합니다.

```PowerShell
lerobot-replay `
  --robot.type=so101_amazing_hand `
  --robot.port=<follower-port> `
  --robot.hand_port=<hand-port> `
  --robot.id=amazing_hand_follower `
  --dataset.repo_id=soarm_amazing_hand_pick `
  --dataset.root=D:\lerobot_data `
  --dataset.episode=0
```

> `<follower_arm_com>` / `<hand_com>`를 실제 COM 번호로 교체합니다; `--dataset.episode`는 재생할 에피소드 번호입니다(**0부터 시작**, 예를 들어 20 에피소드를 기록했다면 `0`\~`19`).

> **💡 설명**：재생 전에 팔로워 암 \+ 핸드를 **시작 위치로 되돌려** 동작 충돌을 방지합니다; 재생 중에는 로봇이 스스로 움직이므로 **수동으로 개입하지 마세요**. 재생 동작이 기록 시와 명백히 다르면 데이터 품질에 문제가 있는 것이므로 해당 에피소드를 다시 기록하는 것을 권장합니다.

---

본 단계를 완료한 후 단계 5: 모델 학습으로 진행합니다.

---

## 문제 해결

|현상|원인|해결|
|---|---|---|
|카메라를 찾을 수 없음|인덱스 오류/드라이버 누락|`lerobot-find-cameras`로 확인; OpenCV/카메라 드라이버 설치|
|기록 중단|시리얼 포트 타임아웃|3개 장치의 시리얼 포트가 점유되지 않았는지 확인 후 재시도|
|이미지가 전부 검정/깨짐|카메라 설정 오류|`index_or_path`/`fps` 확인|
|데이터셋이 비어 있음|정상적으로 기록되지 않음|각 에피소드에서 Enter로 시작/종료했는지 확인|

