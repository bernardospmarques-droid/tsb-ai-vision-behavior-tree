# Valgrind

## Objetivo

Esta secção documenta a utilização do Valgrind para validar a gestão de memória dos componentes desenvolvidos em C/C++ no projeto.

O objetivo é verificar a existência de:

- memory leaks;
- acessos inválidos à memória;
- utilização de memória não inicializada;
- libertações incorretas de memória;
- outros problemas relacionados com gestão dinâmica de memória.

---

## Pré-requisitos

Instalar o Valgrind:

```bash
sudo apt update
sudo apt install valgrind
