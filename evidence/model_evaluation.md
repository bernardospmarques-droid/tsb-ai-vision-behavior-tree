# Avaliação do modelo e análise de overfitting

## Resultados

O modelo foi treinado durante 30 épocas para classificar Down, Left, Right e Up.

No conjunto de teste com 540 imagens foram obtidos:

- accuracy global de 1.0;
- zero classificações incorretas;
- precision de 1.0 em todas as classes;
- recall de 1.0 em todas as classes;
- F1-score de 1.0 em todas as classes;
- matriz de confusão totalmente diagonal.

## Interpretação das curvas

As curvas de treino e validação convergem rapidamente para valores de accuracy próximos de 100%.
Não existe uma separação persistente entre a accuracy de treino e a accuracy de validação.

O training loss e o validation loss diminuem para valores muito baixos. Apesar de pequenas oscilações pontuais no validation loss, não existe uma tendência sustentada de aumento enquanto o training loss continua a diminuir.

O padrão clássico de overfitting seria o training loss continuar a diminuir enquanto o validation loss aumenta e a validation accuracy estabiliza ou diminui. Esse padrão não é observado de forma persistente.

## Limitação da conclusão

A accuracy perfeita deve ser interpretada com prudência. As imagens de treino, validação e teste provêm da mesma fonte e podem partilhar estilo, cores, fundos, enquadramentos e condições de iluminação.

Os resultados demonstram excelente desempenho dentro da distribuição do dataset, mas não garantem automaticamente igual desempenho em imagens externas.

## Validação futura recomendada

- setas desenhadas manualmente;
- imagens adquiridas por outra câmara;
- fundos e condições de iluminação diferentes;
- rotações e escalas mais extremas;
- ruído, desfocagem e oclusão parcial;
- estilos e cores ausentes do treino.

## Conclusão

Os resultados disponíveis não mostram evidência clara do padrão clássico de overfitting. O modelo generaliza corretamente para o conjunto de teste utilizado, mas a conclusão deve ser limitada ao domínio do dataset até existir validação com dados externos.
