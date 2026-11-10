# Evidências das formas

Todas as formas são executadas pela árvore principal `tree.xml`.

## Quadrado

- Comando: `SQUARE`.
- Implementação: `DrawSquare` sobre `DrawRegularPolygon`.
- Geometria fixa: quatro lados e velocidade angular `1.5`.
- Log: `square/execution.log`.
- Imagem: `square/square_turtlesim.png`.

## Círculo

- Comando: `CIRCLE`.
- Velocidades: linear `2.0`, angular `1.5`.
- Duração: `4.1888 s`.
- Log: `circle/execution.log`.
- Imagem: `circle/circle_turtlesim.png`.

## Polígono regular

- Comando: `REGULAR_POLYGON`.
- Configuração predefinida: seis lados.
- Duração da rotação calculada automaticamente.
- Log: `regular_polygon/execution.log`.

O controlo é temporal e em malha aberta, pelo que podem existir pequenos erros de fecho.
