# Conformidade com AED e Programação

## 1. Estruturas de Dados Utilizadas

O projeto utiliza diversas estruturas de dados estudadas nas unidades curriculares de Programação e Algoritmos e Estruturas de Dados (AED):

- `std::vector` para armazenamento sequencial de dados, batches de treino e resultados.
- `std::string` para manipulação de texto, tópicos ROS2 e caminhos de ficheiros.
- Estruturas de dados internas do ROS2 para comunicação publisher/subscriber.
- Blackboard do BehaviourTree.CPP para partilha estruturada de informação entre nós.
- Estruturas hierárquicas representadas por Behaviour Trees.
- Containers da STL para gestão eficiente de coleções de dados.

A seleção destas estruturas privilegia simplicidade, eficiência e reutilização, seguindo boas práticas de engenharia de software.

---

## 2. Complexidade Temporal dos Principais Módulos

| Módulo | Complexidade Aproximada |
|---------|---------|
| Percurso da Behaviour Tree | O(N) |
| Atualização do Blackboard | O(1) |
| Consulta do Blackboard | O(1) |
| Publicação ROS2 | O(1) |
| Subscrição ROS2 | O(1) |
| Inferência CNN | O(P) |
| Renderização Web | O(N) |
| Leitura de configuração | O(N) |

Onde:

- N representa o número de nós visitados.
- P representa o número de parâmetros/operações da rede neuronal.

A utilização de algoritmos lineares ou constantes nos módulos principais garante desempenho adequado para execução em tempo real.

---

## 3. Justificação da Arquitetura Modular

A arquitetura foi concebida segundo os princípios de modularidade, encapsulamento e separação de responsabilidades.

O sistema encontra-se dividido em componentes independentes:

### Perceção
Responsável pela classificação das imagens através da CNN desenvolvida em PyTorch.

### Decisão
Implementada através de Behaviour Trees em C++, permitindo modelar comportamentos complexos de forma modular, reutilizável e facilmente extensível.

### Comunicação
Assegurada pelo ROS2, que desacopla os diferentes componentes através de publishers, subscribers e serviços.

### Interface
Disponibiliza monitorização e interação através da aplicação web.

Esta separação permite:

- Manutenção simplificada.
- Substituição independente de componentes.
- Reutilização de código.
- Facilidade de teste.
- Maior escalabilidade.

A organização segue os princípios estudados em Programação relativos à decomposição modular, abstração de dados e separação entre interface e implementação.

---

## Conclusão

O projeto aplica na prática vários conceitos fundamentais de Programação e AED, nomeadamente abstração de dados, modularidade, organização em múltiplos módulos, análise de complexidade e utilização adequada de estruturas de dados. Estas decisões contribuíram para a construção de uma arquitetura robusta, extensível e alinhada com as boas práticas de desenvolvimento de software.
