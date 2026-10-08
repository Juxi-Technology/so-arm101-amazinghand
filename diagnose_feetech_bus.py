#!/usr/bin/env python3
"""
Feetech 总线诊断工具

【用途】
  当 lerobot-calibrate / lerobot-teleoperate 报
      "FeetechMotorsBus motor check failed on port ..."
  且 "Full found motor list" 显示为空 {} 时，
  用本脚本定位到底是【供电 / 接线 / 端口】问题，还是【舵机 ID 不对】问题。

【原理】
  lerobot 的 _assert_motors_exist 只 ping 配置里写的那几个 ID（默认 1-6），
  所以它报空有两种可能：
    (a) 总线完全没通（供电、接线、端口问题）
    (b) 舵机有响应，但 ID 不在 1-6 范围内
  本脚本扫描 1-253 全部 ID × 全部常见波特率，找出总线上任何有响应的舵机，
  从而把上面两种情况区分开。

【用法】
  python diagnose_feetech_bus.py /dev/tty.usbmodem5C630502861
  python diagnose_feetech_bus.py COM58
"""
import sys

try:
    import scservo_sdk as scs
except ImportError:
    print("缺少 scservo_sdk，请先执行: pip install 'lerobot[feetech]'")
    sys.exit(1)

# STS3215 的常见波特率（默认 1M）
BAUDRATES = [1_000_000, 500_000, 250_000, 128_000, 115_200, 57_600, 38_400]
STS3215_MODEL_NUMBER = 777


def scan(port: str, baudrate: int) -> dict:
    """在指定波特率下扫描所有 ID，返回 {id: model_number}"""
    found = {}
    try:
        ph = scs.PortHandler(port)
        ph.setBaudRate(baudrate)
        pkt = scs.PacketHandler(0)
        for i in range(1, 254):
            res = pkt.ping(ph, i)
            model, comm = (res[0], res[1]) if isinstance(res, tuple) else (res, 0)
            if comm == 0 and model:
                found[i] = model
        ph.closePort()
    except Exception as e:
        print(f"    [错误] 无法打开端口: {e}")
    return found


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("提示：不知道该填哪个端口时，先运行 `lerobot-find-port`，"
              "或在 macOS 上执行 `ls /dev/tty.usbmodem*`")
        sys.exit(1)

    port = sys.argv[1]
    print(f"扫描端口: {port}")
    print("=" * 56)

    any_found = False
    for baud in BAUDRATES:
        print(f"\n[波特率 {baud:,}]")
        found = scan(port, baud)
        if found:
            any_found = True
            for id_, model in sorted(found.items()):
                tag = "  ← STS3215" if model == STS3215_MODEL_NUMBER else f"  ← 型号号 {model}"
                print(f"    找到舵机  ID={id_}{tag}")
        else:
            print("    无响应")

    print("\n" + "=" * 56)
    if any_found:
        print("【结论】总线是通的，舵机有能力响应。")
        print("  → 问题在 ID 配置：实际 ID 与配置期望的 1-6 不一致。")
        print("  → 解决：用 `lerobot-setup-motors` 逐个重新分配 ID，")
        print("          或修改配置里的电机 ID 以匹配实际。")
    else:
        print("【结论】所有波特率下都无响应 → 总线根本没有通。")
        print("  按以下顺序排查（按发生率从高到低）：")
        print("  1. 舵机电源是否接通 —— 最常见原因！")
        print("     USB 线通常只给控制板供电，舵机需要独立电源（12V 或 5V，看版本）")
        print("  2. 端口是否选对 —— 拔插一次，看端口名是否变化")
        print("  3. 控制板到舵机的线是否插紧、有无断针/断线")
        print("  4. 控制板本身是否上电（指示灯亮否）")
        print("  5. 换 USB 口 / 换数据线再试")


if __name__ == "__main__":
    main()
