# Track 1: Indoor Delivery Robot with Safety Zones

## Must-Have Checklist & Implementation Plan

- [ ] **Delivery request service (pickup, drop-off)**
  - *Plan:* Create a custom `DeliveryRequest.srv` interface and a state machine node that navigates `TO_PICKUP` -> `TO_DROPOFF` using Nav2's `NavigateToPose` action, storing incoming requests in a FIFO queue while busy.
- [ ] **Keep-out zone ("wet floor" / restricted room)**
  - *Plan:* Configure a Nav2 keepout costmap filter using a grayscale `.pgm` mask image, and check drop-off coordinates against the mask before accepting a request so invalid goals are rejected with a clear reason.
- [ ] **Slow zone (corridor speed limit)**
  - *Plan:* Configure a Nav2 speed-limit costmap filter with a zone mask that publishes speed restrictions to cap the controller velocity inside the corridor.
- [ ] **Yielding to a scripted moving "person"**
  - *Plan:* Create a scripted obstacle publisher/actor crossing the robot's path and tune local costmap inflation and range check logic so the robot slows, pauses, or reroutes without collision before resuming.
- [ ] **Simulated battery monitor and auto-docking**
  - *Plan:* Subscribe to a `/battery_level` topic; when below the threshold (e.g., 20%), safely finish or abort the active leg, navigate to the dock coordinates (`RETURNING` -> `CHARGING`), and reject new requests until recharged.
- [ ] **Status topic publishing state and rejection reasons**
  - *Plan:* Publish a `/delivery_status` topic reporting the current state (`IDLE`, `TO_PICKUP`, `TO_DROPOFF`, `RETURNING`, `CHARGING`) and the latest rejection reason.


# Delivery Robot Run Sequence

Terminal 1 (Headless Simulation):
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py gui:=false

Terminal 2 (Nav2 & RViz):
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=true

Terminal 3 (Localize Robot):
ros2 topic pub -1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped "{header: {frame_id: 'map'}, pose: {pose: {position: {x: -2.0, y: -0.5, z: 0.0}, orientation: {w: 1.0}}}}"

Terminal 4 (Start Delivery Server):
source ~/ros2_ws/install/setup.bash
ros2 run delivery_robot delivery_server

Terminal 5 (Trigger Delivery):
source ~/ros2_ws/install/setup.bash
ros2 service call /delivery_request std_srvs/srv/Trigger
