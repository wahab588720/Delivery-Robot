import rclpy
from delivery_robot.delivery_server import DeliveryServer

def test_node_initialization():
    rclpy.init()
    node = DeliveryServer()
    assert node.get_name() == 'delivery_server', "Node name mismatch"
    node.destroy_node()
    rclpy.shutdown()

def test_service_server_exists():
    rclpy.init()
    node = DeliveryServer()
    # Verify the /delivery_request service was created
    assert node.service is not None, "Service server not initialized"
    node.destroy_node()
    rclpy.shutdown()

def test_action_client_exists():
    rclpy.init()
    node = DeliveryServer()
    # Verify the Nav2 action client was created
    assert node.action_client is not None, "Action client not initialized"
    node.destroy_node()
    rclpy.shutdown()
