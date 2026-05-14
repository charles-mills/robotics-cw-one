import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Point

import math
import numpy as np

class NavigationClient(Node):
    
    def __init__(self):
        super().__init__('navigationclient')
        # Nagivation uses actions rather than messages, meaning they don't use topics!
        # You don't need to worry about this, but that's why it looks different.
        self._action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        
        self.goal_point = None    
        self.goal_handle = None
        
        # we create a topic where target points will be sent to
        self._point_subscriber = self.create_subscription(
            Point,
            '/target_point',
            self._point_callback,
            10
        )
        
    def _point_callback(self, msg):
        x = msg.x
        y = msg.y
        z = 0.0 # The robot can't fly!
        
        angle = 0.0 #For simplicity
        
        goalmsg = self.create_posemsg(x,y, angle)
        self.send_goal(goalmsg)
        

    def create_posemsg(self, x,y, theta=0.0):
        # The nav stack is expecting a PoseStamped message
        # We provide this function to automatically generate this message for you
        # from just the target x, y and facing angle.
        goal = PoseStamped()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.header.frame_id = 'map'
            
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.position.z = 0.0
        goal.pose.orientation.w = theta

        return goal # This goal will need to sent to the nav2 stack

    def send_goal(self, posemsg: PoseStamped):
        # This function sends a pose goal to the nav2 stack.
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = posemsg
        
        # Because this is an action and not a topic, we must ensure the nav2 server is alive and well
        self._action_client.wait_for_server()
        # Then we send the goal asyncronously (Our code will keep running, and won't wait for the goal to finish!)
        future = self._action_client.send_goal_async(goal_msg)
        
        # However, it's useful to know if the message arrived OK, hence we add a "future callback"
        # This basically says "when the message is sent, run this function (goal_response_callback)"
        future.add_done_callback(self.goal_response_callback)
 
    def goal_response_callback(self, future):
        # This function handles our nav2 future.
        goal_handle = future.result()
        if not goal_handle.accepted:
            # If the goal was not accepted, we print the below...
            self.get_logger().warn("Goal REJECTED by Nav2")
            return # and return.
        # Otherwise we print to the terminal to inform the goal was accepted
        self.get_logger().warn("Goal accepted")
        
        # Similarly to above, we want to know if our robot made it to the goal successfully!
        # This sets up a future callback which will run when the nav2 stack is done, hence get_result..
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_result_callback)
    
    def goal_result_callback(self, future):
        # This function runs when the robot makes it to it's destination. (Or fails to do so!)
        self.get_logger().info("Goal reached")
        
        

def main(args = None):
    rclpy.init(args = args)
    
    action_client = NavigationClient()
    
    rclpy.spin(action_client)
    action_client.destroy_node()
    rclpy.shutdown()

    
if __name__ == '__main__':
    main()