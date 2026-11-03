#!/usr/bin/env python3

import argparse
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".webp",
}


def collect_images(dataset_root):
    image_paths = []

    for current_directory, _, filenames in os.walk(dataset_root):
        for filename in filenames:
            image_path = Path(current_directory) / filename

            if image_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                image_paths.append(image_path)

    return sorted(image_paths)


def inspect_images(image_paths, dataset_root):
    class_counts = Counter()
    mode_counts = Counter()
    size_counts = Counter()
    corrupted_files = []
    class_samples = defaultdict(list)

    total_images = len(image_paths)

    for index, image_path in enumerate(image_paths, start=1):
        class_name = image_path.parent.name
        class_counts[class_name] += 1

        try:
            with Image.open(image_path) as image:
                image.verify()

            with Image.open(image_path) as image:
                mode_counts[image.mode] += 1

                size_name = f"{image.width}x{image.height}"
                size_counts[size_name] += 1

                if len(class_samples[class_name]) < 6:
                    class_samples[class_name].append(image_path)

        except (UnidentifiedImageError, OSError, ValueError) as error:
            corrupted_files.append(
                {
                    "path": str(image_path.relative_to(dataset_root)),
                    "error": str(error),
                }
            )

        if index % 500 == 0:
            print(
                f"Inspecionadas {index}/{total_images} imagens..."
            )

    return {
        "class_counts": class_counts,
        "mode_counts": mode_counts,
        "size_counts": size_counts,
        "corrupted_files": corrupted_files,
        "class_samples": class_samples,
    }


def create_distribution_chart(class_counts, output_path):
    class_names = sorted(class_counts)
    counts = [class_counts[name] for name in class_names]

    figure, axis = plt.subplots(figsize=(8, 5))
    bars = axis.bar(class_names, counts)

    axis.set_title("Distribuição das classes")
    axis.set_xlabel("Classe")
    axis.set_ylabel("Número de imagens")

    for bar, count in zip(bars, counts):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 5,
            str(count),
            ha="center",
            va="bottom",
        )

    figure.tight_layout()
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def create_sample_grid(class_samples, output_path):
    class_names = sorted(class_samples)

    if not class_names:
        return

    samples_per_class = min(
        6,
        min(len(class_samples[name]) for name in class_names),
    )

    if samples_per_class == 0:
        return

    figure, axes = plt.subplots(
        len(class_names),
        samples_per_class,
        figsize=(
            samples_per_class * 3,
            len(class_names) * 3,
        ),
        squeeze=False,
    )

    for row_index, class_name in enumerate(class_names):
        for column_index in range(samples_per_class):
            image_path = class_samples[class_name][column_index]

            with Image.open(image_path) as image:
                axes[row_index][column_index].imshow(
                    image.convert("RGB")
                )

            axes[row_index][column_index].axis("off")

            if column_index == 0:
                axes[row_index][column_index].set_ylabel(
                    class_name
                )

    figure.suptitle("Amostras do dataset por classe")
    figure.tight_layout()
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(
        description="Inspeciona o dataset de setas."
    )

    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="Pasta que contém as classes.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Pasta dos resultados.",
    )

    arguments = parser.parse_args()

    dataset_root = arguments.dataset.expanduser().resolve()
    output_root = arguments.output.expanduser().resolve()

    if not dataset_root.is_dir():
        raise FileNotFoundError(
            f"Dataset não encontrado: {dataset_root}"
        )

    output_root.mkdir(parents=True, exist_ok=True)

    image_paths = collect_images(dataset_root)

    if not image_paths:
        raise RuntimeError(
            f"Nenhuma imagem encontrada em: {dataset_root}"
        )

    print(f"Dataset: {dataset_root}")
    print(f"Total de imagens: {len(image_paths)}")

    results = inspect_images(
        image_paths,
        dataset_root,
    )

    class_counts = results["class_counts"]
    mode_counts = results["mode_counts"]
    size_counts = results["size_counts"]
    corrupted_files = results["corrupted_files"]
    class_samples = results["class_samples"]

    print("\nDistribuição das classes:")

    for class_name in sorted(class_counts):
        print(f"  {class_name}: {class_counts[class_name]}")

    print("\nModos de imagem:")

    for image_mode, count in mode_counts.most_common():
        print(f"  {image_mode}: {count}")

    print("\nDimensões mais frequentes:")

    for image_size, count in size_counts.most_common(20):
        print(f"  {image_size}: {count}")

    print(
        f"\nFicheiros corrompidos: {len(corrupted_files)}"
    )

    report = {
        "dataset_root": str(dataset_root),
        "total_images": len(image_paths),
        "class_counts": dict(sorted(class_counts.items())),
        "image_modes": dict(mode_counts.most_common()),
        "image_sizes": dict(size_counts.most_common()),
        "corrupted_files": corrupted_files,
    }

    report_path = output_root / "dataset_report.json"

    with report_path.open("w", encoding="utf-8") as report_file:
        json.dump(
            report,
            report_file,
            indent=2,
            ensure_ascii=False,
        )

    create_distribution_chart(
        class_counts,
        output_root / "class_distribution.png",
    )

    create_sample_grid(
        class_samples,
        output_root / "sample_images.png",
    )

    print("\nResultados criados:")
    print(f"  {report_path}")
    print(f"  {output_root / 'class_distribution.png'}")
    print(f"  {output_root / 'sample_images.png'}")


if __name__ == "__main__":
    main()
