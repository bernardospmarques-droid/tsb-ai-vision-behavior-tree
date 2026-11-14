#!/usr/bin/env bash
set -eo pipefail

ROOT="$HOME/tsb_project_clean"
DATASET="${1:-$HOME/sa_recrutamento_ai/dataset/arrow_dataset/extracted/Direction}"
OUTPUT="$ROOT/training/outputs"
WEIGHTS="$ROOT/training/weights"
LOG="${TMPDIR:-/tmp}/tsb_training.log"

cd "$ROOT"
source /opt/ros/jazzy/setup.bash
source "$ROOT/.venv/bin/activate"

if [[ ! -d "$DATASET" ]]; then
  echo "[ERROR] Dataset nao encontrado: $DATASET"
  echo "Uso alternativo:"
  echo "  $0 /caminho/para/Direction"
  exit 1
fi

mkdir -p "$OUTPUT" "$WEIGHTS"

python3 "$ROOT/training/check_duplicates.py" \
  2>&1 | tee "$ROOT/training/outputs/duplicates.log"

python3 "$ROOT/training/train.py" \
  --dataset "$DATASET" \
  --output "$OUTPUT" \
  --weights "$WEIGHTS" \
  --epochs 30 \
  --batch-size 64 \
  --learning-rate 0.001 \
  --workers 2 \
  --patience 7 \
  --seed 42 \
  2>&1 | tee "$LOG"

python3 "$ROOT/training/evaluate.py" \
  --dataset "$DATASET" \
  --checkpoint "$WEIGHTS/arrow_cnn_best.pth" \
  --output "$OUTPUT" \
  --batch-size 64 \
  --workers 2 \
  --seed 42 \
  2>&1 | tee "${TMPDIR:-/tmp}/tsb_evaluation.log"

sha256sum \
  "$ROOT/training/weights/arrow_cnn_best.pth" \
  "$WEIGHTS/arrow_cnn_best.pth" \
  | tee "$ROOT/evidence/final_validation/checkpoint_sha256.txt"

echo
echo "[OK] Reproducao concluida."
echo "[INFO] O hash pode ser diferente devido a GPU, CUDA e bibliotecas."
echo "[INFO] Compara sobretudo accuracy, loss, classes e matriz de confusao."
