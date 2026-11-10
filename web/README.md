# Interface web

A interface permite desenhar setas para a CNN e executar formas diretamente pela Behavior Tree.

## Botões

- `Limpar seta`: limpa apenas o canvas.
- `Limpar desenho`: chama `/clear` e mantém a pose da tartaruga.
- `Reiniciar Turtlesim`: chama `/reset`.
- `Classificar seta`.
- `Quadrado`.
- `Círculo`.
- `Polígono regular`.

## Execução

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
ros2 run tsb_cv_brain canvas_bridge
cd ~/tsb_project_clean/web
python3 -m http.server 8000
```

Abrir `http://localhost:8000`.

A classificação requer `vision_node` e `canvas_bridge`. As formas precisam de `bt_executor`, `turtlesim_node`, `rosbridge_server` e do servidor HTTP.
