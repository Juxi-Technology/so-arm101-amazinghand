# SO-ARM101 + AmazingHand Dexterous Manipulation Platform

**English** | [简体中文](README.zh-CN.md)

> Integrating the **AmazingHand 8-DOF dexterous hand** onto the **SO-ARM101 6-DOF robotic arm**, built on the [LeRobot](https://github.com/huggingface/lerobot) framework — covering the full loop of **teleoperation → data collection → imitation learning → autonomous execution**.

---

## Overview

This project delivers a complete hardware integration and software adaptation for a dexterous-hand robotic arm. It addresses three core engineering problems:

| Problem | Solution |
|---|---|
| **Protocol conflict** — the hand's servos (SCS0009, protocol 1) and the arm's servos (STS3215, protocol 0) cannot share a bus | Three physically isolated serial ports with independent power supplies |
| **Driver stack interference** — creating multiple Feetech buses in one process corrupts readings on the first bus | The hand is driven through a separate `rustypot` stack, fully decoupled from the arm's bus |
| **Calibration complexity** — calibrating the open/close pose of an 8-servo parallel mechanism is non-trivial | A purpose-built all-in-one calibration tool: finger angles and gripper direction in a single session, saved automatically |

## Key Features

- **Complete teleoperation loop** — the leader arm's 5 joints drive the follower; its gripper proportionally drives the hand's open/close
- **All-in-one calibration** — `lerobot-calibrate-amazing-hand` provides a GUI for calibrating hand finger angles and leader gripper direction. Results are saved automatically and loaded at startup — **no code changes required**
- **Data collection & training** — synchronized dual-camera capture producing LeRobotDataset v3.0 datasets, ready for ACT and other policies
- **Containerized delivery** — CPU and CUDA Docker images; import and run, no environment setup needed
- **Complete Chinese documentation** — a six-stage tutorial series, split by Windows / Linux

## Hardware Requirements

| Component | Model / Notes |
|---|---|
| Follower arm | SO-ARM101, 5 × `STS3215` (IDs 1–5), **original gripper servo #6 removed** |
| Dexterous hand | AmazingHand, 8 × `SCS0009` (IDs 1–8), **dedicated serial port + separate power supply** |
| Leader arm | SO-ARM101, 6 servos (**gripper #6 retained** as the hand's control input) |
| Cameras | 2 × USB camera, 640×480 @ 30 fps |
| Adapter | 3D printed, mounts the hand onto the follower's wrist |

> ⚠️ **All three devices must have their own serial port and their own power supply.** SCS0009 (protocol 1) and STS3215 (protocol 0) cannot share a bus.

## Quick Start

See **[tutorials/](tutorials/)** for the full walkthrough, organized by stage and split by platform:

| Stage | Windows | Linux |
|---|---|---|
| 1. Environment setup | [win](tutorials/01-environment/win.md) | [linux](tutorials/01-environment/linux.md) |
| 2. Calibration | [win](tutorials/02-calibration/win.md) | [linux](tutorials/02-calibration/linux.md) |
| 3. Teleoperation | [win](tutorials/03-teleoperation/win.md) | [linux](tutorials/03-teleoperation/linux.md) |
| 4. Data collection | [win](tutorials/04-data-collection/win.md) | [linux](tutorials/04-data-collection/linux.md) |
| 5. Training | [win](tutorials/05-training/win.md) | [linux](tutorials/05-training/linux.md) |
| 6. Deployment & evaluation | [win](tutorials/06-deployment/win.md) | [linux](tutorials/06-deployment/linux.md) |

> The tutorial documents are currently in Chinese.

**Environment setup (summary)**:

```bash
conda create -y -n lerobot python=3.12
conda activate lerobot
pip install -e ".[amazinghand,training]"
```

**Common commands**:

```bash
# Calibrate hand finger angles + gripper direction (GUI)
lerobot-calibrate-amazing-hand --hand_port=<hand-port> --leader_port=<leader-port>

# Teleoperation
lerobot-teleoperate \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> --robot.hand_port=<hand-port> \
  --robot.id=amazing_hand_follower \
  --teleop.type=so101_leader --teleop.port=<leader-port> \
  --teleop.id=amazing_hand_leader

# Deploy a trained policy
lerobot-rollout --strategy.type=base \
  --policy.path=<model-dir> \
  --robot.type=so101_amazing_hand \
  --robot.port=<follower-port> --robot.hand_port=<hand-port> \
  --task="Pick up the cube with the dexterous hand"
```

## Containerization

```bash
# Build (on Linux)
bash docker/build_and_export.sh cpu     # CPU image, ~1 GB
bash docker/build_and_export.sh cuda    # CUDA image, ~3.5 GB

# Customer side: import and run
docker load -i dist/lerobot-amazinghand-cpu.tar
```

See **[docker/README_DEPLOY.md](docker/README_DEPLOY.md)** for serial / camera / GUI passthrough configuration.

## Changes Relative to Upstream LeRobot

| Path | Change |
|---|---|
| `src/lerobot/robots/so_amazing_hand/` | **New** — robot definition for the SO-ARM101 + dexterous hand combination |
| `src/lerobot/scripts/lerobot_calibrate_amazing_hand.py` | **New** — all-in-one hand calibration GUI |
| `src/lerobot/robots/so_follower/so_follower.py` | Added retries to bus writes for resilience against transient packet loss |
| `pyproject.toml` | Added the `amazinghand` extra |
| `tutorials/` | **New** — six-stage Chinese tutorial series |
| `docker/Dockerfile.amazinghand.*` | **New** — CPU / CUDA images |

All other directories (`policies/`, `datasets/`, `envs/`, etc.) are unchanged from upstream LeRobot.

## Repository Structure

```
so-arm101-amazinghand/
├── src/lerobot/
│   ├── robots/so_amazing_hand/          # Dexterous-hand arm definition (core of this project)
│   ├── scripts/lerobot_calibrate_amazing_hand.py  # Calibration tool
│   └── ...                              # Remaining code is stock LeRobot
├── tutorials/                           # Six-stage tutorials (Windows / Linux)
├── docker/                              # Containerization
├── diagnose_feetech_bus.py              # Feetech bus diagnostic tool
└── preview_cameras.py                   # Live camera preview tool
```

## Troubleshooting

**Bus reports no motors found** (`FeetechMotorsBus motor check failed`):

```bash
python diagnose_feetech_bus.py /dev/ttyACM0    # Linux
python diagnose_feetech_bus.py COM58           # Windows
```

This script scans every ID across every common baud rate, distinguishing a dead bus from a misconfigured ID.

**Camera fails to open**:

```bash
lerobot-find-cameras opencv       # Confirm the index
python preview_cameras.py         # Live preview
```

## Credits & License

This project builds on the following open-source work:

- **[LeRobot](https://github.com/huggingface/lerobot)** — training and deployment framework (Apache-2.0)
- **[AmazingHand](https://github.com/pollen-robotics/AmazingHand)** — open-source dexterous hand by Pollen Robotics (software Apache-2.0 / mechanical design CC BY 4.0)
- **SO-ARM101** — open-source 6-DOF robotic arm

The code in this repository is released under **Apache-2.0**; see [LICENSE](LICENSE). Hardware designs follow the licenses of their respective upstream projects.
