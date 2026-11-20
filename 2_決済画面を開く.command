#!/bin/bash
cd "$(dirname "$0")" || exit 1
if [ ! -x .venv/bin/python ]; then
  echo "先にMac環境セットアップ.commandを実行 / Run setup first"
  exit 1
fi
.venv/bin/python mac.py checkout
result=$?
read -r -p "Enterで閉じる / Press Enter to close "
exit "$result"
