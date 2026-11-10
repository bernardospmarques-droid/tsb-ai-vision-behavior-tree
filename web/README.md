# Interface web da Fase 4

A interface permite desenhar uma seta para a CNN e executar formas pela Behavior Tree.

## Topicos
- Canvas: `/vision/canvas_png`
- Comandos: `/vision/command`

## Fluxos
- Canvas -> CNN -> UP/DOWN/LEFT/RIGHT -> Behavior Tree
- Botao Quadrado -> SQUARE -> DrawSquare
- Botao Circulo -> CIRCLE -> DrawCircle

A CNN continua treinada apenas para as quatro setas. SQUARE e CIRCLE nao passam pela CNN.

## Formas
- SQUARE: quatro repeticoes de UP e LEFT; rotacao 1.5 rad/s durante 1.0472 s.
- CIRCLE: velocidades linear 2.0 e angular 1.5 durante 4.1888 s; raio aproximado 1.333.

## Execucao
1. Iniciar Turtlesim e a Behavior Tree.
2. Iniciar rosbridge_server na porta 9090.
3. Iniciar canvas_bridge e vision_node para classificar setas.
4. Executar `python3 -m http.server 8000` nesta pasta.
5. Abrir `http://localhost:8000`.
6. Ligar o Monitor do Groot2 a `localhost:1667`.
