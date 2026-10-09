# README

# SO\-ARM101 \+ AmazingHand Tutorial

This tutorial covers the full workflow of teleoperation, data collection, and training for reproducing the **SO\-ARM101 follower arm \+ AmazingHand dexterous hand**, based on LeRobot (a customized version of the official repository).

The tutorial is organized by **stage**, with each stage in its own directory, split internally by operating system into two documents: `win.md` (Windows) and `linux.md` (Linux). Choose the document that matches your operating system.

---

## Hardware and Software Overview

|Device|Serial port (example, must be replaced)|Servo model|Notes|
|---|---|---|---|
|Leader arm|`COM54` / `/dev/ttyACM1`|Mixed models<br>`sts3125-C001, sts3215-C044, sts3215-C046`|Teleoperation input, keeps gripper #6|
|Follower arm|`COM58` / `/dev/ttyACM0`|`sts3215-C018` (No. 1\-5)|Execution side, gripper #6 removed|
|AmazingHand dexterous hand|`COM11` / `/dev/ttyACM2`|`scs0009` (8 units, ID 1\-8)|Follower arm end effector, dedicated serial port|

> **⚠️ Serial port names vary by machine**: The table above is only an example. The COM number/device path differs on every computer, so be sure to use `lerobot-find-port` to confirm your machine's actual values and replace all placeholder parameters in the commands.

> The three devices must each have **their own serial port and their own power supply**. SCS0009 (protocol 1) and STS3215 (protocol 0) are not compatible on the same bus.

---

## Tutorial Directory Structure

```Plaintext
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

## Recommended Reading Path

|Step|Stage|Windows|Linux|
|---|---|---|---|
|1|Environment setup|01\-environment/win\.md|01\-environment/linux\.md|
|2|Calibration|02\-calibration/win\.md|02\-calibration/linux\.md|
|3|Teleoperation|03\-teleoperation/win\.md|03\-teleoperation/linux\.md|
|4|Data collection|04\-data\-collection/win\.md|04\-data\-collection/linux\.md|
|5|Model training|05\-training/win\.md|05\-training/linux\.md|
|6|Deployment and evaluation|06\-deployment/win\.md|06\-deployment/linux\.md|

---

## Quick Reference: Core Differences by Stage

|Aspect|Windows|Linux|
|---|---|---|
|Python environment|Miniconda \+ `conda create -n lerobot python=3.12`|Miniforge \+ the same command|
|Serial port name|`COM54` / `COM58` / `COM11` (examples)|`/dev/ttyACM0/1/2` (examples)|
|Serial port permissions|No special configuration needed|Requires `sudo chmod 666 /dev/ttyACM*` or a udev rule|
|Command invocation|`lerobot-xxx` after activating conda|`lerobot-xxx` after activating conda|
|CUDA training|CUDA torch must be installed manually|Officially supported, resolves smoothly|

---

## General Notes

1. **Get stage 1 working first, then move on to the later stages**—the environment is the prerequisite for every subsequent command.

2. **Every computer must be recalibrated**: especially the hand angles (`lerobot-calibrate-amazing-hand`). The angles in the config are AmazingHand's official generic defaults and serve only as a fallback; when `hand_angles.json` exists, the locally measured values are loaded in preference.

3. **Calibration file location**: `~/.cache/huggingface/lerobot/calibration/`. When switching machines, migrate the file or recalibrate.

4. **Always verify the directions on the first teleoperation**: gripper open ↔ hand open, pinch ↔ hand close.

5. Each stage's `win.md` / `linux.md` includes **platform-specific notes**; please read them in full.

---

## Troubleshooting Entry Point

The stage documents include a troubleshooting table for each platform. Common issues:

- conda not initialized / command not found

- Insufficient serial port permissions (Linux)

- Incorrect hand/arm direction mapping

- Hand angles not calibrated, causing abnormal opening/closing

See the individual stage documents for details.

