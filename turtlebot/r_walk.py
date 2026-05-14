from geometry_msgs.msg import Point
import time
from rclpy.node import Node

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Point

import math
import numpy as np


class r_walk(Node):
    def __init__(self):
        super().__init__('r_walk')
        self.publisher_ = self.create_publisher(Point, '/target_point', 10)
        
        msg = Point()
        msg.x = 1.0
        msg.y = 1.0
        #msg = [1.0,1.0]
        print("line 15")
        while True:
            self.publisher_.publish(msg)
            print("line 17")
            print("should be publishing.")
            time.sleep(10)
    
def main(args = None):
    rclpy.init(args = args)
    
    r_walk_client = r_walk()
    
    rclpy.spin(r_walk_client)
    r_walk_client.destroy_node()
    rclpy.shutdown()

    
if __name__ == '__main__':
    main()