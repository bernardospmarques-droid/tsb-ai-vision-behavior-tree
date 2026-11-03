#!/usr/bin/env python3

import torch
from torch import nn


class TurtleVisionCNN(nn.Module):
    """CNN criada de raiz para classificar setas em quatro direções."""

    def __init__(self, number_of_classes=4):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(
                in_channels=3,
                out_channels=32,
                kernel_size=3,
                padding=1,
            ),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),

            nn.Conv2d(
                in_channels=32,
                out_channels=64,
                kernel_size=3,
                padding=1,
            ),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),

            nn.Conv2d(
                in_channels=64,
                out_channels=128,
                kernel_size=3,
                padding=1,
            ),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),

            nn.Conv2d(
                in_channels=128,
                out_channels=128,
                kernel_size=3,
                padding=1,
            ),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
        )

        self.pool = nn.AdaptiveAvgPool2d((4, 4))

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.4),
            nn.Linear(256, number_of_classes),
        )

    def forward(self, image_batch):
        features = self.features(image_batch)
        pooled_features = self.pool(features)
        logits = self.classifier(pooled_features)

        return logits


def count_trainable_parameters(model):
    return sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )


if __name__ == "__main__":
    network = TurtleVisionCNN(number_of_classes=4)

    example_batch = torch.randn(8, 3, 96, 96)
    output = network(example_batch)

    print(network)
    print()
    print("Input shape:", tuple(example_batch.shape))
    print("Output shape:", tuple(output.shape))
    print(
        "Trainable parameters:",
        count_trainable_parameters(network),
    )
