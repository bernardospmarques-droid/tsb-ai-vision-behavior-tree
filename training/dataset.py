#!/usr/bin/env python3

from collections import Counter
from pathlib import Path

import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms


IMAGE_SIZE = 96

EXPECTED_CLASSES = [
    "Down",
    "Left",
    "Right",
    "Up",
]


def create_transforms():
    training_transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),

            transforms.RandomAffine(
                degrees=10,
                translate=(0.08, 0.08),
                scale=(0.90, 1.10),
            ),

            transforms.ColorJitter(
                brightness=0.15,
                contrast=0.15,
            ),

            transforms.ToTensor(),

            transforms.Normalize(
                mean=(0.5, 0.5, 0.5),
                std=(0.5, 0.5, 0.5),
            ),
        ]
    )

    evaluation_transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),

            transforms.ToTensor(),

            transforms.Normalize(
                mean=(0.5, 0.5, 0.5),
                std=(0.5, 0.5, 0.5),
            ),
        ]
    )

    return training_transform, evaluation_transform


def create_split_indices(
    targets,
    random_seed=42,
    training_fraction=0.70,
    validation_fraction=0.15,
):
    indices = np.arange(len(targets))
    targets_array = np.asarray(targets)

    test_fraction = (
        1.0
        - training_fraction
        - validation_fraction
    )

    if test_fraction <= 0.0:
        raise ValueError(
            "Training and validation fractions leave no test set."
        )

    training_indices, temporary_indices = train_test_split(
        indices,
        test_size=validation_fraction + test_fraction,
        random_state=random_seed,
        stratify=targets_array,
    )

    temporary_targets = targets_array[temporary_indices]

    relative_test_fraction = (
        test_fraction
        / (validation_fraction + test_fraction)
    )

    validation_indices, test_indices = train_test_split(
        temporary_indices,
        test_size=relative_test_fraction,
        random_state=random_seed,
        stratify=temporary_targets,
    )

    return (
        training_indices.tolist(),
        validation_indices.tolist(),
        test_indices.tolist(),
    )


def create_datasets(
    dataset_root,
    random_seed=42,
):
    dataset_root = Path(
        dataset_root
    ).expanduser().resolve()

    if not dataset_root.is_dir():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_root}"
        )

    training_transform, evaluation_transform = (
        create_transforms()
    )

    metadata_dataset = datasets.ImageFolder(
        root=dataset_root
    )

    if metadata_dataset.classes != EXPECTED_CLASSES:
        raise RuntimeError(
            "Unexpected class order. "
            f"Expected {EXPECTED_CLASSES}, "
            f"but received {metadata_dataset.classes}."
        )

    (
        training_indices,
        validation_indices,
        test_indices,
    ) = create_split_indices(
        targets=metadata_dataset.targets,
        random_seed=random_seed,
    )

    training_dataset = datasets.ImageFolder(
        root=dataset_root,
        transform=training_transform,
    )

    evaluation_dataset = datasets.ImageFolder(
        root=dataset_root,
        transform=evaluation_transform,
    )

    training_subset = Subset(
        training_dataset,
        training_indices,
    )

    validation_subset = Subset(
        evaluation_dataset,
        validation_indices,
    )

    test_subset = Subset(
        evaluation_dataset,
        test_indices,
    )

    return {
        "train": training_subset,
        "validation": validation_subset,
        "test": test_subset,

        "classes": metadata_dataset.classes,
        "class_to_index": metadata_dataset.class_to_idx,
        "targets": metadata_dataset.targets,

        "indices": {
            "train": training_indices,
            "validation": validation_indices,
            "test": test_indices,
        },
    }


def create_dataloaders(
    dataset_root,
    batch_size=32,
    number_of_workers=2,
    random_seed=42,
):
    dataset_information = create_datasets(
        dataset_root=dataset_root,
        random_seed=random_seed,
    )

    use_pinned_memory = torch.cuda.is_available()

    training_loader = DataLoader(
        dataset_information["train"],
        batch_size=batch_size,
        shuffle=True,
        num_workers=number_of_workers,
        pin_memory=use_pinned_memory,
    )

    validation_loader = DataLoader(
        dataset_information["validation"],
        batch_size=batch_size,
        shuffle=False,
        num_workers=number_of_workers,
        pin_memory=use_pinned_memory,
    )

    test_loader = DataLoader(
        dataset_information["test"],
        batch_size=batch_size,
        shuffle=False,
        num_workers=number_of_workers,
        pin_memory=use_pinned_memory,
    )

    dataset_information["loaders"] = {
        "train": training_loader,
        "validation": validation_loader,
        "test": test_loader,
    }

    return dataset_information


def describe_split(
    split_name,
    indices,
    targets,
    classes,
):
    split_targets = [
        targets[index]
        for index in indices
    ]

    class_counts = Counter(split_targets)

    print(f"\n{split_name}: {len(indices)} images")

    for class_index, class_name in enumerate(classes):
        number_of_images = class_counts.get(
            class_index,
            0,
        )

        print(
            f"  {class_name}: {number_of_images}"
        )


if __name__ == "__main__":
    dataset_path = (
        Path.home()
        / "sa_recrutamento_ai"
        / "dataset"
        / "arrow_dataset"
        / "extracted"
        / "Direction"
    )

    information = create_dataloaders(
        dataset_root=dataset_path,
        batch_size=32,
        number_of_workers=2,
        random_seed=42,
    )

    print("Classes:", information["classes"])

    print(
        "Class to index:",
        information["class_to_index"],
    )

    for name in [
        "train",
        "validation",
        "test",
    ]:
        describe_split(
            split_name=name,
            indices=information["indices"][name],
            targets=information["targets"],
            classes=information["classes"],
        )

    image_batch, label_batch = next(
        iter(information["loaders"]["train"])
    )

    print()
    print(
        "Image batch:",
        tuple(image_batch.shape),
    )

    print(
        "Label batch:",
        tuple(label_batch.shape),
    )

    print(
        "Smallest label:",
        int(label_batch.min()),
    )

    print(
        "Largest label:",
        int(label_batch.max()),
    )
