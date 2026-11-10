# TSB AI Vision and Behavior Tree

Sistema ROS 2 que classifica setas com uma CNN em PyTorch e executa movimentos e formas no Turtlesim através de BehaviorTree.CPP.

## Funcionalidades

- Classificação: `UP`, `DOWN`, `LEFT`, `RIGHT`.
- Movimentos lineares e rotações de aproximadamente 90 graus.
- Quadrado implementado como polígono regular de quatro lados.
- Círculo com velocidades linear e angular simultâneas.
- Polígono regular configurável entre 3 e 12 lados.
- Interface web via rosbridge.
- Edição da árvore no Groot2 e monitorização quando suportada pela licença.

## Arquitetura

```text
Canvas ou imagem
-> /vision/canvas_png ou /vision/image
-> canvas_bridge, quando aplicável
-> vision_node e TurtleVisionCNN
-> /vision/command
-> GetVisionCommand
-> Blackboard {command}
-> Switch6
-> MoveTurtle, DrawSquare, DrawCircle ou DrawRegularPolygon
-> /turtle1/cmd_vel
-> Turtlesim
```

Os botões web publicam `SQUARE`, `CIRCLE` e `REGULAR_POLYGON` diretamente em `/vision/command`. Estes comandos não passam pela CNN.

## Parâmetros principais

### Setas

| Comando | linear.x | angular.z | Duração |
|---|---:|---:|---:|
| `UP` | `+2.0` | `0.0` | `0.8 s` |
| `DOWN` | `-2.0` | `0.0` | `0.8 s` |
| `LEFT` | `0.0` | `+1.5` | `1.0472 s` |
| `RIGHT` | `0.0` | `-1.5` | `1.0472 s` |

### Quadrado

O nó `ExecuteSquare` expõe apenas:

- `move_direction`;
- `turn_direction`;
- `linear_speed`;
- `side_duration`.

A geometria fica protegida dentro de `DrawSquare`:

```text
number_of_sides = 4
angular_speed = 1.5
```

### Polígono regular

Parâmetros editáveis:

```text
number_of_sides: 3 a 12
move_direction: UP ou DOWN
turn_direction: LEFT ou RIGHT
linear_speed
side_duration
angular_speed
```

A duração de cada rotação é calculada por:

```text
turn_duration = 2*pi / (number_of_sides * abs(angular_speed))
```

### Círculo

```text
linear_speed = 2.0
angular_speed = 1.5
duration = 4.1888 s
radius ~= 1.333
```

## Requisitos

- Ubuntu 24.04 LTS;
- ROS 2 Jazzy;
- Python 3.12;
- BehaviorTree.CPP v4;
- PyTorch;
- Turtlesim;
- rosbridge_server;
- Groot2, opcional.

## Preparação e compilação

```bash
cd ~/tsb_project_clean/ros2_ws
source /opt/ros/jazzy/setup.bash
source ~/tsb_project_clean/.venv/bin/activate
colcon build --symlink-install --event-handlers console_direct+
source install/setup.bash
```

## Execução

### Sistema principal

```bash
ros2 launch tsb_bt_core challenge.launch.py
```

O launch inicia `turtlesim_node`, `vision_node` e `bt_executor`.

### Interface web

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

```bash
ros2 run tsb_cv_brain canvas_bridge
```

```bash
cd ~/tsb_project_clean/web
python3 -m http.server 8000
```

Abrir `http://localhost:8000`.

## Groot2

- Editor: abrir `ros2_ws/src/tsb_bt_core/behavior_trees/tree.xml`.
- Monitor: ligar a `localhost:1667`.
- O Monitor é apenas de leitura.
- Depois de guardar alterações ao XML, reiniciar o `bt_executor`.
- Com `--symlink-install`, não é necessário recompilar alterações exclusivamente no XML.
- A versão gratuita do Groot2 pode limitar a monitorização de árvores com mais de 20 nós.

O nome `SelectBehavior_REGULAR_POLYGON_fallback` identifica que `REGULAR_POLYGON` utiliza a saída final do `Switch6`. O port `variable` permanece ligado a `{command}`.

## Testes e resultados

Resultado registado:

```text
13 tests, 13 passed, 0 failed
```

CNN no conjunto de teste:

```text
540 imagens
accuracy = 1.0
erros = 0
```

A accuracy perfeita deve ser interpretada apenas dentro da distribuição do dataset. A validação com setas desenhadas manualmente continua a ser a evidência externa mais relevante.

## Evidências

- Logs: `evidence/square/`, `evidence/circle/`, `evidence/regular_polygon/`.
- Avaliação da CNN: `training/outputs/` e `evidence/model_evaluation.md`.
- Vídeo final integrado: `evidence/final_validation/final_integrated_demo.mp4`.

## Estado validado

- Branch: `main`.
- Commit de referência anterior à limpeza: `0032133`.
- Vídeo final comprimido e incluído no Git.
- Blackboard, web, CNN, formas e Turtlesim integrados.
