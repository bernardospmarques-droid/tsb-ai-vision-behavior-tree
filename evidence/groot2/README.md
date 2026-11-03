# Monitorização em tempo real no Groot2

## Configuração

- Projeto: `behavior_trees/tsb_challenge.btproj`
- Árvore: `MainTree`
- Host: `localhost`
- Porta: `1667`
- Estado: `Connected`

## Elementos monitorizados

- `Root`
- `Sequence: VisionToMotion`
- `GetVisionCommand`
- `MoveTurtle`
- Blackboard: `{vision_command}`

## Sequência observada

1. `GetVisionCommand` permanece em `RUNNING` enquanto aguarda.
2. O nó de visão publica uma direção em `/vision/command`.
3. `GetVisionCommand` escreve a direção no Blackboard.
4. `GetVisionCommand` devolve `SUCCESS`.
5. `MoveTurtle` entra em `RUNNING`.
6. A tartaruga executa o movimento.
7. `MoveTurtle` devolve `SUCCESS`.
8. A árvore completa termina em `SUCCESS`.
9. Uma nova execução volta a aguardar por um comando.

## Evidências

- Vídeo: `groot2_runtime_monitoring.mov`
- Log: `execution.log`
