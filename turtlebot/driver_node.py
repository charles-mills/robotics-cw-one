from sympy import Point
import rclpy
import json
from rclpy.node import Node
import paho.mqtt.client as mqtt
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3
import time
import math
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Point
import re

BROKER_IP = "10.250.6.18"


class driver_node(Node):
    
    def __init__(self):
        super().__init__('driver_node')
        

        self.publisher_ = self.create_publisher(Point, '/target_point', 10)
        self.poi_msg = Point()
        self.pt = Point()
        self.x = 1.0
        self.y = 1.0

        pointClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        pointClient.on_message = self.on_point_message
        pointClient.connect(BROKER_IP, 1883, 60)  
        pointClient.subscribe("MY_TAR")
        pointClient.loop_start()
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
    def on_point_message(self,client, userdata, msg):
        """
        This is triggered whenever a new message is published to the "MY_TAR" topic. 
        It parses the raw payload into X, Y and Z floats.

        Args:
            client (_type_): The MQTT client instance.
            userdata (_type_): User data.
            msg (_type_): MQTT message containing the payload and topic.
        """
        st = str(msg.payload)
        st = st[2:-1]

        split = [float(x.strip()) for x in st.split(",")]
        self.pt.x = split[0]
        self.pt.y = split[1]
        self.pt.z = split[2]
        
        self.publisher_.publish(self.pt)

def main(args=None):

    rclpy.init(args=args)
    driver = driver_node()    
    rclpy.spin(driver)    
    driver.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
        
    