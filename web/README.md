# Interface web da Fase 4

A interface permite classificar setas com a CNN e executar formas diretamente pela Behavior Tree.

## Tópicos

- Canvas: `/vision/canvas_png`
- Imagem ROS: `/vision/image`
- Comandos: `/vision/command`

## Comandos

```text
UP
DOWN
LEFT
RIGHT
SQUARE
CIRCLE
REGULAR_POLYGON
```

A CNN produz apenas os quatro comandos direcionais. As três formas são publicadas diretamente pelos botões web.

## Execução

1. Iniciar `challenge.launch.py` ou `turtlesim_node` e `bt_executor`.
2. Iniciar `canvas_bridge` e `vision_node` para classificar setas.
3. Iniciar `rosbridge_server` na porta `9090`.
4. Executar `python3 -m http.server 8000` na pasta `web`.
5. Abrir `http://localhost:8000`.
6. Opcionalmente, ligar o Monitor do Groot2 a `localhost:1667`.

## Formas

- `SQUARE`: `DrawRegularPolygon` com quatro lados.
- `CIRCLE`: velocidades linear e angular simultâneas.
- `REGULAR_POLYGON`: entre 3 e 12 lados, com duração de rotação calculada automaticamente.

## Groot2

Os valores são editáveis no modo Editor, no ficheiro `ros2_ws/src/tsb_bt_core/behavior_trees/tree.xml`. O modo Monitor é apenas de leitura. Depois de guardar o XML, reiniciar o `bt_executor`.

## Limpeza da interface e do Turtlesim

A página distingue três operações:

- `Limpar seta`: limpa apenas o canvas HTML e não chama serviços ROS 2;
- `Limpar desenho`: chama `/clear`, apaga os traços e mantém a posição e orientação da tartaruga;
- `Reiniciar Turtlesim`: chama `/reset`, apaga os traços e repõe a tartaruga na posição inicial.

Para gravar evidências comparáveis, deve usar-se `Reiniciar Turtlesim` antes de executar cada forma.
