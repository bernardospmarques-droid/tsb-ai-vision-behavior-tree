# Evidencia ROS 2 bag

A gravacao integrada validada encontra-se em:

```text
integrated_20261114_221401
```

A gravacao foi criada com `ros2 bag record` e validada com:

```bash
ros2 bag info evidence/rosbag/integrated_20261114_221401
```

## Resultado da validacao

- Mensagens registadas: 8577
- Duracao: 93.742608992s
- Topicos incluidos:
  - `/vision/canvas_png`
  - `/vision/image`
  - `/vision/command`
  - `/turtle1/cmd_vel`
  - `/turtle1/pose`
  - `/rosout`
- Resultado integral de `ros2 bag info`:
  `evidence/rosbag/latest_bag_info.txt`

Esta evidencia permite inspecionar e reproduzir a comunicacao entre a
interface web, o processamento de visao, a Behavior Tree e o Turtlesim.
