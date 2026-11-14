# Validação final atual

Esta pasta contém exclusivamente as evidências correspondentes ao estado
atual validado do projeto.

## Artefactos oficiais

- `python.txt`: única execução atual dos testes Python.
- `colcon_test.txt`: única execução atual dos testes ROS 2 e C++.
- `validation_manifest.txt`: ambiente, commit, hashes e resultados.
- `checkpoint_sha256.txt`: verificação dos checkpoints.
- `final_integrated_demo.mp4`: demonstração integrada final.

## Resultados atuais

- Python: 8 testes aprovados em 2.05 segundos.
- Tempo total Python: 2.79 segundos.
- Colcon: 20 testes, 0 erros e 0 falhas.
- Oito testes foram ignorados pelo sistema de testes ROS 2.
- As oito pre/post conditions do BehaviorTree.CPP passaram.

## Checkpoint oficial

- Treino: `training/weights/arrow_cnn_best.pth`
- Produção ROS 2:
  `ros2_ws/src/tsb_cv_brain/models/arrow_cnn_best.pth`
- SHA-256: `3cf85fdda9b1f8e2d1f4abbc571196417aeed8d8aa3359d55b7f7658da2c3a2e`

Os dois ficheiros são binariamente iguais.

## Resultados e gráficos atuais do modelo

Os resultados oficiais encontram-se exclusivamente em `training/outputs/`.
Resultados antigos, checkpoints substituídos e evidências duplicadas foram
removidos.
