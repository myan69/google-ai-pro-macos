#!/usr/bin/env python3
"""Local macOS adapter. Upstream code must be supplied separately."""
import argparse
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
MUMU_ADB = "/Applications/MuMuPlayer Pro.app/Contents/MacOS/MuMu Android Device.app/Contents/MacOS/tools/adb"


def find_adb():
    candidates = [os.environ.get("ADB_PATH"), MUMU_ADB, shutil.which("adb"),
                  str(Path.home() / "Library/Android/sdk/platform-tools/adb")]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("ADBが見つかりません / ADB not found. Set ADB_PATH.")


def adb_run(adb, *args):
    result = subprocess.run([adb, *args], capture_output=True, text=True, timeout=15)
    if result.returncode:
        raise RuntimeError("ADB command failed: " + " ".join(args[:2]))
    return result.stdout.strip()


def select_device(adb, serial=None):
    def connected():
        return [line.split()[0] for line in adb_run(adb, "devices").splitlines()[1:]
                if len(line.split()) == 2 and line.split()[1] == "device"]
    devices = connected()
    if serial and serial not in devices:
        adb_run(adb, "connect", serial)
        devices = connected()
    if not devices and not serial:
        for port in (26624, 26625, 26626):
            try:
                adb_run(adb, "connect", f"127.0.0.1:{port}")
            except (RuntimeError, subprocess.TimeoutExpired):
                continue
            devices = connected()
            if devices:
                break
    if serial:
        if serial not in devices:
            raise RuntimeError("指定端末に接続できません / Selected device unavailable")
        return serial
    if len(devices) != 1:
        raise RuntimeError("端末を1台接続するか--serialを指定 / Connect one device or use --serial")
    return devices[0]


def load_upstream():
    path = ROOT / "vendor" / "ultra0.py"
    if not path.is_file():
        raise RuntimeError("vendor/ultra0.py が必要です / Supply your own upstream file; see README")
    spec = importlib.util.spec_from_file_location("local_upstream", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    required = ("ensure_root", "ensure_module_apk", "ensure_vending", "launch_app", "ensure_frida_server", "build_js")
    if not all(callable(getattr(module, name, None)) for name in required):
        raise RuntimeError("未対応の元ファイル / Incompatible upstream file")
    return module


def prepare(module, adb, serial):
    module.ADB, module.SERIAL = adb, serial
    module.ensure_root()
    for pid in module.sh("shell", "pidof frida-server").split():
        if pid.isdigit():
            module.sh("shell", "kill", pid)
    time.sleep(1)
    for package in (module.PKG, module.VENDING):
        if not module.sh("shell", "pm path " + package):
            raise RuntimeError("必要なGoogleアプリがありません / Required Google app missing")
    module.ensure_module_apk()
    module.ensure_vending()
    if not module.sh("shell", "pidof " + module.VENDING):
        raise RuntimeError("Playストアを開けません / Play Store did not start")
    pid = module.sh("shell", "pidof " + module.PKG)
    if not pid.isdigit():
        pid = str(module.launch_app())
    if not pid.isdigit() or int(pid) <= 0:
        raise RuntimeError("Google Oneを開けません / Google One did not start")
    # Let the supplied code provision its matching server, then restart without preload.
    module.ensure_frida_server()
    for server_pid in module.sh("shell", "pidof frida-server").split():
        if server_pid.isdigit():
            module.sh("shell", "kill", server_pid)
    time.sleep(1)
    module.sh("shell", "nohup " + module.FRIDA_REMOTE + " -D -P >/dev/null 2>&1 &")
    for _ in range(20):
        if module.sh("shell", "pidof frida-server"):
            return int(pid)
        time.sleep(0.5)
    raise RuntimeError("Frida server did not start")


def query(module, serial, pid, checkout=False, wait=35):
    import frida
    device = frida.get_device(serial, timeout=10)
    session = device.attach(pid)
    events = []

    def on_message(message, data):
        if message.get("type") == "error":
            events.append({"ev": "script_error"})
        elif isinstance(message.get("payload"), dict):
            events.append(message["payload"])

    try:
        script = session.create_script(module.build_js("pro12", list_only=not checkout))
        script.on("message", on_message)
        script.load()
        time.sleep(wait)
        return events
    finally:
        session.detach()


def print_summary(events):
    for event in events:
        if event.get("ev") == "offer":
            print(f"Offer: {event.get('id')} | period={event.get('period')} | price_micros={event.get('micros')}")
        elif event.get("ev") == "launched":
            print("Checkout response:", event.get("code"))
        elif "err" in str(event.get("ev", "")) or str(event.get("ev", "")).startswith("no_"):
            print("Result:", event.get("ev"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "list", "checkout"))
    parser.add_argument("--serial")
    args = parser.parse_args()
    if sys.platform != "darwin":
        raise RuntimeError("この補助ツールはmacOS用です / This adapter supports macOS")
    adb = find_adb()
    serial = select_device(adb, args.serial)
    print("Device:", serial, flush=True)
    # Upstream output may contain tokens. Do not echo or save it.
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        module = load_upstream()
        pid = prepare(module, adb, serial)
        events = [] if args.action == "check" else query(module, serial, pid, args.action == "checkout")
    print("Environment ready.")
    print_summary(events)
    if args.action == "checkout":
        print("決済画面で条件を確認してください / Review checkout and confirm manually if desired.")
    # Deliberately never call upstream process(), confirm_zero(), or account/card helpers.
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"Stopped: {type(error).__name__}. Check device, upstream version and README.", file=sys.stderr)
        sys.exit(1)
