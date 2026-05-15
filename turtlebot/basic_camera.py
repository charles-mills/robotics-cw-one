import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge



class BasicCamera(Node):
    
    def __init__(self):
        super().__init__('basic_camera_listener')
        
        self.cvb = CvBridge()
        self.subscriptions_image = self.create_subscription(
            Image,
            '/camera/camera/color/image_raw',
            self.image_callback,
            10)

        self.current_frame = None
    
    def image_callback(self, msg):
        """
        The callback is triggered whenever a new Image mesasge is published to the topic.
        It then converts teh message to a BGR8 OpenCV image and shows it on the window.

        Args:
            msg (_type_): The image message received from the topic.
        """

        self.current_frame = self.cvb.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        
        cv2.imshow('frame', self.current_frame) 
        cv2.waitKey(1)

def main(args=None): 
    rclpy.init(args=args)
    image_node = BasicCamera()
    rclpy.spin(image_node)
    image_node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()