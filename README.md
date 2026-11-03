# TSB AI Vision and Behavior Tree

Sistema ROS 2 que classifica imagens de setas através de uma CNN em PyTorch e converte a direção prevista num movimento do Turtlesim através de uma Behavior Tree.

## Arquitetura

Imagem
  |
  v
/vision/image
sensor_msgs/Image
  |
  v

### tsb_cv_brain

TurtleVisionCNN
  |
  v
/vision/command
std_msgs/String
  |
  v
GetVisionCommand
  |
  v
Blackboard
{vision_command}
  |
  v
MoveTurtle
  |
  v
/turtle1/cmd_vel
geometry_msgs/Twist
  |
  v
Turtlesim
O sistema está dividido em três camadas principais:

Perceção: a CNN classifica a imagem recebida.
Decisão: a Behavior Tree recebe e valida o comando.
Atuação: o nó MoveTurtle converte o comando numa mensagem geometry_msgs/Twist.

## Classes

Índice	Classe da CNN	Comando ROS	Movimento
0	Down	DOWN	Movimento linear negativo
1	Left	LEFT	Rotação angular positiva
2	Right	RIGHT	Rotação angular negativa
3	Up	UP	Movimento linear positivo

## Packages ROS 2

### tsb_cv_brain

Package Python responsável por:

receber imagens em /vision/image;
converter mensagens sensor_msgs/Image para tensores RGB;
aceitar imagens rgb8, bgr8, rgba8, bgra8 e mono8;
redimensionar as imagens para 96 x 96;
aplicar a normalização usada durante o treino;
carregar o checkpoint arrow_cnn_best.pth;
executar inferência com PyTorch;
publicar UP, DOWN, LEFT ou RIGHT;
publicar imagens de teste através do executável image_publisher.
Principais módulos:

tsb_cv_brain/
├── image_processing.py
├── image_publisher.py
├── model.py
└── vision_node.py

### tsb_bt_core

Package C++ responsável por:

receber comandos em /vision/command;
aguardar um comando sem terminar a árvore em falha;
validar os comandos recebidos;
escrever o comando no Blackboard;
converter a direção numa mensagem geometry_msgs/Twist;
publicar em /turtle1/cmd_vel;
interromper o movimento após a duração configurada;
permitir monitorização através do Groot2;
terminar corretamente quando recebe Ctrl+C.

## Ambiente validado

O projeto foi desenvolvido e validado com:

Ubuntu 24.04 LTS;
ROS 2 Jazzy;
Python 3.12;
PyTorch 2.15 CPU;
NumPy 1.26;
BehaviorTree.CPP v4;
Turtlesim;
Groot2, opcional;
Colcon;
Git.

## Estrutura do projeto

tsb_project_clean/
├── .gitignore
├── README.md
├── evidence/
├── inventory/
├── training/
└── ros2_ws/
    └── src/
        ├── tsb_bt_core/
        └── tsb_cv_brain/
A pasta training/ contém os scripts usados na preparação, treino e avaliação da CNN.

A pasta ros2_ws/src/ contém apenas os packages necessários para a execução do sistema.

Os diretórios build/, install/ e log/ são gerados pelo Colcon e não são guardados no Git.

## Preparação do ambiente

Carregar o ROS 2 Jazzy:

source /opt/ros/jazzy/setup.bash
Ativar o ambiente virtual:

source ~/tsb_project_clean/.venv/bin/activate
Depois da compilação, carregar o workspace:

source ~/tsb_project_clean/ros2_ws/install/setup.bash
A preparação completa de um terminal é:

source /opt/ros/jazzy/setup.bash
source ~/tsb_project_clean/.venv/bin/activate
source ~/tsb_project_clean/ros2_ws/install/setup.bash

## Criação do ambiente virtual

O ambiente virtual deve permitir acesso aos packages Python instalados pelo ROS 2:

cd ~/tsb_project_clean

python3 -m venv \
  --system-site-packages \
  .venv
Ativar o ambiente:

source .venv/bin/activate
Atualizar as ferramentas Python:

python -m pip install \
  --upgrade \
  pip \
  setuptools \
  wheel

## Instalação das dependências Python

Instalar PyTorch e Torchvision para CPU:

python -m pip install \
  torch \
  torchvision \
  --index-url https://download.pytorch.org/whl/cpu
Instalar as restantes dependências:

python -m pip install \
  Pillow \
  pytest \
  isort
Confirmar a instalação:

python -c "import torch; print(torch.__version__)"
python -c "import rclpy; print(rclpy.__file__)"
python -c "import numpy; print(numpy.__version__)"

## Compilação

Entrar no workspace:

cd ~/tsb_project_clean/ros2_ws
Preparar o ambiente:

