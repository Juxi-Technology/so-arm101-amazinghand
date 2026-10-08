# SO-ARM101 + AmazingHand Tutorial

> 🌐 **English** | [简体中文 (Chinese)](https://wiki.juxitech.com/zh-hant/tutorials/robot-arms/so-arm-amazinghand/)

This tutorial covers the complete workflow for reproducing teleoperation, data collection, and training on the **SO-ARM101 follower arm + AmazingHand dexterous hand**, based on LeRobot (the customized version in this repository).

The tutorial is organized by **stage**. Each stage has its own directory, which contains two documents split by operating system: `win.md` (Windows) and `linux.md` (Linux). Read the document that matches your operating system.

---

## Hardware and software overview

| Device | Serial port (example, needs replacing) | Servo model | Description |
|---|---|---|---|
| Leader arm | `COM54` / `/dev/ttyACM1` | Mixed models | Teleoperation input; gripper #6 retained |
| Follower arm | `COM58` / `/dev/ttyACM0` | `sts3215-C018` (No. 1-5) | Execution end; gripper #6 removed |
| AmazingHand dexterous hand | `COM11` / `/dev/ttyACM2` | `scs0009` (8 servos, IDs 1-8) | At the end of the follower arm; dedicated serial port |

> **⚠️ Serial port names vary by machine:** The table above is only an example. COM numbers and device paths differ from computer to computer. Always use `lerobot-find-port` to confirm the actual values on your machine, and replace the placeholder parameters in every command.

> The three devices must each have **an independent serial port and an independent power supply**. SCS0009 (protocol 1) and STS3215 (protocol 0) are not compatible on the same bus.

---

## Tutorial directory structure

```
tutorials/
├── README.md                          # This file (overview)
├── 01-environment/                    # Stage 1: Environment setup
│   ├── win.md                         #   Windows environment setup
│   └── linux.md                       #   Linux environment setup
├── 02-calibration/                    # Stage 2: Calibration
│   ├── win.md
│   └── linux.md
├── 03-teleoperation/                  # Stage 3: Teleoperation
│   ├── win.md
│   └── linux.md
├── 04-data-collection/                # Stage 4: Data collection
│   ├── win.md
│   └── linux.md
├── 05-training/                       # Stage 5: Model training
│   ├── win.md
│   └── linux.md
└── 06-deployment/                     # Stage 6: Deployment and evaluation
    ├── win.md
    └── linux.md
```

---

## Recommended reading path

| Step | Stage | Windows | Linux |
|---|---|---|---|
| 1 | Environment setup | [01-environment/win.md](01-environment/win.md) | [01-environment/linux.md](01-environment/linux.md) |
| 2 | Calibration | [02-calibration/win.md](02-calibration/win.md) | [02-calibration/linux.md](02-calibration/linux.md) |
| 3 | Teleoperation | [03-teleoperation/win.md](03-teleoperation/win.md) | [03-teleoperation/linux.md](03-teleoperation/linux.md) |
| 4 | Data collection | [04-data-collection/win.md](04-data-collection/win.md) | [04-data-collection/linux.md](04-data-collection/linux.md) |
| 5 | Model training | [05-training/win.md](05-training/win.md) | [05-training/linux.md](05-training/linux.md) |
| 6 | Deployment and evaluation | [06-deployment/win.md](06-deployment/win.md) | [06-deployment/linux.md](06-deployment/linux.md) |

---

## Key differences by stage at a glance

| Aspect | Windows | Linux |
|---|---|---|
| Python environment | Miniconda + `conda create -n lerobot python=3.12` | Miniforge + the same command |
| Serial port names | `COM54` / `COM58` / `COM11` (examples) | `/dev/ttyACM0/1/2` (examples) |
| Serial port permissions | No special configuration needed | Requires `sudo chmod 666 /dev/ttyACM*` or a udev rule |
| Command invocation | `lerobot-xxx` after activating conda | `lerobot-xxx` after activating conda |
| CUDA training | CUDA torch must be installed manually | Officially supported; resolves smoothly |

---

## General notes

1. **Get Stage 1 working before moving on to later stages** — the environment is the prerequisite for every command that follows.
2. **Every computer must be recalibrated**: especially the hand angles (`lerobot-calibrate-amazing-hand`). The angles in the config are AmazingHand's official generic defaults and serve only as a fallback; when `hand_angles.json` exists, the locally measured values are loaded preferentially.
3. **Calibration file location**: `~/.cache/huggingface/lerobot/calibration/` — when switching machines, migrate it or recalibrate.
4. **Always verify directions on the first teleoperation run**: gripper open ↔ hand open, pinch ↔ hand closed.
5. Each stage's `win.md` / `linux.md` contains **platform-specific notes** — please read them in full.

---

## Troubleshooting

Each stage document includes a troubleshooting table for its platform. The following is a summary of **cross-stage common issues**:

| Symptom | Cause | Solution |
|---|---|---|
| `FeetechMotorsBus motor check failed` | Bus not responding, or servo IDs don't match the configuration | Run `python diagnose_feetech_bus.py <serial port>` to locate the problem (scans all IDs × all baud rates) |
| `uv run` reports 32/64-bit / numpy import errors | Wrong interpreter bitness | Recreate with `uv venv --python <absolute path to a 64-bit interpreter>` |
| `uv` reports a cross-drive `os error 17` | Cache spans multiple disks | Set `UV_CACHE_DIR` / `TMPDIR` to the same disk |
| Leader arm calibration reports a model 2307 error | Arm bus polluted | Confirm the hand bus is not connected at the same time; this project avoids it by running the hand over rustypot |
| Hand opens/closes in the wrong direction | Angle semantics reversed | Recalibrate the hand, or swap open / close in `hand_angles.json` |
| Hand open/close ratio doesn't match | Gripper mapping direction is wrong | Measure the `gripper.pos` for gripper open/closed, then adjust `gripper_open_pos` / `gripper_close_pos` |
| Hand driver reports `Operation timed out` | Serial port busy / timing | Confirm the hand's serial port is not occupied, then retry |
| No GUI when calibrating the hand | Wrong command used | You must use `lerobot-calibrate-amazing-hand` (not `lerobot-calibrate`) |
| `--display_data=true` reports a rerun error | Visualization dependency missing | Drop the flag, or install `lerobot[viz]` + Rerun Viewer |
| Recording crashes as soon as it starts | Voice announcements (TTS) block the control loop | Add `--play_sounds=false` |
| Camera won't open / frame timeouts | Index changed, or camera USB state stuck | Use `lerobot-find-cameras` to confirm the index; unplug and replug the camera to reset it |
| Opening two cameras at once fails | Open-order issue | Put the camera with the larger index earlier in the cameras configuration |

---

## Frequently Asked Questions (FAQ)

**Q: Why doesn't the dexterous hand use lerobot's `RangeFinderGUI` for calibration?**

A: The dexterous hand runs on its own `rustypot` serial stack (to work around lerobot's dual-bus mutual-pollution flaw) and does not use `FeetechMotorsBus`. It therefore uses the dedicated `lerobot-calibrate-amazing-hand` GUI to calibrate the open/close angles.

**Q: What is the relationship between `hand_angles.json` and the default values in the config?**

A: `hand_open_angles` / `hand_close_angles` in the config are **fallback defaults** (AmazingHand's official generic values); when `hand_angles.json` exists, the locally measured values are **loaded preferentially**. After recalibrating the hand, no code changes are needed.

**Q: Do I need to recalibrate when switching to a different computer?**

A: Yes. Calibration files are located in `~/.cache/huggingface/lerobot/calibration/`; when switching machines, migrate that directory or recalibrate. `hand_angles.json` is also in this directory.

**Q: What are the differences between Windows / Linux / macOS?**

A: The commands themselves are identical; the differences are concentrated in these places:

| Aspect | Windows | Linux | macOS |
|---|---|---|---|
| Serial port names | `COMx` | `/dev/ttyACM*` | `/dev/cu.*` (prefer `cu.` over `tty.`) |
| Virtual environment path | `.venv\Scripts\` | `.venv/bin/` | `.venv/bin/` |
| Serial port permissions | No configuration needed | Requires `sudo chmod 666 /dev/ttyACM*` | No configuration needed |

**Q: Do the three devices need independent power supplies?**

A: Yes, they must. SCS0009 (protocol 1) and STS3215 (protocol 0) cannot share the same bus; moreover, mixing lerobot serial stacks in the same process causes mutual pollution — which is exactly why this project runs the hand on an independent rustypot stack.

**Q: Where is the trained model?**

A: For deployment, use `outputs/train/<task name>/checkpoints/last/pretrained_model/` (containing `config.json` + weights). `--policy.path` must point to this directory, not the checkpoint root directory.

