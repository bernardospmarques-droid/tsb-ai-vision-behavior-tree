#!/usr/bin/env bash
set -eo pipefail

ROOT="$HOME/tsb_project_clean"
WS="$ROOT/ros2_ws"
OUT="$ROOT/evidence/final_validation"

mkdir -p "$OUT"

source /opt/ros/jazzy/setup.bash
source "$ROOT/.venv/bin/activate"

cd "$WS"
rm -rf build/tsb_bt_core install/tsb_bt_core
colcon build \
  --symlink-install  \
  --packages-select tsb_bt_core tsb_cv_brain \
  --event-handlers console_direct+

source install/setup.bash

colcon test \
  --packages-select tsb_bt_core \
  --event-handlers console_direct+ \
  2>&1 | tee "$OUT/colcon_test.txt"

colcon test-result --verbose \
  2>&1 | tee "$OUT/colcon_test.txt"

cd "$WS/src/tsb_cv_brain"
python3 -m pytest -v \
  2>&1 | tee "$OUT/python.txt"

python3 -m py_compile \
  tsb_cv_brain/*.py \
  test/*.py

echo "[OK] Compilacao e testes concluidos."
