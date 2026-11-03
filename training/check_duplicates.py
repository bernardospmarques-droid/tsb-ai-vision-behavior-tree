#!/usr/bin/env python3

import hashlib
from collections import defaultdict
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def calculate_hash(file_path):
    hash_object = hashlib.sha256()

    with file_path.open("rb") as image_file:
        while True:
            data = image_file.read(1024 * 1024)

            if not data:
                break

            hash_object.update(data)

    return hash_object.hexdigest()


def main():
    dataset_root = (
        Path.home()
        / "sa_recrutamento_ai"
        / "dataset"
        / "arrow_dataset"
        / "extracted"
        / "Direction"
    )

    image_paths = sorted(
        path
        for path in dataset_root.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )
    )

    hashes = defaultdict(list)

    for index, image_path in enumerate(
        image_paths,
        start=1,
    ):
        image_hash = calculate_hash(image_path)
        hashes[image_hash].append(image_path)

        if index % 500 == 0:
            print(
                f"Processadas {index}/{len(image_paths)} imagens"
            )

    duplicate_groups = [
        paths
        for paths in hashes.values()
        if len(paths) > 1
    ]

    cross_class_duplicates = []

    for group in duplicate_groups:
        classes = {
            path.parent.name
            for path in group
        }

        if len(classes) > 1:
            cross_class_duplicates.append(group)

    print()
    print("Total de imagens:", len(image_paths))

    print(
        "Grupos de duplicados exatos:",
        len(duplicate_groups),
    )

    print(
        "Duplicados entre classes diferentes:",
        len(cross_class_duplicates),
    )

    if duplicate_groups:
        print("\nPrimeiros grupos duplicados:")

        for group in duplicate_groups[:20]:
            print()

            for image_path in group:
                print(
                    " ",
                    image_path.relative_to(dataset_root),
                )


if __name__ == "__main__":
    main()
