# Checkpoint Reproduction Result

## Environment

- Execution device: CPU
- Random seed: 42
- Dataset split: 70%% training, 15%% validation and 15%% testing
- Number of test images: 540
- Classes: Down, Left, Right and Up

## Training result

- Training completed successfully
- Best checkpoint epoch: 26
- Best validation loss: 0.00001413085830831378
- Best validation accuracy: 1.000000
- Final training loss: 0.0003
- Final training accuracy: 1.000000
- Elapsed training time: 551 seconds
- Final learning rate: 0.000125

## Test result

- Test loss: 0.000011
- Test accuracy: 1.000000
- Correct predictions: 540
- Incorrect predictions: 0

## Per-class result

| Class | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Down | 1.00 | 1.00 | 1.00 | 125 |
| Left | 1.00 | 1.00 | 1.00 | 138 |
| Right | 1.00 | 1.00 | 1.00 | 138 |
| Up | 1.00 | 1.00 | 1.00 | 139 |

## Confusion matrix

```text
[[125,   0,   0,   0],
 [  0, 138,   0,   0],
 [  0,   0, 138,   0],
 [  0,   0,   0, 139]]
```

## Checkpoint decision

The reproduced checkpoint was promoted to the production path:

```text
training/weights/arrow_cnn_best.pth
```

The reproduced checkpoint obtained 100%% validation accuracy and 100%% test accuracy, with 540 correct predictions and no incorrect predictions.

The SHA-256 value differs from the previously stored checkpoint because retraining does not necessarily produce a bit-for-bit identical file. Functional equivalence was established through the model metadata, class ordering, validation metrics, test metrics and confusion matrix.
