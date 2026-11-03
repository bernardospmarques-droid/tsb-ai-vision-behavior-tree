#!/usr/bin/env python3

import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from torch import nn
from tqdm import tqdm

from dataset import create_dataloaders
from model import TurtleVisionCNN


def choose_device():
    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def load_checkpoint(checkpoint_path, device):
    checkpoint_path = checkpoint_path.expanduser().resolve()

    if not checkpoint_path.is_file():
        raise FileNotFoundError(
            f"Checkpoint not found: {checkpoint_path}"
        )

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,
    )

    required_keys = [
        "model_state_dict",
        "classes",
        "class_to_index",
        "image_size",
    ]

    for key in required_keys:
        if key not in checkpoint:
            raise KeyError(
                f"Checkpoint is missing the key: {key}"
            )

    return checkpoint


def evaluate_model(
    model,
    data_loader,
    criterion,
    device,
):
    model.eval()

    total_loss = 0.0
    total_samples = 0

    all_labels = []
    all_predictions = []
    all_probabilities = []

    with torch.no_grad():
        progress_bar = tqdm(
            data_loader,
            desc="Testing",
            leave=True,
        )

        for images, labels in progress_bar:
            images = images.to(
                device,
                non_blocking=True,
            )

            labels = labels.to(
                device,
                non_blocking=True,
            )

            logits = model(images)
            loss = criterion(logits, labels)

            probabilities = torch.softmax(
                logits,
                dim=1,
            )

            predictions = probabilities.argmax(
                dim=1
            )

            batch_size = labels.size(0)

            total_loss += loss.item() * batch_size
            total_samples += batch_size

            all_labels.extend(
                labels.detach().cpu().tolist()
            )

            all_predictions.extend(
                predictions.detach().cpu().tolist()
            )

            all_probabilities.extend(
                probabilities.detach().cpu().tolist()
            )

    test_loss = total_loss / total_samples

    return {
        "test_loss": test_loss,
        "labels": all_labels,
        "predictions": all_predictions,
        "probabilities": all_probabilities,
    }


def create_confusion_matrix_figure(
    matrix,
    class_names,
    output_path,
):
    figure, axis = plt.subplots(
        figsize=(8, 7)
    )

    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
        cbar=True,
        ax=axis,
    )

    axis.set_title("Matriz de confusão no conjunto de teste")
    axis.set_xlabel("Classe prevista")
    axis.set_ylabel("Classe verdadeira")

    figure.tight_layout()
    figure.savefig(
        output_path,
        dpi=200,
    )

    plt.close(figure)


def save_predictions_csv(
    output_path,
    image_paths,
    labels,
    predictions,
    probabilities,
    class_names,
):
    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.writer(csv_file)

        header = [
            "image_path",
            "true_index",
            "true_class",
            "predicted_index",
            "predicted_class",
            "confidence",
        ]

        for class_name in class_names:
            header.append(
                f"probability_{class_name}"
            )

        writer.writerow(header)

        for (
            image_path,
            true_index,
            predicted_index,
            probability_values,
        ) in zip(
            image_paths,
            labels,
            predictions,
            probabilities,
        ):
            confidence = max(probability_values)

            row = [
                str(image_path),
                true_index,
                class_names[true_index],
                predicted_index,
                class_names[predicted_index],
                confidence,
            ]

            row.extend(probability_values)
            writer.writerow(row)


