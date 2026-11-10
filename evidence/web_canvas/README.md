# Demonstração ponta a ponta da interface web

## Botões

- `Limpar`;
- `Classificar seta`;
- `Quadrado`;
- `Círculo`;
- `Polígono regular`.

## Pipeline das setas

```text
Canvas HTML5
-> rosbridge_server
-> /vision/canvas_png
-> canvas_bridge
-> /vision/image
-> vision_node
-> TurtleVisionCNN
-> /vision/command
-> GetVisionCommand
-> Blackboard {command}
-> SelectBehavior
-> MoveTurtle
-> Turtlesim
```

A CNN classifica apenas `UP`, `DOWN`, `LEFT` e `RIGHT`.

## Pipeline das formas

```text
Botão web
-> rosbridge_server
-> /vision/command
-> Behavior Tree
-> DrawRegularPolygon ou DrawCircle
-> Turtlesim
```

`SQUARE`, `CIRCLE` e `REGULAR_POLYGON` não passam pela CNN.

## Serviços

```text
Página: http://localhost:8000
WebSocket: ws://localhost:9090
Groot2Publisher: localhost:1667
```

A classificação de setas exige `canvas_bridge`, `vision_node` e o modelo CNN. Os botões geométricos exigem `rosbridge_server`, `bt_executor`, `turtlesim_node` e o servidor HTTP.

## Evidências

- Vídeo atual a gravar: `web_all_commands_demo.mp4`
- Captura recomendada: `web_all_commands.png`

## Limpeza da interface e do Turtlesim

A página distingue três operações:

- `Limpar seta`: limpa apenas o canvas HTML e não chama serviços ROS 2;
- `Limpar desenho`: chama `/clear`, apaga os traços e mantém a posição e orientação da tartaruga;
- `Reiniciar Turtlesim`: chama `/reset`, apaga os traços e repõe a tartaruga na posição inicial.

Para gravar evidências comparáveis, deve usar-se `Reiniciar Turtlesim` antes de executar cada forma.
