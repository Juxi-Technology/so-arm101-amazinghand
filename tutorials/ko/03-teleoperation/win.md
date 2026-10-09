# win

# 단계 3: 원격 조작(Windows)

본 단계에서는 원격 조작 폐루프를 시작합니다: 리더 암이 팔로워 암의 움직임을 제어하고, 그리퍼가 AmazingHand의 개폐를 제어합니다. 이것은 전체 시스템이 정상적으로 동작하는지 검증하는 핵심 단계입니다.

---

## 사전 조건

- 단계 1: 환경 구축과 단계 2: 캘리브레이션을 완료함

- 3개 장치에 전원을 공급하고 시리얼 포트를 기록함

---

## 원격 조작 실행

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader
```

> `<follower_arm_com>` / `<hand_com>` / `<leader_arm_com>`를 사용자 머신의 실제 COM 번호로 교체하세요(예시 `COM58` / `COM11` / `COM54`).

**예상 동작**:

- 리더 암 5개 관절 → 팔로워 암 추종

- 리더 암 그리퍼 → AmazingHand 개폐(비례 추종: 반쯤 집으면 = 반쯤 닫힘)

> **💡 매개변수 설명**：

- `--robot.type=so101_amazing_hand`：팔로워 암 \+ 핸드 복합 로봇

- `--robot.port`：팔로워 암 시리얼 포트

- `--robot.hand_port`：핸드 시리얼 포트

- `--teleop.type=so101_leader`：리더 암 원격 조작기

- `--teleop.port`：리더 암 시리얼 포트

---

## 최초 실행 시 필수: 방향 검증

시작 후 먼저 **방향 테스트**를 수행하여 다음 두 가지가 모두 올바른지 확인합니다:

|테스트|조작|올바른 현상|
|---|---|---|
|암 추종|리더 암의 각 관절 회전|팔로워 암이 같은 방향으로 추종|
|핸드 개폐|리더 암 그리퍼를 열기/집기|그리퍼가 열림 → 핸드가 열림; 그리퍼를 집음 → 핸드가 닫힘|

> **⚠️ 주의(방향이 반대일 때 대처)**：

- **핸드 개폐 방향이 반대**(그리퍼를 열면 핸드가 닫힘)：핸드 각도 캘리브레이션이 부정확한 것입니다. 캘리브레이션 도구(그리퍼 방향 캘리브레이션 포함)를 다시 실행하면 저장 후 자동으로 반영되며, **수동으로 파일을 수정할 필요가 없습니다**. 단계 2: 캘리브레이션을 참조하세요.

- **그리퍼 매핑 방향이 반대**(그리퍼를 열면 핸드가 닫힘)：위와 동일합니다. 캘리브레이션 시 리더 암 그리퍼를 **열었을** 때 `[Capture Open]`을, **집었을** 때 `[Capture Close]`를 클릭하면 도구가 자동으로 `gripper_open_pos`/`gripper_close_pos`를 기록·저장하고 시작 시 자동으로 로드합니다.

> 수정 후 **원격 조작을 다시 실행**하여 검증합니다.

---

## 비례 추종 검증

방향이 올바르면 비례의 정밀도를 검증합니다:

1. **천천히** 그리퍼를 열기 → 핸드는 **매끄럽게** 열려야 합니다(튐 없음)

2. 그리퍼를 **중간**에서 멈춤 → 핸드도 중간에서 멈춰야 합니다

3. 빠르게 개폐 → 핸드가 빠르게 반응하고 끊김이 없음

> **⚠️ 주의(핸드 개폐가 과도해지는 기존 문제)**：그리퍼가 반쯤 열린 시점에서 핸드가 닫히면, 대부분 핸드 각도 캘리브레이션 시 "열기/주먹" 위치가 부정확한 것입니다. 캘리브레이션 단계 3(핸드 각도 GUI)을 다시 실행하여 더 정확한 개폐 위치를 캘리브레이션하세요.

---

## 선택: 카메라를 포함한 시각화

`--robot.cameras`로 카메라를 연결하고, `--display_data=true`로 Rerun 시각화 창을 엽니다(카메라 이미지 \+ 관절 상태를 실시간 표시):

```PowerShell
lerobot-teleoperate --robot.type=so101_amazing_hand --robot.port=<follower-port> --robot.hand_port=<hand-port> --robot.id=amazing_hand_follower --teleop.type=so101_leader --teleop.port=<leader-port> --teleop.id=amazing_hand_leader --robot.cameras='{wrist: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30, fourcc: "MJPG"},top: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30, fourcc: "MJPG"}}' --display_data=true
```

> **💡 설명**：

- `index_or_path`는 카메라 인덱스입니다. 먼저 `lerobot-find-cameras`로 확인하세요(머신마다 번호가 다릅니다).

- `fourcc: "MJPG"`는 선택 사항이며, USB 카메라의 대역폭 사용량을 크게 줄일 수 있습니다(MJPEG 압축으로 변경). 끊길 때 추가할 수 있습니다.

- 카메라가 하나만 필요하면 해당 행(예 `top`)을 삭제하면 됩니다.

> **⚠️ 주의(rerun 의존성)**：`--display_data=true`에는 rerun 시각화 패키지가 필요합니다. 미설치 시 다음을 실행합니다:

```PowerShell
pip install "rerun-sdk>=0.24.0,<0.34.0"
```

> Rerun Viewer 실행 파일이 필요합니다. Windows에서 `Failed to find Rerun Viewer executable`가 보고되면 GUI 뷰어가 없는 것입니다. **원격 조작에는 영향을 주지 않습니다**. `--display_data=true`를 빼면 됩니다.

---

## 종료

`Ctrl+C`를 누르면 정지합니다. 프로그램이 자동으로:

1. 8개 핸드 서보의 토크를 해제

2. 팔로워 암/리더 암 시리얼 포트를 연결 해제

3. 카메라를 연결 해제(있는 경우)

> **⚠️ 주의**：정상 종료 전에 **터미널을 바로 닫지 마세요**. 그렇지 않으면 시리얼 포트 점유가 남을 수 있습니다. 비정상 종료 후 시리얼 포트가 점유되어 있으면 USB를 다시 꽂거나 터미널 프로세스를 재시작하세요.

---

## 문제 해결

|현상|원인|해결|
|---|---|---|
|핸드 방향이 반대|핸드 각도 또는 그리퍼 매핑이 반대|위 본문 "방향 검증" 참조. 각도를 교환하거나 매핑 조정|
|핸드 개폐가 과도/부족|핸드 각도 캘리브레이션 부정확|핸드 각도 GUI 재캘리브레이션|
|암이 추종하지 않음|캘리브레이션 누락/시리얼 포트 오류|팔로워 암이 캘리브레이션되었는지, `--robot.port`가 올바른지 확인|
|rerun 오류|시각화 의존성 누락|`--display_data=true` 제거|
|시리얼 포트 점유됨|지난번 비정상 종료|점유 프로세스를 닫거나 USB를 다시 꽂기|

