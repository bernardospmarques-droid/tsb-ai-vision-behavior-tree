#!/usr/bin/env python3

import argparse
import json
import random
import time
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import nn
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from tqdm import tqdm

from dataset import create_dataloaders
from model import TurtleVisionCNN


def set_random_seed(random_seed):
    random.seed(random_seed)
    np.random.seed(random_seed)
    torch.manual_seed(random_seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(random_seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def choose_device():
    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def calculate_class_weights(
    training_indices,
    all_targets,
    number_of_classes,
    device,
):
    training_targets = [
        all_targets[index]
        for index in training_indices
    ]

    class_counts = Counter(training_targets)
    total_samples = len(training_targets)

    weights = []

    for class_index in range(number_of_classes):
        class_count = class_counts[class_index]

        class_weight = (
            total_samples
            / (number_of_classes * class_count)
        )

        weights.append(class_weight)

    return torch.tensor(
        weights,
        dtype=torch.float32,
        device=device,
    )


def run_training_epoch(
    model,
    data_loader,
    criterion,
    optimizer,
    device,
):
    model.train()

    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    progress_bar = tqdm(
        data_loader,
        desc="Training",
        leave=False,
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

        optimizer.zero_grad(set_to_none=True)

        logits = model(images)
        loss = criterion(logits, labels)

        loss.backward()
        optimizer.step()

        predictions = logits.argmax(dim=1)

        batch_size = labels.size(0)

        total_loss += loss.item() * batch_size
        total_correct += (
            predictions == labels
        ).sum().item()

        total_samples += batch_size

        current_loss = total_loss / total_samples
        current_accuracy = (
            total_correct / total_samples
        )

        progress_bar.set_postfix(
            loss=f"{current_loss:.4f}",
            accuracy=f"{current_accuracy:.4f}",
        )

    epoch_loss = total_loss / total_samples
    epoch_accuracy = total_correct / total_samples

    return epoch_loss, epoch_accuracy


def run_evaluation(
    model,
    data_loader,
    criterion,
    device,
):
    model.eval()

    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    with torch.no_grad():
        progress_bar = tqdm(
            data_loader,
            desc="Validation",
            leave=False,
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

            predictions = logits.argmax(dim=1)

            batch_size = labels.size(0)

            total_loss += loss.item() * batch_size
            total_correct += (
                predictions == labels
            ).sum().item()

            total_samples += batch_size

    epoch_loss = total_loss / total_samples
    epoch_accuracy = total_correct / total_samples

    return epoch_loss, epoch_accuracy


def save_checkpoint(
    checkpoint_path,
    model,
    optimizer,
    epoch,
    validation_loss,
    validation_accuracy,
    classes,
    class_to_index,
    image_size,
):
    checkpoint = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "validation_loss": validation_loss,
        "validation_accuracy": validation_accuracy,
        "classes": classes,
        "class_to_index": class_to_index,
        "image_size": image_size,
        "normalization_mean": [0.5, 0.5, 0.5],
        "normalization_std": [0.5, 0.5, 0.5],
    }

    torch.save(
        checkpoint,
        checkpoint_path,
    )


def create_training_curves(
    history,
    output_path,
):
    epochs = range(
        1,
        len(history["training_loss"]) + 1,
    )

    figure, axes = plt.subplots(
        1,
        2,
        figsize=(13, 5),
    )

    axes[0].plot(
        epochs,
        history["training_loss"],
        label="Training loss",
    )

    axes[0].plot(
        epochs,
        history["validation_loss"],
        label="Validation loss",
    )

    axes[0].set_title("Loss over epochs")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot(
        epochs,
        history["training_accuracy"],
        label="Training accuracy",
    )

    axes[1].plot(
        epochs,
        history["validation_accuracy"],
        label="Validation accuracy",
    )

    axes[1].set_title("Accuracy over epochs")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].set_ylim(0.0, 1.0)
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    figure.tight_layout()
    figure.savefig(
        output_path,
        dpi=180,
    )

    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(
        description="Train the arrow classification CNN."
    )

    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs"),
    )

    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("weights"),
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.001,
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--patience",
        type=int,
        default=7,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )

    arguments = parser.parse_args()

    dataset_root = arguments.dataset.expanduser().resolve()
    output_root = arguments.output.expanduser().resolve()
    weights_root = arguments.weights.expanduser().resolve()

    output_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    weights_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    set_random_seed(arguments.seed)

    device = choose_device()

    print("Device:", device)

    if device.type == "cuda":
        print(
            "GPU:",
            torch.cuda.get_device_name(0),
        )

    dataset_information = create_dataloaders(
        dataset_root=dataset_root,
        batch_size=arguments.batch_size,
        number_of_workers=arguments.workers,
        random_seed=arguments.seed,
    )

    classes = dataset_information["classes"]
    class_to_index = dataset_information["class_to_index"]

    print("Classes:", classes)
    print("Class mapping:", class_to_index)

    print(
        "Training images:",
        len(dataset_information["train"]),
    )

    print(
        "Validation images:",
        len(dataset_information["validation"]),
    )

    print(
        "Test images:",
        len(dataset_information["test"]),
    )

    class_weights = calculate_class_weights(
        training_indices=dataset_information["indices"]["train"],
        all_targets=dataset_information["targets"],
        number_of_classes=len(classes),
        device=device,
    )

    print(
        "Class weights:",
        class_weights.detach().cpu().tolist(),
    )

    model = TurtleVisionCNN(
        number_of_classes=len(classes)
    ).to(device)

    criterion = nn.CrossEntropyLoss(
        weight=class_weights
    )

    optimizer = Adam(
        model.parameters(),
        lr=arguments.learning_rate,
        weight_decay=0.0001,
    )

    scheduler = ReduceLROnPlateau(
        optimizer,
        mode="min",
        factor=0.5,
        patience=2,
    )

    history = {
        "training_loss": [],
        "validation_loss": [],
        "training_accuracy": [],
        "validation_accuracy": [],
        "learning_rate": [],
    }

    best_validation_loss = float("inf")
    best_validation_accuracy = 0.0
    epochs_without_improvement = 0

    best_model_path = (
        weights_root
        / "arrow_cnn_best.pth"
    )

    start_time = time.time()

    for epoch in range(1, arguments.epochs + 1):
        print()
        print(
            f"Epoch {epoch}/{arguments.epochs}"
        )

        training_loss, training_accuracy = (
            run_training_epoch(
                model=model,
                data_loader=dataset_information[
                    "loaders"
                ]["train"],
                criterion=criterion,
                optimizer=optimizer,
                device=device,
            )
        )

        validation_loss, validation_accuracy = (
            run_evaluation(
                model=model,
                data_loader=dataset_information[
                    "loaders"
                ]["validation"],
                criterion=criterion,
                device=device,
            )
        )

        scheduler.step(validation_loss)

        current_learning_rate = (
            optimizer.param_groups[0]["lr"]
        )

        history["training_loss"].append(
            training_loss
        )

        history["validation_loss"].append(
            validation_loss
        )

        history["training_accuracy"].append(
            training_accuracy
        )

        history["validation_accuracy"].append(
            validation_accuracy
        )

        history["learning_rate"].append(
            current_learning_rate
        )

        print(
            "Training loss:",
            f"{training_loss:.4f}",
        )

        print(
            "Training accuracy:",
            f"{training_accuracy:.4f}",
        )

        print(
            "Validation loss:",
            f"{validation_loss:.4f}",
        )

        print(
            "Validation accuracy:",
            f"{validation_accuracy:.4f}",
        )

        print(
            "Learning rate:",
            current_learning_rate,
        )

        if validation_loss < best_validation_loss:
            best_validation_loss = validation_loss
            best_validation_accuracy = (
                validation_accuracy
            )

            epochs_without_improvement = 0

            save_checkpoint(
                checkpoint_path=best_model_path,
                model=model,
                optimizer=optimizer,
                epoch=epoch,
                validation_loss=validation_loss,
                validation_accuracy=validation_accuracy,
                classes=classes,
                class_to_index=class_to_index,
                image_size=96,
            )

            print(
                "Best model saved:",
                best_model_path,
            )

        else:
            epochs_without_improvement += 1

            print(
                "Epochs without improvement:",
                epochs_without_improvement,
            )

        history_path = (
            output_root
            / "training_history.json"
        )

        with history_path.open(
            "w",
            encoding="utf-8",
        ) as history_file:
            json.dump(
                history,
                history_file,
                indent=2,
            )

        create_training_curves(
            history=history,
            output_path=(
                output_root
                / "training_curves.png"
            ),
        )

        if (
            epochs_without_improvement
            >= arguments.patience
        ):
            print()
            print(
                "Early stopping activated."
            )

            break

    elapsed_seconds = time.time() - start_time

    summary = {
        "device": str(device),
        "classes": classes,
        "class_to_index": class_to_index,
        "epochs_completed": len(
            history["training_loss"]
        ),
        "best_validation_loss": (
            best_validation_loss
        ),
        "best_validation_accuracy": (
            best_validation_accuracy
        ),
        "elapsed_seconds": elapsed_seconds,
        "best_model": str(best_model_path),
    }

    summary_path = (
        output_root
        / "training_summary.json"
    )

    with summary_path.open(
        "w",
        encoding="utf-8",
    ) as summary_file:
        json.dump(
            summary,
            summary_file,
            indent=2,
        )

    print()
    print("Training completed.")
    print(
        "Best validation loss:",
        f"{best_validation_loss:.4f}",
    )

    print(
        "Best validation accuracy:",
        f"{best_validation_accuracy:.4f}",
    )

    print(
        "Elapsed time:",
        f"{elapsed_seconds:.1f} seconds",
    )

    print(
        "Best model:",
        best_model_path,
    )


if __name__ == "__main__":
    main()

