# README

# SO\-ARM101 \+ AmazingHand 사용 튜토리얼

본 튜토리얼은 **SO\-ARM101 팔로워 암 \+ AmazingHand 정교한 핸드**의 원격 조작, 데이터 수집, 학습 전 과정을 재현하기 위한 것입니다. LeRobot(공식 리포지토리 커스텀 버전)를 기반으로 합니다.

튜토리얼은 **단계**별로 구성되어 있으며, 각 단계는 독립된 디렉터리로 되어 있고 내부는 운영체제에 따라 `win.md`(Windows)와 `linux.md`(Linux) 두 문서로 나뉩니다. 사용하는 운영체제에 맞는 문서를 선택해 읽어 주세요.

---

## 하드웨어 및 소프트웨어 개요

|장치|시리얼 포트(예시, 교체 필요)|서보 모델|설명|
|---|---|---|---|
|리더 암(Leader)|`COM54` / `/dev/ttyACM1`|혼합 모델<br>`sts3125-C001、sts3215-C044、sts3215-C046`|원격 조작 입력, 6번 그리퍼 유지|
|팔로워 암(Follower)|`COM58` / `/dev/ttyACM0`|`sts3215-C018`(1\-5번)|실행 측, 6번 그리퍼 제거|
|AmazingHand 정교한 핸드|`COM11` / `/dev/ttyACM2`|`scs0009`(8개, ID 1\-8)|팔로워 암 말단, 독립 시리얼 포트|

> **⚠️ 시리얼 포트 이름은 머신마다 다릅니다**：위 표는 예시입니다. COM 번호/장치 경로는 PC마다 다르므로, 반드시 `lerobot-find-port`로 본체의 실제 값을 확인하고 모든 명령의 자리표시자 인자를 교체해 주세요.

> 세 장치는 **각각 독립된 시리얼 포트와 독립 전원**이 필요합니다. SCS0009(프로토콜 1)와 STS3215(프로토콜 0)는 동일 버스에서 호환되지 않습니다.

---

## 튜토리얼 디렉터리 구조

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

## 권장 읽기 순서

|순서|단계|Windows|Linux|
|---|---|---|---|
|1|환경 구축|01\-environment/win\.md|01\-environment/linux\.md|
|2|캘리브레이션|02\-calibration/win\.md|02\-calibration/linux\.md|
|3|원격 조작|03\-teleoperation/win\.md|03\-teleoperation/linux\.md|
|4|데이터 수집|04\-data\-collection/win\.md|04\-data\-collection/linux\.md|
|5|모델 학습|05\-training/win\.md|05\-training/linux\.md|
|6|배포 및 평가|06\-deployment/win\.md|06\-deployment/linux\.md|

---

## 단계별 핵심 차이 요약

|항목|Windows|Linux|
|---|---|---|
|Python 환경|Miniconda \+ `conda create -n lerobot python=3.12`|Miniforge \+ 동일한 명령|
|시리얼 포트 이름|`COM54` / `COM58` / `COM11`(예시)|`/dev/ttyACM0/1/2`(예시)|
|시리얼 포트 권한|특별한 설정 불필요|`sudo chmod 666 /dev/ttyACM*` 또는 udev 규칙 필요|
|명령 호출|conda 활성화 후 `lerobot-xxx`|conda 활성화 후 `lerobot-xxx`|
|CUDA 학습|CUDA 버전 torch 수동 설치 필요|공식 지원, 해석이 원활|

---

## 공통 주의사항

1. **먼저 단계 1을 완료한 뒤 이후 단계로 진행하세요**——환경은 이후 모든 명령의 전제입니다.

2. **PC마다 반드시 재캘리브레이션해야 합니다**：특히 핸드 각도(`lerobot-calibrate-amazing-hand`)는 config 안의 각도가 AmazingHand 공식 범용 기본값으로, 백업용일 뿐입니다. `hand_angles.json`이 존재하면 본체 실측값을 우선 로드합니다.

3. **캘리브레이션 파일 위치**：`~/.cache/huggingface/lerobot/calibration/`, 머신을 바꾸면 마이그레이션이나 재캘리브레이션이 필요합니다.

4. **최초 원격 조작 시 반드시 방향을 검증**：그리퍼 열림 ↔ 핸드 열림, 집기 ↔ 핸드 닫힘.

5. 각 단계의 `win.md` / `linux.md`에는 **해당 플랫폼 특유의 주의사항**이 포함되어 있습니다. 끝까지 읽어 주세요.

---

## 문제 해결 진입점

각 단계 문서에 플랫폼별 문제 해결 표가 첨부되어 있습니다. 자주 발생하는 문제:

- conda 미초기화/명령을 찾을 수 없음

- 시리얼 포트 권한 부족(Linux)

- 핸드/암 방향 매핑 오류

- 핸드 각도 미캘리브레이션으로 인한 개폐 이상

각 단계 문서를 참조하세요.

