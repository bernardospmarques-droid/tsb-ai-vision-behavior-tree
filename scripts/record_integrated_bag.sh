#!/usr/bin/env bash
set -eo pipefail

ROOT="$HOME/tsb_project_clean"
WS="$ROOT/ros2_ws"
BAG_ROOT="$ROOT/evidence/rosbag"
STAMP="$(date +%Y%m%d_%H%M%S)"
BAG="$BAG_ROOT/integrated_$STAMP"

mkdir -p "$BAG_ROOT"

source /opt/ros/jazzy/setup.bash
source "$ROOT/.venv/bin/activate"
source "$WS/install/setup.bash"

echo "[INFO] A gravar para: $BAG"
echo "[INFO] Executa setas e formas na pagina web."
echo "[INFO] No fim, regressa aqui e carrega Ctrl+C."

ros2 bag record \
  \
  --output "$BAG" \
  /vision/canvas_png \
  /vision/image \
  /vision/command \
  /turtle1/cmd_vel \
  /turtle1/pose \
  /rosout
