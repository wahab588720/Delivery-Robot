import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_srvs.srv import Trigger
from nav2_msgs.action import NavigateToPose

class DeliveryServer(Node):
    def __init__(self):
        super().__init__('delivery_server')
        # Service Server to listen for the trigger
        self.service = self.create_service(Trigger, 'delivery_request', self.trigger_callback)
        # Action Client to communicate with Nav2
        self.action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.get_logger().info("Delivery Server is ready. Waiting for requests...")

    def trigger_callback(self, request, response):
        self.get_logger().info("Delivery request received. Dispatching to Nav2...")
        
        if not self.action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Nav2 Action server offline.")
            response.success = False
            response.message = "Nav2 offline."
            return response

        # Package the target coordinates
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = 1.5
        goal_msg.pose.pose.position.y = 1.5
        goal_msg.pose.pose.orientation.w = 1.0

        # Send coordinate to Nav2
        self.action_client.send_goal_async(goal_msg)
        
        response.success = True
        response.message = "Coordinates accepted. Delivery to (1.5, 1.5) initiated."
        return response

def main(args=None):
    rclpy.init(args=args)
    node = DeliveryServer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
