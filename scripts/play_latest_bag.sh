#!/usr/bin/env bash
set -eo pipefail

ROOT="$HOME/tsb_project_clean"
WS="$ROOT/ros2_ws"
BAG_ROOT="$ROOT/evidence/rosbag"

source /opt/ros/jazzy/setup.bash
source "$ROOT/.venv/bin/activate"
source "$WS/install/setup.bash"

BAG="$(find "$BAG_ROOT" -mindepth 1 -maxdepth 1 -type d \
  -name 'integrated_*' -printf '%T@|%p\n' \
  | sort -nr | head -n 1 | cut -d'|' -f2-)"

if [[ -z "${BAG:-}" ]]; then
  echo "[ERROR] Nao encontrei nenhuma gravacao."
  exit 1
fi

echo "[INFO] A reproduzir: $BAG"
echo "[INFO] O bt_executor deve estar desligado para evitar comandos duplicados."
ros2 bag play "$BAG" --rate 1.0
