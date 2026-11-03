"""ROS 2 node for arrow classification."""

import time
from pathlib import Path

import rclpy
import torch
from ament_index_python.packages import get_package_share_directory
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

from tsb_cv_brain.image_processing import image_message_to_tensor
from tsb_cv_brain.model import TurtleVisionCNN

EXPECTED_CLASSES = ["Down", "Left", "Right", "Up"]

CLASS_TO_COMMAND = {
    "Down": "DOWN",
    "Left": "LEFT",
    "Right": "RIGHT",
    "Up": "UP",
}


class VisionNode(Node):
    """Classify arrow images and publish direction commands."""

    def __init__(self):
        super().__init__("vision_node")

        self.declare_parameter("image_topic", "/vision/image")
        self.declare_parameter("command_topic", "/vision/command")
        self.declare_parameter("model_path", "")
        self.declare_parameter("minimum_confidence", 0.0)

        image_topic = self.get_parameter("image_topic").value
        command_topic = self.get_parameter("command_topic").value
        configured_path = self.get_parameter("model_path").value

        self.minimum_confidence = float(
            self.get_parameter("minimum_confidence").value
        )

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        model_path = self.resolve_model_path(configured_path)

        checkpoint = torch.load(
            model_path,
            map_location=self.device,
            weights_only=False,
        )

        self.classes = list(
            checkpoint.get("classes", EXPECTED_CLASSES)
        )

        if self.classes != EXPECTED_CLASSES:
            raise ValueError(
                f"Unexpected classes: {self.classes}"
            )

        expected_mapping = {
            name: index
            for index, name in enumerate(EXPECTED_CLASSES)
        }

        class_mapping = checkpoint.get(
            "class_to_index",
            expected_mapping,
        )

        if class_mapping != expected_mapping:
            raise ValueError(
                f"Unexpected class mapping: {class_mapping}"
            )

        self.image_size = int(
            checkpoint.get("image_size", 96)
        )

        self.normalization_mean = list(
            checkpoint.get(
                "normalization_mean",
                [0.5, 0.5, 0.5],
            )
        )

        self.normalization_std = list(
            checkpoint.get(
                "normalization_std",
                [0.5, 0.5, 0.5],
            )
        )

        self.model = TurtleVisionCNN(
            number_of_classes=len(self.classes)
        ).to(self.device)

        self.model.load_state_dict(
            checkpoint["model_state_dict"],
            strict=True,
        )

        self.model.eval()

        self.command_publisher = self.create_publisher(
            String,
            command_topic,
            10,
        )

        self.image_subscription = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            10,
        )

        self.get_logger().info(
            f"PyTorch {torch.__version__}, device: {self.device}"
        )
        self.get_logger().info(
            f"Loaded model: {model_path}"
        )
        self.get_logger().info(
            f"Classes: {self.classes}"
        )
        self.get_logger().info(
            f"Input size: {self.image_size}x{self.image_size}"
        )
        self.get_logger().info(
            f"Listening on {image_topic}"
        )
        self.get_logger().info(
            f"Publishing on {command_topic}"
        )

    @staticmethod
    def resolve_model_path(configured_path):
        """Resolve the configured or installed checkpoint."""
        if str(configured_path).strip():
            model_path = Path(
                configured_path
            ).expanduser().resolve()
        else:
            package_share = Path(
                get_package_share_directory(
                    "tsb_cv_brain"
                )
            )

            model_path = (
                package_share
                / "models"
                / "arrow_cnn_best.pth"
            )

        if not model_path.is_file():
            raise FileNotFoundError(
                f"Model not found: {model_path}"
            )

        return model_path

    def image_callback(self, message):
        """Classify one ROS image."""
        start_time = time.perf_counter()

        try:
            image_tensor = image_message_to_tensor(
                message=message,
                image_size=self.image_size,
                normalization_mean=self.normalization_mean,
                normalization_std=self.normalization_std,
                device=self.device,
            )

            with torch.inference_mode():
                logits = self.model(image_tensor)
                probabilities = torch.softmax(
                    logits,
                    dim=1,
                )

            confidence, predicted_index = probabilities.max(
                dim=1,
            )

            class_name = self.classes[
                int(predicted_index.item())
            ]

            command = CLASS_TO_COMMAND[class_name]
            confidence_value = float(confidence.item())

            if confidence_value < self.minimum_confidence:
                self.get_logger().warning(
                    f"Ignored {command}: confidence "
                    f"{confidence_value:.3f}"
                )
                return

            output_message = String()
            output_message.data = command

            self.command_publisher.publish(
                output_message
            )

            latency_ms = (
                time.perf_counter() - start_time
            ) * 1000.0

            self.get_logger().info(
                f"Prediction={command}; "
                f"confidence={confidence_value:.3f}; "
                f"latency={latency_ms:.1f} ms"
            )

        except Exception as error:
            self.get_logger().error(
                f"Image processing failed: "
                f"{type(error).__name__}: {error}"
            )


def main(args=None):
    """Initialize ROS 2 and run the vision node."""
    rclpy.init(args=args)
    node = None

    try:
        node = VisionNode()
        rclpy.spin(node)

    except (
        KeyboardInterrupt,
        ExternalShutdownException,
    ):
        pass

    finally:
        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
