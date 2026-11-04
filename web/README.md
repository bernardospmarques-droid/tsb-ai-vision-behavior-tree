# Interface web da Fase 4

A interface permite desenhar uma seta num canvas HTML5, enviar a imagem
ao ROS 2 e receber a classificação produzida pela CNN.

## Tópicos

- Publicação: `/vision/canvas_png`
- Classificação: `/vision/command`

## Execução

1. Iniciar o `rosbridge_server`.
2. Iniciar `canvas_bridge`.
3. Iniciar `vision_node`.
4. Iniciar a Behavior Tree e o Turtlesim.
5. Servir esta pasta com `python3 -m http.server 8000`.
6. Abrir `http://localhost:8000`.

A aplicação liga ao WebSocket:

`ws://localhost:9090`

## Semântica dos comandos

Os comandos são relativos à orientação atual da tartaruga:

- `UP`: avançar;
- `DOWN`: recuar;
- `LEFT`: rodar à esquerda no lugar;
- `RIGHT`: rodar à direita no lugar.

`UP` e `DOWN` não correspondem necessariamente às direções verticais do ecrã.
