#!/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  command -v python3.12 >/dev/null || { echo "Python 3.12をインストールしてください / Install Python 3.12"; exit 1; }
  python3.12 -m venv .venv
fi
.venv/bin/python -m pip install -r requirements.txt
echo "完了 / Ready. Read README.md before running the launchers."
read -r -p "Enterで閉じる / Press Enter to close "
