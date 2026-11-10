# Demonstração de formas geométricas

As formas são selecionadas pela árvore principal através de `/vision/command`.

## Fluxo comum

```text
/vision/command
-> GetVisionCommand
-> Blackboard {command}
-> SelectBehavior
-> subárvore geométrica
-> /turtle1/cmd_vel
-> Turtlesim
```

O `bt_executor` usa uma frequência de `100 Hz` para reduzir o erro temporal.

## Quadrado

O comando `SQUARE` reutiliza `DrawRegularPolygon` com:

```text
number_of_sides = 4
move_direction = UP
turn_direction = LEFT
linear_speed = 2.0
side_duration = 1.5
angular_speed = 1.5
```

O nó `CalculatePolygonTurn` calcula automaticamente:

```text
turn_duration = 2*pi / (4 * 1.5) = 1.0472 s
```

Cada lado tem aproximadamente `2.0 * 1.5 = 3.0` unidades.

- Árvore: `behavior_trees/tree.xml`
- Imagem: `square/square_turtlesim.png`
- Log: `square/execution.log`
- Estado final esperado: `SUCCESS`

## Círculo

O comando `CIRCLE` aplica simultaneamente:

```text
linear_speed = 2.0
angular_speed = 1.5 rad/s
duration = 4.1888 s
```

```text
radius = 2.0 / 1.5 = 1.333
duration = 2*pi / 1.5 = 4.1888 s
```

- Árvore: `behavior_trees/tree.xml`
- Imagem: `circle/circle_turtlesim.png`
- Log: `circle/execution.log`
- Estado final esperado: `SUCCESS`

## Polígono regular

O comando `REGULAR_POLYGON` executa `DrawRegularPolygon`.
A configuração predefinida é:

```text
number_of_sides = 6
move_direction = UP
turn_direction = LEFT
linear_speed = 1.5
side_duration = 1.0
angular_speed = 1.5
```

O cálculo automático é:

```text
turn_duration = 2*pi / (number_of_sides * abs(angular_speed))
turn_duration = 2*pi / (6 * 1.5) = 0.6981 s
```

Parâmetros editáveis no Editor do Groot2:

- `number_of_sides`: inteiro entre `3` e `12`;
- `move_direction`: `UP` ou `DOWN`;
- `turn_direction`: `LEFT` ou `RIGHT`;
- `linear_speed`;
- `side_duration`;
- `angular_speed`.

- Árvore: `behavior_trees/tree.xml`
- Imagem: `regular_polygon/regular_hexagon_turtlesim.png`
- Log: `regular_polygon/execution.log`
- Estado final esperado: `SUCCESS`

## Limitação geométrica

O controlo é temporal e em malha aberta. Pequenos erros de fecho podem resultar do escalonamento, da frequência de tick e da discretização dos comandos `Twist`.
