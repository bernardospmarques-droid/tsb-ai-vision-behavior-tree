#!/usr/bin/env bash
set +u

ROOT="$HOME/tsb_project_clean"
WS="$ROOT/ros2_ws"
LOGS="$ROOT/runtime_logs"
WEB="$ROOT/web"
VENV_PYTHON="$ROOT/.venv/bin/python"

cd "$ROOT" || exit 1

echo "============================================"
echo "A terminar processos antigos"
echo "============================================"

pkill -f vision_node 2>/dev/null || true
pkill -f canvas_bridge 2>/dev/null || true
pkill -f bt_executor 2>/dev/null || true
pkill -f turtlesim_node 2>/dev/null || true
pkill -f rosbridge_websocket 2>/dev/null || true
pkill -f rosapi_node 2>/dev/null || true
pkill -f "http.server 8000" 2>/dev/null || true
pkill -f challenge.launch.py 2>/dev/null || true

sleep 3

source /opt/ros/jazzy/setup.bash || exit 1
source "$WS/install/setup.bash" || exit 1

ros2 daemon stop >/dev/null 2>&1 || true
sleep 1
ros2 daemon start >/dev/null 2>&1 || true
sleep 2

MODEL_PATH="$(
    find "$ROOT" \
        -type f \
        -name "arrow_cnn_best.pth" \
        -not -path "*/backup*/*" \
        -print \
        -quit
)"

if [ -z "$MODEL_PATH" ]; then
    echo "[ERRO] arrow_cnn_best.pth nao encontrado."
    exit 1
fi

if [ ! -x "$VENV_PYTHON" ]; then
    echo "[ERRO] Python da .venv nao encontrado:"
    echo "$VENV_PYTHON"
    exit 1
fi

if ! "$VENV_PYTHON" -c "import torch, rclpy" 2>/dev/null; then
    echo "[ERRO] A .venv nao consegue importar torch e rclpy."
    exit 1
fi

mkdir -p "$LOGS"
rm -f "$LOGS"/*.log "$LOGS"/*.pid

echo "[OK] Modelo: $MODEL_PATH"

echo "[1/6] A iniciar Turtlesim"
nohup ros2 run turtlesim turtlesim_node \
    > "$LOGS/turtlesim.log" 2>&1 &
echo $! > "$LOGS/turtlesim.pid"

sleep 2

echo "[2/6] A iniciar Behavior Tree"
nohup ros2 run tsb_bt_core bt_executor \
    > "$LOGS/bt_executor.log" 2>&1 &
echo $! > "$LOGS/bt_executor.pid"

sleep 2

echo "[3/6] A iniciar Vision Node com PyTorch"
nohup "$VENV_PYTHON" \
    "$WS/src/tsb_cv_brain/tsb_cv_brain/vision_node.py" \
    --ros-args \
    -p model_path:="$MODEL_PATH" \
    -p minimum_confidence:=0.75 \
    > "$LOGS/vision_node.log" 2>&1 &
echo $! > "$LOGS/vision_node.pid"

sleep 6

echo "[4/6] A iniciar Canvas Bridge"
nohup "$VENV_PYTHON" \
    "$WS/src/tsb_cv_brain/tsb_cv_brain/canvas_bridge.py" \
    --ros-args \
    -p canvas_topic:=/vision/canvas_png \
    -p image_topic:=/vision/image \
    > "$LOGS/canvas_bridge.log" 2>&1 &
echo $! > "$LOGS/canvas_bridge.pid"

sleep 4

echo "[5/6] A iniciar Rosbridge"
nohup ros2 launch \
    rosbridge_server \
    rosbridge_websocket_launch.xml \
    > "$LOGS/rosbridge.log" 2>&1 &
echo $! > "$LOGS/rosbridge.pid"

sleep 5

echo "[6/6] A iniciar servidor Web"
cd "$WEB" || exit 1
nohup python3 -m http.server 8000 \
    > "$LOGS/web.log" 2>&1 &
echo $! > "$LOGS/web.pid"

sleep 4

source /opt/ros/jazzy/setup.bash
source "$WS/install/setup.bash"

echo
echo "============================================"
echo "VERIFICACAO DOS PROCESSOS"
echo "============================================"

for process in turtlesim bt_executor vision_node canvas_bridge rosbridge web; do
    pid_file="$LOGS/$process.pid"

    if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        echo "[OK] $process ativo, PID $(cat "$pid_file")"
    else
        echo "[ERRO] $process terminou"
    fi
done

echo
echo "============================================"
echo "NOS ROS"
echo "============================================"
ros2 node list

echo
echo "============================================"
echo "TOPICO DE ENTRADA"
echo "============================================"
ros2 topic info /vision/canvas_png 2>/dev/null || \
    echo "[ERRO] /vision/canvas_png indisponivel"

echo
echo "============================================"
echo "TOPICO DE SAIDA"
echo "============================================"
ros2 topic info /vision/command 2>/dev/null || \
    echo "[ERRO] /vision/command indisponivel"

echo
echo "============================================"
echo "PORTAS WEB"
echo "============================================"
ss -ltn | grep -E ":8000|:9090" || \
    echo "[ERRO] Portas 8000/9090 incompletas"

echo
echo "============================================"
echo "ULTIMAS LINHAS DO VISION NODE"
echo "============================================"
tail -n 20 "$LOGS/vision_node.log"

echo
echo "============================================"
echo "ARRANQUE CONCLUIDO"
echo "Web: http://localhost:8000/index.html"
echo "Limite de confianca: 0.80"
echo "Logs: $LOGS"
echo "============================================"
