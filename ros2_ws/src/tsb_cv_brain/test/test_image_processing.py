"""Tests for ROS image preprocessing."""

import numpy as np
import torch
from sensor_msgs.msg import Image

from tsb_cv_brain.image_processing import image_message_to_tensor


def create_image_message(
    pixels: np.ndarray,
    encoding: str,
) -> Image:
    """Create a ROS image message from a NumPy array."""
    message = Image()
    message.height = pixels.shape[0]
    message.width = pixels.shape[1]
    message.encoding = encoding
    message.is_bigendian = 0

    if pixels.ndim == 2:
        channels = 1
    else:
        channels = pixels.shape[2]

    message.step = message.width * channels
    message.data = pixels.tobytes()

    return message


def preprocess(message: Image) -> torch.Tensor:
    """Apply the production preprocessing configuration."""
    return image_message_to_tensor(
        message=message,
        image_size=96,
        normalization_mean=[0.5, 0.5, 0.5],
        normalization_std=[0.5, 0.5, 0.5],
        device=torch.device("cpu"),
    )


def test_rgb8_output_shape():
    """RGB images must produce one normalized RGB tensor."""
    pixels = np.zeros(
        (224, 224, 3),
        dtype=np.uint8,
    )

    tensor = preprocess(
        create_image_message(pixels, "rgb8")
    )

    assert tensor.shape == (1, 3, 96, 96)
    assert tensor.dtype == torch.float32


def test_bgr8_is_converted_to_rgb():
    """BGR channel order must be converted into RGB."""
    pixels = np.zeros(
        (1, 1, 3),
        dtype=np.uint8,
    )

    pixels[0, 0] = [0, 0, 255]

    tensor = preprocess(
        create_image_message(pixels, "bgr8")
    )

    red_mean = tensor[0, 0].mean()
    blue_mean = tensor[0, 2].mean()

    assert red_mean > blue_mean


def test_mono8_is_expanded_to_three_channels():
    """Monochrome images must be copied into three channels."""
    pixels = np.full(
        (20, 20),
        128,
        dtype=np.uint8,
    )

    tensor = preprocess(
        create_image_message(pixels, "mono8")
    )

    assert tensor.shape == (1, 3, 96, 96)

    assert torch.allclose(
        tensor[:, 0],
        tensor[:, 1],
    )

    assert torch.allclose(
        tensor[:, 1],
        tensor[:, 2],
    )


def test_unsupported_encoding_is_rejected():
    """Unsupported encodings must raise an explicit error."""
    pixels = np.zeros(
        (10, 10, 3),
        dtype=np.uint8,
    )

    message = create_image_message(
        pixels,
        "unsupported",
    )

    try:
        preprocess(message)
    except ValueError as error:
        assert "Unsupported image encoding" in str(error)
    else:
        raise AssertionError(
            "Unsupported encoding was accepted"
        )
