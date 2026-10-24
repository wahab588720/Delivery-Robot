import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity
from geometry_msgs.msg import Twist

SDF_OBSTACLE = """<?xml version='1.0'?>
<sdf version='1.6'>
  <model name='dynamic_person'>
    <static>false</static>
    <link name='link'>
      <inertial>
        <mass>10.0</mass>
        <inertia>
          <ixx>10.0</ixx><ixy>0.0</ixy><ixz>0.0</ixz>
          <iyy>10.0</iyy><iyz>0.0</iyz><izz>1.0</izz>
        </inertia>
      </inertial>
      <!-- Main upright pillar -->
      <visual name='visual'>
        <pose>0 0 0.5 0 0 0</pose>
        <geometry><cylinder><radius>0.18</radius><length>1.0</length></cylinder></geometry>
        <material><ambient>1 0 0 1</ambient><diffuse>1 0 0 1</diffuse></material>
      </visual>
      <collision name='collision'>
        <pose>0 0 0.5 0 0 0</pose>
        <geometry><cylinder><radius>0.18</radius><length>1.0</length></cylinder></geometry>
      </collision>
    </link>
    <plugin name='planar_move' filename='libgazebo_ros_planar_move.so'>
      <ros><namespace>/dynamic_person</namespace></ros>
      <update_rate>50</update_rate>
      <publish_odom>false</publish_odom>
      <publish_odom_tf>false</publish_odom_tf>
      <odometry_frame>person_odom</odometry_frame>
      <robot_base_frame>person_base</robot_base_frame>
    </plugin>
  </model>
</sdf>"""

class DynamicObstacleNode(Node):
    def __init__(self):
        super().__init__('dynamic_obstacle_node')
        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')
        self.cmd_pub = self.create_publisher(Twist, '/dynamic_person/cmd_vel', 10)

        while not self.spawn_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info('Waiting for /spawn_entity service...')

        self.spawn_obstacle()

        # Movement parameters (Patrol along Y corridor)
        self.direction = 1.0
        self.speed = 0.2
        self.steps = 0
        self.max_steps = 25

        self.timer = self.create_timer(0.1, self.patrol_loop)
        self.get_logger().info('Obstacle standing upright and patrolling.')

    def spawn_obstacle(self):
        req = SpawnEntity.Request()
        req.name = 'dynamic_person'
        req.xml = SDF_OBSTACLE
        # Position 1 meter ahead of Turtlebot (-2.0, -0.5)
        req.initial_pose.position.x = -1.0
        req.initial_pose.position.y = -0.5
        req.initial_pose.position.z = 0.0

        future = self.spawn_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

    def patrol_loop(self):
        msg = Twist()
        msg.linear.y = float(self.direction * self.speed)
        self.cmd_pub.publish(msg)

        self.steps += 1
        if self.steps >= self.max_steps:
            self.direction *= -1.0
            self.steps = 0

def main(args=None):
    rclpy.init(args=args)
    node = DynamicObstacleNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