source /opt/ros/jazzy/setup.bash
source ~/tsb_project_clean/.venv/bin/activate
Compilar:

colcon build \
  --symlink-install \
  --event-handlers console_direct+
Carregar o workspace:

source install/setup.bash
Confirmar os packages:

ros2 pkg prefix tsb_bt_core
ros2 pkg prefix tsb_cv_brain
Os dois comandos devem devolver caminhos dentro de:

/home/bernardo/tsb_project_clean/ros2_ws/install/

## Testes automatizados

Entrar no workspace:

cd ~/tsb_project_clean/ros2_ws
Executar todos os testes:

colcon test \
  --event-handlers console_direct+
Apresentar os resultados detalhados:

colcon test-result --verbose
Resultado validado:

18 tests
0 errors
0 failures
6 skipped
Os testes incluem:

formato da saída da CNN;
compatibilidade entre arquitetura e checkpoint;
ordem das classes;
mapeamento dos índices;
preprocessamento de imagens RGB;
conversão de BGR para RGB;
expansão de imagens mono para três canais;
rejeição de encodings inválidos;
Flake8;
PEP 257;
CMake lint;
XML lint;
validação dos ficheiros das Behavior Trees.
Os testes identificados como skipped correspondem a verificações desativadas ou não aplicáveis no boilerplate. Não representam falhas funcionais.

## Execução completa

A execução completa pode ser feita através de quatro terminais.

### Terminal 1: Turtlesim

source /opt/ros/jazzy/setup.bash
source ~/tsb_project_clean/.venv/bin/activate
source ~/tsb_project_clean/ros2_ws/install/setup.bash

ros2 run turtlesim turtlesim_node

### Terminal 2: Behavior Tree

source /opt/ros/jazzy/setup.bash
source ~/tsb_project_clean/.venv/bin/activate
source ~/tsb_project_clean/ros2_ws/install/setup.bash

ros2 run tsb_bt_core bt_executor \
  --ros-args \
  -p tick_rate_hz:=10.0 \
  -p run_once:=false
O executor permanece em RUNNING enquanto aguarda um comando. O estado RUNNING não é apresentado continuamente no terminal.

Quando um comando é recebido e executado, a árvore termina essa execução com SUCCESS e volta a aguardar pelo comando seguinte.

### Terminal 3: nó de visão

source /opt/ros/jazzy/setup.bash
source ~/tsb_project_clean/.venv/bin/activate
source ~/tsb_project_clean/ros2_ws/install/setup.bash

ros2 run tsb_cv_brain vision_node
O nó deve apresentar informação semelhante a:

PyTorch 2.15.0+cpu, device: cpu
Loaded model: .../arrow_cnn_best.pth
Classes: ['Down', 'Left', 'Right', 'Up']
Input size: 96x96
Listening on /vision/image
Publishing on /vision/command

### Terminal 4: publicador de imagens

Preparar o terminal:

source /opt/ros/jazzy/setup.bash
source ~/tsb_project_clean/.venv/bin/activate
source ~/tsb_project_clean/ros2_ws/install/setup.bash
Escolher uma imagem da classe Left:

IMAGE="$(find \
  ~/sa_recrutamento_ai/dataset/arrow_dataset/extracted/Direction/Left \
  -type f \
  | head -n 1)"
Publicar a imagem uma única vez:

ros2 run tsb_cv_brain image_publisher \
  --ros-args \
  -p image_path:="$IMAGE" \
  -p repeat_count:=1
O publicador termina automaticamente após enviar a imagem.

## Testar as quatro classes

### Up

IMAGE="$(find \
  ~/sa_recrutamento_ai/dataset/arrow_dataset/extracted/Direction/Up \
  -type f \
  | head -n 1)"

ros2 run tsb_cv_brain image_publisher \
  --ros-args \
  -p image_path:="$IMAGE" \
  -p repeat_count:=1

### Down

IMAGE="$(find \
  ~/sa_recrutamento_ai/dataset/arrow_dataset/extracted/Direction/Down \
  -type f \
  | head -n 1)"

ros2 run tsb_cv_brain image_publisher \
  --ros-args \
  -p image_path:="$IMAGE" \
  -p repeat_count:=1

### Left

IMAGE="$(find \
  ~/sa_recrutamento_ai/dataset/arrow_dataset/extracted/Direction/Left \
  -type f \
  | head -n 1)"

ros2 run tsb_cv_brain image_publisher \
  --ros-args \
  -p image_path:="$IMAGE" \
  -p repeat_count:=1

### Right

IMAGE="$(find \
  ~/sa_recrutamento_ai/dataset/arrow_dataset/extracted/Direction/Right \
  -type f \
  | head -n 1)"

ros2 run tsb_cv_brain image_publisher \
  --ros-args \
  -p image_path:="$IMAGE" \
  -p repeat_count:=1

