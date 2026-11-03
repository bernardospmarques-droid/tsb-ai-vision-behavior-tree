"""Conversion of ROS image messages into normalized PyTorch tensors."""

from typing import Sequence

import numpy as np
import torch
from sensor_msgs.msg import Image
from torch.nn import functional as functional


SUPPORTED_ENCODINGS = {
    "rgb8",
    "bgr8",
    "rgba8",
    "bgra8",
    "mono8",
}


def _decode_image(message: Image) -> np.ndarray:
    """Decode a ROS Image message as a contiguous RGB NumPy array."""
    if message.height <= 0 or message.width <= 0:
        raise ValueError("Image height and width must be positive")

    encoding = message.encoding.lower()

    if encoding not in SUPPORTED_ENCODINGS:
        raise ValueError(
            f"Unsupported image encoding '{message.encoding}'. "
            f"Supported encodings: {sorted(SUPPORTED_ENCODINGS)}"
        )

    channels_by_encoding = {
        "rgb8": 3,
        "bgr8": 3,
        "rgba8": 4,
        "bgra8": 4,
        "mono8": 1,
    }

    channels = channels_by_encoding[encoding]
    minimum_step = message.width * channels

    if message.step < minimum_step:
        raise ValueError(
            f"Invalid image step {message.step}; "
            f"expected at least {minimum_step}"
        )

    raw_data = np.frombuffer(message.data, dtype=np.uint8)
    expected_size = message.height * message.step

    if raw_data.size < expected_size:
        raise ValueError(
            f"Image contains {raw_data.size} bytes; "
            f"expected at least {expected_size}"
        )

    rows = raw_data[:expected_size].reshape(
        message.height,
        message.step,
    )

    pixels = rows[:, :minimum_step].reshape(
        message.height,
        message.width,
        channels,
    )

    if encoding == "mono8":
        pixels = np.repeat(pixels, 3, axis=2)

    elif encoding == "bgr8":
        pixels = pixels[:, :, ::-1]

    elif encoding == "rgba8":
        pixels = pixels[:, :, :3]

    elif encoding == "bgra8":
        pixels = pixels[:, :, :3]
        pixels = pixels[:, :, ::-1]

    return np.ascontiguousarray(pixels)


def image_message_to_tensor(
    message: Image,
    image_size: int,
    normalization_mean: Sequence[float],
    normalization_std: Sequence[float],
    device: torch.device,
) -> torch.Tensor:
    """Convert a ROS Image message into a normalized NCHW tensor."""
    if image_size <= 0:
        raise ValueError("image_size must be positive")

    if len(normalization_mean) != 3:
        raise ValueError("normalization_mean must contain three values")

    if len(normalization_std) != 3:
        raise ValueError("normalization_std must contain three values")

    if any(value <= 0 for value in normalization_std):
        raise ValueError("normalization_std values must be positive")

    rgb_image = _decode_image(message)

    tensor = torch.from_numpy(rgb_image)
    tensor = tensor.permute(2, 0, 1)
    tensor = tensor.unsqueeze(0)
    tensor = tensor.to(
        device=device,
        dtype=torch.float32,
        non_blocking=True,
    )
    tensor = tensor / 255.0

    tensor = functional.interpolate(
        tensor,
        size=(image_size, image_size),
        mode="bilinear",
        align_corners=False,
    )

    mean = torch.tensor(
        normalization_mean,
        dtype=torch.float32,
        device=device,
    ).view(1, 3, 1, 1)

    standard_deviation = torch.tensor(
        normalization_std,
        dtype=torch.float32,
        device=device,
    ).view(1, 3, 1, 1)

    return (tensor - mean) / standard_deviation
