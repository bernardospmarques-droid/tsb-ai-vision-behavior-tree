"""Publish an image file as a ROS sensor_msgs/Image message."""

from pathlib import Path
import time

from PIL import Image as PillowImage
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class ImagePublisher(Node):
    """Publish an RGB image file on the vision input topic."""

    def __init__(self) -> None:
        """Declare parameters and create the ROS publisher."""
        super().__init__("image_publisher")

        self.declare_parameter("image_path", "")
        self.declare_parameter("image_topic", "/vision/image")
        self.declare_parameter("repeat_count", 1)
        self.declare_parameter("publish_interval", 0.2)

        image_path = str(
            self.get_parameter("image_path").value
        )

        image_topic = str(
            self.get_parameter("image_topic").value
        )

        self.repeat_count = int(
            self.get_parameter("repeat_count").value
        )

        self.publish_interval = float(
            self.get_parameter("publish_interval").value
        )

        if not image_path.strip():
            raise ValueError(
                "The image_path parameter must be provided"
            )

        if self.repeat_count <= 0:
            raise ValueError(
                "repeat_count must be positive"
            )

        if self.publish_interval <= 0.0:
            raise ValueError(
                "publish_interval must be positive"
            )

        self.image_path = Path(
            image_path
        ).expanduser().resolve()

        if not self.image_path.is_file():
            raise FileNotFoundError(
                f"Image not found: {self.image_path}"
            )

        self.message = self.load_image(
            self.image_path
        )

        self.publisher = self.create_publisher(
            Image,
            image_topic,
            10,
        )

        self.published_count = 0

        self.timer = self.create_timer(
            self.publish_interval,
            self.publish_image,
        )

        self.get_logger().info(
            f"Image: {self.image_path}"
        )
        self.get_logger().info(
            f"Publishing to: {image_topic}"
        )
        self.get_logger().info(
            f"Repeat count: {self.repeat_count}"
        )

    @staticmethod
    def load_image(image_path: Path) -> Image:
        """Load an image file and convert it into a ROS message."""
        pillow_image = PillowImage.open(
            image_path
        ).convert("RGB")

        message = Image()
        message.height = pillow_image.height
        message.width = pillow_image.width
        message.encoding = "rgb8"
        message.is_bigendian = 0
        message.step = pillow_image.width * 3
        message.data = pillow_image.tobytes()

        return message

    def publish_image(self) -> None:
        """Publish the configured image and stop when finished."""
        self.message.header.stamp = (
            self.get_clock().now().to_msg()
        )

        self.publisher.publish(
            self.message
        )

        self.published_count += 1

        self.get_logger().info(
            f"Published image "
            f"{self.published_count}/{self.repeat_count}"
        )

        if self.published_count >= self.repeat_count:
            self.timer.cancel()

            self.get_logger().info(
                "Image publication completed"
            )


def main(args=None) -> None:
    """Initialize ROS 2 and publish the configured image."""
    rclpy.init(args=args)
    node = None

    try:
        node = ImagePublisher()

        while (
            rclpy.ok()
            and node.published_count < node.repeat_count
        ):
            rclpy.spin_once(
                node,
                timeout_sec=0.1,
            )

        time.sleep(0.3)

    except KeyboardInterrupt:
        pass

    finally:
        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
