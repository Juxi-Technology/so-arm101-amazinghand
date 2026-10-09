# SO-ARM101 + AmazingHand — Tutorials

Full walkthrough for reproducing **teleoperation, data collection and training** on the **SO-ARM101 follower arm + AmazingHand dexterous hand**, built on LeRobot.

Each language directory contains the same six stages, and every stage is split by operating system into `win.md` (Windows) and `linux.md` (Linux).

---

## Choose your language

| Language | Directory |
|---|---|
| English | **[en/](en/)** |
| 简体中文 (Simplified Chinese) | [zh-hans/](zh-hans/) |
| 繁體中文 (Traditional Chinese) | [zh-hant/](zh-hant/) |
| Deutsch | [de/](de/) |
| Español | [es/](es/) |
| Français | [fr/](fr/) |
| Italiano | [it/](it/) |
| 日本語 | [ja/](ja/) |
| 한국어 | [ko/](ko/) |
| Português (Brasil) | [pt-br/](pt-br/) |
| Português (Portugal) | [pt-pt/](pt-pt/) |

> 🌐 Also published on the wiki: <https://wiki.juxitech.com/zh-hant/tutorials/robot-arms/so-arm-amazinghand/>

---

## The six stages

| # | Stage | What it covers |
|---|---|---|
| 1 | [01-environment](en/01-environment/) | Miniconda setup, project dependencies, serial port confirmation |
| 2 | [02-calibration](en/02-calibration/) | Leader arm, follower arm, hand finger angles, gripper direction |
| 3 | [03-teleoperation](en/03-teleoperation/) | Running the teleoperation loop and verifying directions |
| 4 | [04-data-collection](en/04-data-collection/) | Recording a LeRobotDataset, replaying it, optional HF upload |
| 5 | [05-training](en/05-training/) | Training an ACT policy, local and cloud GPU |
| 6 | [06-deployment](en/06-deployment/) | Autonomous execution with `lerobot-rollout` |

---

## Hardware prerequisites

| Device | Model | Notes |
|---|---|---|
| Leader arm | SO-ARM101 | 6 servos; **gripper #6 retained** as the hand's control input |
| Follower arm | SO-ARM101 | 5 × `STS3215` (IDs 1–5); **original gripper servo #6 removed** |
| Dexterous hand | AmazingHand | 8 × `SCS0009` (IDs 1–8); **dedicated serial port + separate power** |
| Cameras | 2 × USB camera | 640×480 @ 30 fps (`top` + `wrist`) |

> ⚠️ **All three devices must have their own serial port and their own power supply.** SCS0009 (protocol 1) and STS3215 (protocol 0) cannot share a bus.

---

## Reading order

Follow the stages in order — each one builds on the previous. **Complete Stage 1 first**: the environment is the prerequisite for every command that follows.

Each stage document also carries a troubleshooting table for its platform, plus a general FAQ in the per-language `README.md`.
