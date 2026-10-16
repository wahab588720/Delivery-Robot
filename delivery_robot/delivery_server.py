import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from delivery_interfaces.srv import DeliveryRequest
from delivery_interfaces.msg import DeliveryStatus
from collections import deque

class DeliveryServer(Node):
    def __init__(self):
        super().__init__('delivery_server')
        
        # Internal states: IDLE, TO_PICKUP, TO_DROPOFF, RETURNING, CHARGING
        self.state = 'IDLE'
        self.reason = 'None'
        self.request_queue = deque()
        self.current_goal_handle = None
        
        # Action client for Nav2
        self._nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Service & Publisher
        self.srv = self.create_service(DeliveryRequest, 'delivery_request', self.handle_delivery_request)
        self.status_pub = self.create_publisher(DeliveryStatus, 'delivery_status', 10)
        
        # State machine loop timer (5 Hz to keep VM CPU load low)
        self.timer = self.create_timer(0.2, self.state_machine_loop)
        
        self.get_logger().info('Delivery Server Node initialized with Nav2 Action Client.')

    def handle_delivery_request(self, request, response):
        if request.pickup_x == request.dropoff_x and request.pickup_y == request.dropoff_y:
            response.accepted = False
            response.reason = 'Pickup and dropoff coordinates are identical.'
            self.get_logger().warn(f'Rejected: {response.reason}')
            return response

        response.accepted = True
        response.reason = 'Accepted and added to queue.'
        self.request_queue.append(request)
        self.get_logger().info(f'Request accepted. Pending in queue: {len(self.request_queue)}')
        return response

    def send_nav_goal(self, x, y):
        if not self._nav_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().warn('Nav2 navigate_to_pose action server not available yet.')
            return False

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.orientation.w = 1.0

        send_goal_future = self._nav_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)
        return True

    def goal_response_callback(self, future):
        self.current_goal_handle = future.result()
        if not self.current_goal_handle.accepted:
            self.get_logger().error('Nav2 goal rejected.')
            self.state = 'IDLE'
            return

        self.get_logger().info('Nav2 goal accepted. Navigating...')
        result_future = self.current_goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_result_callback)

    def goal_result_callback(self, future):
        status = future.result().status
        self.get_logger().info(f'Navigation goal finished with status: {status}')
        
        if self.state == 'TO_PICKUP':
            self.get_logger().info('Reached pickup point. Navigating to drop-off...')
            self.state = 'TO_DROPOFF'
            self.send_nav_goal(self.current_request.dropoff_x, self.current_request.dropoff_y)

        elif self.state == 'TO_DROPOFF':
            self.get_logger().info('Delivery complete.')
            if len(self.request_queue) > 0:
                self.state = 'IDLE'
            else:
                self.state = 'RETURNING'
                self.send_nav_goal(0.0, 0.0)  # Return to origin/dock coordinates

        elif self.state == 'RETURNING':
            self.get_logger().info('Docked at base. Charging complete.')
            self.state = 'IDLE'

    def state_machine_loop(self):
        if self.state == 'IDLE' and len(self.request_queue) > 0:
            self.current_request = self.request_queue.popleft()
            self.state = 'TO_PICKUP'
            self.get_logger().info(f'Processing task: Sending goal to pickup ({self.current_request.pickup_x}, {self.current_request.pickup_y})')
            self.send_nav_goal(self.current_request.pickup_x, self.current_request.pickup_y)

        # Publish status
        msg = DeliveryStatus()
        msg.state = self.state
        msg.reason = self.reason
        msg.queue_size = int(len(self.request_queue))
        self.status_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = DeliveryServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