## Launch completo

Os componentes principais também podem ser iniciados através do launch:

source /opt/ros/jazzy/setup.bash
source ~/tsb_project_clean/.venv/bin/activate
source ~/tsb_project_clean/ros2_ws/install/setup.bash

ros2 launch tsb_bt_core challenge.launch.py
O launch inicia:

turtlesim_node;
vision_node;
bt_executor.
A imagem é publicada separadamente através do executável image_publisher.

## Tópicos principais

Tópico	Tipo	Finalidade
/vision/image	sensor_msgs/Image	Imagem de entrada
/vision/command	std_msgs/String	Direção classificada
/turtle1/cmd_vel	geometry_msgs/Twist	Movimento da tartaruga

## Behavior Tree

A árvore principal encontra-se em:

ros2_ws/src/tsb_bt_core/behavior_trees/tree.xml
Estrutura:

Sequence
├── GetVisionCommand
└── MoveTurtle
O comando é transferido através do Blackboard:

{vision_command}
O nó GetVisionCommand:

subscreve /vision/command;
aceita apenas UP, DOWN, LEFT e RIGHT;
permanece em RUNNING enquanto aguarda;
escreve o comando válido no Blackboard;
devolve SUCCESS depois de receber um comando válido.
O nó MoveTurtle:

lê o comando do Blackboard;
calcula a velocidade linear ou angular;
publica em /turtle1/cmd_vel;
mantém o movimento durante a duração configurada;
publica velocidade zero no final;
devolve SUCCESS após concluir o movimento.

## Configuração de movimento

A árvore principal utiliza os seguintes valores:

linear_speed = 2.0
angular_speed = 1.5
duration = 0.8 segundos
Os comandos são convertidos da seguinte forma:

Comando	linear.x	angular.z
UP	+2.0	0.0
DOWN	-2.0	0.0
LEFT	0.0	+1.5
RIGHT	0.0	-1.5

## Modelo CNN

O checkpoint encontra-se em:

ros2_ws/src/tsb_cv_brain/models/arrow_cnn_best.pth
Metadados utilizados durante a inferência:

Input: 3 x 96 x 96
Classes: Down, Left, Right, Up
Mean: 0.5, 0.5, 0.5
Standard deviation: 0.5, 0.5, 0.5
A arquitetura contém:

quatro camadas convolucionais;
Batch Normalization;
ReLU;
Max Pooling;
Adaptive Average Pooling;
uma camada totalmente ligada com 256 unidades;
Dropout de 0.4;
uma camada final com quatro logits.
O modelo é carregado uma única vez durante a inicialização do vision_node.

A inferência utiliza:

torch.inference_mode()

## Resultados da CNN

Dataset:

Total: 3.593 imagens
Down: 830
Left: 921
Right: 921
Up: 921
Todas as imagens originais têm:

224 x 224
RGB
Durante o preprocessamento, as imagens são redimensionadas para:

96 x 96
Resultados no conjunto de teste:

Imagens de teste: 540
Test accuracy: 1.0
Erros: 0
Resultados por classe:

Precision: 1.0
Recall: 1.0
F1-score: 1.0

## Monitorização com Groot2

O bt_executor cria um Groot2Publisher.

A porta predefinida é:

1667
Para alterar a porta:

ros2 run tsb_bt_core bt_executor \
  --ros-args \
  -p groot_port:=1668
No Groot2, utilizar o modo Monitor e ligar ao endereço:

localhost:1667

## Reposição do Turtlesim

Se a tartaruga atingir uma parede, repor o simulador:

ros2 service call \
  /reset \
  std_srvs/srv/Empty \
  "{}"
Reposicionar sem apagar o desenho:

ros2 service call \
  /turtle1/teleport_absolute \
  turtlesim/srv/TeleportAbsolute \
  "{x: 5.5, y: 5.5, theta: 0.0}"

## Encerramento

Os nós podem ser terminados através de:

Ctrl+C
O bt_executor utiliza tree.tickOnce(), devolvendo controlo ao ciclo principal após cada tick. Isto permite que o processo responda corretamente aos sinais de encerramento.

## Git

Versões estáveis:

v1.0-end-to-end
v1.1-stable-pipeline
v1.2-tested
Branch de acabamento:

feature/final-cleanup
Consultar o histórico:

git log --oneline --decorate
Consultar o estado:

git status

## Estado do projeto

Estrutura limpa e organizada;
CNN treinada e validada;
checkpoint integrado;
preprocessamento modular;
publicador de imagens integrado;
Behavior Tree reativa;
comunicação pelo Blackboard funcional;
controlo do Turtlesim funcional;
encerramento do executor corrigido;
testes automatizados sem falhas;
referências ao ambiente antigo removidas;
comentários TODO residuais removidos.