def create_misclassified_grid(
    misclassified_items,
    class_names,
    output_path,
    maximum_images=24,
):
    if not misclassified_items:
        print(
            "No misclassified images were found."
        )
        return

    selected_items = misclassified_items[
        :maximum_images
    ]

    number_of_images = len(selected_items)
    number_of_columns = 4
    number_of_rows = int(
        np.ceil(
            number_of_images / number_of_columns
        )
    )

    figure, axes = plt.subplots(
        number_of_rows,
        number_of_columns,
        figsize=(
            number_of_columns * 4,
            number_of_rows * 4,
        ),
        squeeze=False,
    )

    flattened_axes = axes.flatten()

    for axis in flattened_axes:
        axis.axis("off")

    for axis, item in zip(
        flattened_axes,
        selected_items,
    ):
        image_path = item["image_path"]

        with Image.open(image_path) as image:
            axis.imshow(
                image.convert("RGB")
            )

        true_name = class_names[
            item["true_index"]
        ]

        predicted_name = class_names[
            item["predicted_index"]
        ]

        confidence = item["confidence"]

        axis.set_title(
            f"Real: {true_name}\n"
            f"Prevista: {predicted_name}\n"
            f"Confiança: {confidence:.3f}"
        )

        axis.axis("off")

    figure.suptitle(
        "Exemplos classificados incorretamente",
        fontsize=16,
    )

    figure.tight_layout()
    figure.savefig(
        output_path,
        dpi=180,
    )

    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the arrow classification CNN "
            "on the test set."
        )
    )

    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--checkpoint",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs"),
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    arguments = parser.parse_args()

    dataset_root = (
        arguments.dataset.expanduser().resolve()
    )

    output_root = (
        arguments.output.expanduser().resolve()
    )

    checkpoint_path = (
        arguments.checkpoint.expanduser().resolve()
    )

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    device = choose_device()

    print("Device:", device)

    if device.type == "cuda":
        print(
            "GPU:",
            torch.cuda.get_device_name(0),
        )

    checkpoint = load_checkpoint(
        checkpoint_path=checkpoint_path,
        device=device,
    )

    checkpoint_classes = checkpoint["classes"]
    checkpoint_mapping = checkpoint[
        "class_to_index"
    ]

    print(
        "Checkpoint epoch:",
        checkpoint.get("epoch"),
    )

    print(
        "Checkpoint validation loss:",
        checkpoint.get("validation_loss"),
    )

    print(
        "Checkpoint validation accuracy:",
        checkpoint.get(
            "validation_accuracy"
        ),
    )

    print(
        "Checkpoint classes:",
        checkpoint_classes,
    )

    dataset_information = create_dataloaders(
        dataset_root=dataset_root,
        batch_size=arguments.batch_size,
        number_of_workers=arguments.workers,
        random_seed=arguments.seed,
    )

    dataset_classes = dataset_information[
        "classes"
    ]

    dataset_mapping = dataset_information[
        "class_to_index"
    ]

    if checkpoint_classes != dataset_classes:
        raise RuntimeError(
            "Checkpoint classes do not match "
            "the dataset classes."
        )

    if checkpoint_mapping != dataset_mapping:
        raise RuntimeError(
            "Checkpoint class mapping does not match "
            "the dataset mapping."
        )

    model = TurtleVisionCNN(
        number_of_classes=len(dataset_classes)
    ).to(device)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    criterion = nn.CrossEntropyLoss()

    results = evaluate_model(
        model=model,
        data_loader=dataset_information[
            "loaders"
        ]["test"],
        criterion=criterion,
        device=device,
    )

    labels = results["labels"]
    predictions = results["predictions"]
    probabilities = results["probabilities"]
    test_loss = results["test_loss"]

    test_accuracy = accuracy_score(
        labels,
        predictions,
    )

    report = classification_report(
        labels,
        predictions,
        target_names=dataset_classes,
        labels=list(
            range(len(dataset_classes))
        ),
        output_dict=True,
        zero_division=0,
    )

    report_text = classification_report(
        labels,
        predictions,
        target_names=dataset_classes,
        labels=list(
            range(len(dataset_classes))
        ),
        zero_division=0,
    )

    matrix = confusion_matrix(
        labels,
        predictions,
        labels=list(
            range(len(dataset_classes))
        ),
    )

    test_subset = dataset_information["test"]
    test_indices = dataset_information[
        "indices"
    ]["test"]

    base_dataset = test_subset.dataset

    image_paths = [
        Path(base_dataset.samples[index][0])
        for index in test_indices
    ]

    misclassified_items = []

    for (
        image_path,
        true_index,
        predicted_index,
        probability_values,
    ) in zip(
        image_paths,
        labels,
        predictions,
        probabilities,
    ):
        if true_index != predicted_index:
            misclassified_items.append(
                {
                    "image_path": image_path,
                    "true_index": true_index,
                    "predicted_index": predicted_index,
                    "confidence": max(
                        probability_values
                    ),
                }
            )

    misclassified_items.sort(
        key=lambda item: item["confidence"],
        reverse=True,
    )

    create_confusion_matrix_figure(
        matrix=matrix,
        class_names=dataset_classes,
        output_path=(
            output_root
            / "confusion_matrix.png"
        ),
    )

    create_misclassified_grid(
        misclassified_items=misclassified_items,
        class_names=dataset_classes,
        output_path=(
            output_root
            / "misclassified_examples.png"
        ),
    )

    save_predictions_csv(
        output_path=(
            output_root
            / "test_predictions.csv"
        ),
        image_paths=image_paths,
        labels=labels,
        predictions=predictions,
        probabilities=probabilities,
        class_names=dataset_classes,
    )

    final_report = {
        "checkpoint": str(checkpoint_path),
        "checkpoint_epoch": checkpoint.get(
            "epoch"
        ),
        "device": str(device),
        "classes": dataset_classes,
        "class_to_index": dataset_mapping,
        "test_images": len(labels),
        "test_loss": test_loss,
        "test_accuracy": test_accuracy,
        "number_of_errors": len(
            misclassified_items
        ),
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
    }

    report_path = (
        output_root
        / "test_evaluation.json"
    )

    with report_path.open(
        "w",
        encoding="utf-8",
    ) as report_file:
        json.dump(
            final_report,
            report_file,
            indent=2,
            ensure_ascii=False,
        )

    report_text_path = (
        output_root
        / "classification_report.txt"
    )

    with report_text_path.open(
        "w",
        encoding="utf-8",
    ) as text_file:
        text_file.write(report_text)

    print()
    print("Test loss:", f"{test_loss:.6f}")
    print(
        "Test accuracy:",
        f"{test_accuracy:.6f}",
    )

    print(
        "Correct predictions:",
        len(labels) - len(misclassified_items),
    )

    print(
        "Incorrect predictions:",
        len(misclassified_items),
    )

    print()
    print(report_text)

    print("Confusion matrix:")
    print(matrix)

    print()
    print("Results saved in:", output_root)


if __name__ == "__main__":
    main()
