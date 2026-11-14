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

- Python: 8 testes aprovados.
- ROS 2/C++: 18 testes, 0 erros e 0 falhas.
- Seis testes foram ignorados pelo sistema de testes ROS 2.
- As oito pre/post conditions do BehaviorTree.CPP foram executadas com sucesso
  pelo teste C++ incluído em `tsb_bt_core`.

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

## Reprodução da avaliação do modelo

A avaliação do conjunto de teste foi reproduzida explicitamente com o
checkpoint cujo SHA-256 é:

`3cf85fdda9b1f8e2d1f4abbc571196417aeed8d8aa3359d55b7f7658da2c3a2e`

Configuração utilizada:

- dataset: `Direction`, com 3.593 imagens;
- divisão determinística com seed `42`;
- conjunto de teste: 540 imagens;
- batch size: `64`;
- workers: `2`;
- checkpoint epoch: `26`.

Resultados reproduzidos:

- test loss: `1.0815736210066394e-05`;
- test accuracy: `1.0`;
- previsões corretas: `540`;
- previsões incorretas: `0`.

A reprodução gerou um relatório de classificação, uma matriz de confusão e
um JSON binariamente iguais aos ficheiros existentes em `training/outputs/`.
O CSV continha as mesmas 540 imagens, classes, previsões, probabilidades e
confianças; a diferença de hash era apenas uma diferença de ordenação das
linhas.
