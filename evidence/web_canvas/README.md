# Demonstração ponta a ponta da interface web

## Componentes demonstrados

- interface web com canvas HTML5;
- ligação ao ROS 2 através do rosbridge WebSocket;
- publicação em `/vision/canvas_png`;
- conversão da imagem pelo `canvas_bridge`;
- inferência com a `TurtleVisionCNN`;
- publicação em `/vision/command`;
- Behavior Tree monitorizada no Groot2;
- atuação no Turtlesim.

## Pipeline demonstrada

Canvas HTML5
→ rosbridge_server
→ /vision/canvas_png
→ canvas_bridge
→ /vision/image
→ vision_node
→ TurtleVisionCNN
→ /vision/command
→ GetVisionCommand
→ Blackboard {vision_command}
→ MoveTurtle
→ /turtle1/cmd_vel
→ Turtlesim

## Semântica dos comandos

Os comandos são relativos à orientação atual da tartaruga:

- `UP`: avançar;
- `DOWN`: recuar;
- `LEFT`: rodar à esquerda no lugar;
- `RIGHT`: rodar à direita no lugar.

## Evidência

- Vídeo: `web_groot2_turtlesim_demo.mp4`

O vídeo mostra simultaneamente:

1. a página ligada ao ROS 2;
2. uma seta desenhada no canvas;
3. a classificação apresentada na página;
4. os estados da Behavior Tree no Groot2;
5. o movimento correspondente no Turtlesim.
