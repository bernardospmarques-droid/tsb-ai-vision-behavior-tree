"""Convert browser canvas images into ROS Image messages."""

import base64
from io import BytesIO
from rclpy.executors import ExternalShutdownException
import numpy as np
from PIL import Image as PillowImage
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String


class CanvasBridge(Node):
    """Convert Base64 PNG messages into RGB ROS images."""

    def __init__(self):
        """Create the canvas subscriber and image publisher."""
        super().__init__('canvas_bridge')

        self.declare_parameter(
            'canvas_topic',
            '/vision/canvas_png',
        )

        self.declare_parameter(
            'image_topic',
            '/vision/image',
        )

        canvas_topic = str(
            self.get_parameter('canvas_topic').value
        )

        image_topic = str(
            self.get_parameter('image_topic').value
        )

        self.image_publisher = self.create_publisher(
            Image,
            image_topic,
            10,
        )

        self.canvas_subscription = self.create_subscription(
            String,
            canvas_topic,
            self.canvas_callback,
            10,
        )

        self.get_logger().info(
            f'Listening for canvas images on {canvas_topic}'
        )

        self.get_logger().info(
            f'Publishing RGB images on {image_topic}'
        )

    def canvas_callback(self, message):
        """Decode and publish one Base64-encoded canvas image."""
        try:
            encoded_data = message.data.strip()

            if ',' in encoded_data:
                encoded_data = encoded_data.split(
                    ',',
                    maxsplit=1,
                )[1]

            binary_data = base64.b64decode(
                encoded_data,
                validate=True,
            )

            pillow_image = PillowImage.open(
                BytesIO(binary_data)
            ).convert('RGB')

            image_array = np.asarray(
                pillow_image,
                dtype=np.uint8,
            )

            ros_message = Image()
            ros_message.header.stamp = (
                self.get_clock().now().to_msg()
            )
            ros_message.height = pillow_image.height
            ros_message.width = pillow_image.width
            ros_message.encoding = 'rgb8'
            ros_message.is_bigendian = 0
            ros_message.step = pillow_image.width * 3
            ros_message.data = image_array.tobytes()

            self.image_publisher.publish(
                ros_message
            )

            self.get_logger().info(
                f'Published canvas image: '
                f'{pillow_image.width}x'
                f'{pillow_image.height}'
            )

        except Exception as error:
            self.get_logger().error(
                f'Invalid canvas image: '
                f'{type(error).__name__}: {error}'
            )


def main(args=None):
    """Run the canvas bridge node."""
    rclpy.init(args=args)
    node = None

    try:
        node = CanvasBridge()
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


if __name__ == '__main__':
    main()
