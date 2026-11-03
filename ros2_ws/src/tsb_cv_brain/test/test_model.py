"""Tests for the arrow-classification neural network."""

from pathlib import Path

import torch

from tsb_cv_brain.model import TurtleVisionCNN


def test_model_output_shape():
    """The network must return four logits per image."""
    model = TurtleVisionCNN(number_of_classes=4)
    model.eval()

    image_batch = torch.rand(2, 3, 96, 96)

    with torch.inference_mode():
        output = model(image_batch)

    assert output.shape == (2, 4)


def test_checkpoint_is_compatible():
    """The installed checkpoint must match the network architecture."""
    package_root = Path(__file__).resolve().parents[1]
    checkpoint_path = (
        package_root
        / "models"
        / "arrow_cnn_best.pth"
    )

    assert checkpoint_path.is_file()

    checkpoint = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=False,
    )

    assert checkpoint["classes"] == [
        "Down",
        "Left",
        "Right",
        "Up",
    ]

    assert checkpoint["class_to_index"] == {
        "Down": 0,
        "Left": 1,
        "Right": 2,
        "Up": 3,
    }

    assert checkpoint["image_size"] == 96

    model = TurtleVisionCNN(number_of_classes=4)

    model.load_state_dict(
        checkpoint["model_state_dict"],
        strict=True,
    )
