# Monitorização e edição no Groot2

## Ligação

- Árvore principal: `MainTree`
- Host: `localhost`
- Porta: `1667`
- Publicador: `BT::Groot2Publisher`

## Estrutura atual

```text
MainTree
└── ReceiveAndExecute
    ├── GetCommand
    └── SelectBehavior
        ├── MoveForward
        ├── MoveBackward
        ├── RotateLeft90
        ├── RotateRight90
        ├── ExecuteSquare
        ├── ExecuteCircle
        └── ExecuteRegularPolygon
```

`REGULAR_POLYGON` utiliza a saída final do `Switch6`. Os seis casos explícitos são `UP`, `DOWN`, `LEFT`, `RIGHT`, `SQUARE` e `CIRCLE`. Como `GetVisionCommand` valida apenas sete comandos, a saída final é usada exclusivamente por `REGULAR_POLYGON`.

## Subárvore configurável

```text
DrawRegularPolygon
└── ConfigureAndDrawPolygon
    ├── CalculateTurnDuration
    └── RepeatPolygonSides
        └── DrawOnePolygonSide
            ├── PolygonMove
            └── PolygonTurn
```

Variáveis passadas pelo Blackboard:

```text
command
number_of_sides
move_direction
turn_direction
linear_speed
side_duration
angular_speed
turn_duration
```

## Monitor versus Editor

- `Monitor`: observa estados e valores, mas não permite editar a árvore em execução.
- `Editor`: permite alterar os ports no ficheiro `tree.xml`.

Ficheiro a editar:

```text
ros2_ws/src/tsb_bt_core/behavior_trees/tree.xml
```

Depois de guardar o XML, é necessário reiniciar o `bt_executor`. Com `--symlink-install`, não é necessário recompilar quando apenas o XML muda.

No Windows, o caminho WSL é semelhante a:

```text
\\wsl.localhost\Ubuntu\home\bernardo\tsb_project_clean\ros2_ws\src\tsb_bt_core\behavior_trees\tree.xml
```

## Limite da versão gratuita

A versão gratuita do Groot2 monitoriza árvores com até 20 nós. A árvore principal pode ultrapassar esse limite. Esta limitação não impede a execução pelo `bt_executor`.

## Evidências

- Vídeo atual a gravar: `groot2_current_runtime.mp4`
- Log: `execution.log`
