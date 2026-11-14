#!/usr/bin/env bash
set -eo pipefail

ROOT="$HOME/tsb_project_clean"
WS="$ROOT/ros2_ws"
TREE="$WS/src/tsb_bt_core/behavior_trees/tree_prepost_demo.xml"
LOG="$ROOT/evidence/pre_post_conditions/execution.log"
mkdir -p "$(dirname "$LOG")"

source /opt/ros/jazzy/setup.bash
source "$ROOT/.venv/bin/activate"

cd "$WS"
colcon build \
  --symlink-install \
  --packages-select tsb_bt_core \
  --event-handlers console_direct+

source install/setup.bash

echo "[INFO] Arvore de demonstracao: $TREE"
echo "[INFO] Publica um comando noutro terminal, por exemplo:"
echo "  ros2 topic pub --once /vision/command std_msgs/msg/String \"{data: SQUARE}\""
echo
echo "[INFO] Para Groot2: localhost:1668"

ros2 run tsb_bt_core bt_executor \
  --ros-args \
  -p tree_file:="$TREE" \
  -p groot_port:=1668 \
  -p run_once:=true \
  2>&1 | tee "$LOG"
