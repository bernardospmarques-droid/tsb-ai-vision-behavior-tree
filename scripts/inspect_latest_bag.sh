#!/usr/bin/env bash
set -eo pipefail

ROOT="$HOME/tsb_project_clean"
BAG_ROOT="$ROOT/evidence/rosbag"

source /opt/ros/jazzy/setup.bash

BAG="$(find "$BAG_ROOT" -mindepth 1 -maxdepth 1 -type d \
  -name 'integrated_*' -printf '%T@|%p\n' \
  | sort -nr | head -n 1 | cut -d'|' -f2-)"

if [[ -z "${BAG:-}" ]]; then
  echo "[ERROR] Nao encontrei nenhuma gravacao."
  exit 1
fi

echo "[INFO] Bag: $BAG"
ros2 bag info "$BAG" \
  | tee "$BAG_ROOT/latest_bag_info.txt"
