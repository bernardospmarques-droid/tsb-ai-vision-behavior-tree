# TSB AI Vision and Behavior Tree

Sistema desenvolvido em ROS 2 Jazzy que integra uma CNN em PyTorch, Behavior Trees (BehaviorTree.CPP), Turtlesim e uma interface web para demonstrar uma pipeline completa de perceção, decisão e atuação.

## Objetivo

O sistema classifica setas através de uma CNN e converte essas previsões em comandos executados por uma Behavior Tree.

Além dos comandos provenientes da visão, a interface web permite executar diretamente formas geométricas pré-definidas.

## Funcionalidades

- Classificação de setas: `UP`, `DOWN`, `LEFT` e `RIGHT`
- Execução de movimentos através de Behavior Trees
- Desenho de:
  - `SQUARE`
  - `CIRCLE`
  - `REGULAR_POLYGON`
- Interface web baseada em rosbridge
- Edição e visualização da árvore em Groot2
- Integração completa com ROS 2

## Arquitetura

```text
Imagem
    ↓
CNN (PyTorch)
    ↓
/vision/command
    ↓
Behavior Tree
    ↓
Ações de movimento
    ↓
/turtle1/cmd_vel
    ↓
Turtlesim
```

Os comandos das formas geométricas são publicados diretamente pela interface web para `/vision/command`.

## Estrutura do Sistema

```text
CNN (PyTorch)
    ↓
vision_node
    ↓
BehaviorTree.CPP
    ↓
MoveTurtle
DrawSquare
DrawCircle
DrawRegularPolygon
    ↓
Turtlesim
```

## Requisitos

- Ubuntu 24.04 LTS
- ROS 2 Jazzy
- Python 3.12
- PyTorch
- BehaviorTree.CPP v4
- Turtlesim
- rosbridge_server
- Groot2 (opcional)

## Compilação

```bash
cd ~/tsb_project_clean/ros2_ws

source /opt/ros/jazzy/setup.bash
source ~/tsb_project_clean/.venv/bin/activate

colcon build --symlink-install

source install/setup.bash
```

## Execução

### Sistema Principal

```bash
ros2 launch tsb_bt_core challenge.launch.py
```

O launch inicia:

- turtlesim_node
- vision_node
- bt_executor

### Interface Web

Iniciar o rosbridge:

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

Iniciar o canvas bridge:

```bash
ros2 run tsb_cv_brain canvas_bridge
```

Iniciar o servidor web:

```bash
cd web
python3 -m http.server 8000
```

Abrir:

```text
http://localhost:8000
```

## Groot2

Abrir:

```text
ros2_ws/src/tsb_bt_core/behavior_trees/tree.xml
```

Monitorização:

```text
localhost:1667
```

Após alterações ao XML:

1. Guardar a árvore.
2. Reiniciar o `bt_executor`.

Com `--symlink-install`, não é necessário recompilar alterações exclusivamente no XML.

## Comandos Suportados

### CNN

A CNN reconhece:

```text
UP
DOWN
LEFT
RIGHT
```

### Interface Web

A interface permite executar diretamente:

```text
SQUARE
CIRCLE
REGULAR_POLYGON
```

## Resultados

### CNN

Conjunto de teste:

```text
540 imagens
accuracy = 1.0
0 classificações incorretas
```

### Integração

Sistema validado com:

- CNN
- ROS 2
- Behavior Tree
- Interface Web
- Groot2
- Turtlesim

## Evidências

A pasta:

```text
evidence/final_validation/
```

contém:

- vídeo final integrado;
- resultados dos testes;
- validação final do sistema;
- evidências de funcionamento dos componentes.

## Estado Final

- CNN integrada em ROS 2
- Behavior Tree funcional
- Interface web operacional
- Groot2 configurado
- Integração completa validada
- Demonstração final disponível em evidências
