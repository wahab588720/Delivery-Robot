#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "nav2_msgs/action/navigate_to_pose.hpp"
#include "std_srvs/srv/trigger.hpp"

using namespace std::placeholders;
using NavigateToPose = nav2_msgs::action::NavigateToPose;
using GoalHandleNav2 = rclcpp_action::ClientGoalHandle<NavigateToPose>;

class DeliveryServer : public rclcpp::Node {
public:
  DeliveryServer() : Node("delivery_server") {
    // Initialize Action Client to communicate with Nav2
    client_ptr_ = rclcpp_action::create_client<NavigateToPose>(this, "navigate_to_pose");

    // Initialize Service Server to listen for the trigger command
    service_ = this->create_service<std_srvs::srv::Trigger>(
      "delivery_request",
      std::bind(&DeliveryServer::handle_delivery_request, this, _1, _2));

    RCLCPP_INFO(this->get_logger(), "Delivery Server is ready. Waiting for requests...");
  }

private:
  rclcpp_action::Client<NavigateToPose>::SharedPtr client_ptr_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr service_;

  void handle_delivery_request(const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
                               std::shared_ptr<std_srvs::srv::Trigger::Response> response) {
    (void)request; // Unused for a basic Trigger
    
    if (!client_ptr_->wait_for_action_server(std::chrono::seconds(5))) {
      RCLCPP_ERROR(this->get_logger(), "Nav2 Action server offline or unreachable.");
      response->success = false;
      response->message = "Nav2 offline.";
      return;
    }

    // Package the coordinate variables
    auto goal_msg = NavigateToPose::Goal();
    goal_msg.pose.header.frame_id = "map";
    goal_msg.pose.header.stamp = this->now();
    goal_msg.pose.pose.position.x = 1.5;
    goal_msg.pose.pose.position.y = 1.5;
    goal_msg.pose.pose.orientation.w = 1.0;

    auto send_goal_options = rclcpp_action::Client<NavigateToPose>::SendGoalOptions();
    send_goal_options.result_callback =
      std::bind(&DeliveryServer::result_callback, this, _1);

    // Send to Nav2
    client_ptr_->async_send_goal(goal_msg, send_goal_options);
    
    response->success = true;
    response->message = "Coordinates accepted. Delivery to (1.5, 1.5) initiated.";
    RCLCPP_INFO(this->get_logger(), "Sending target coordinates to Nav2...");
  }

  void result_callback(const GoalHandleNav2::WrappedResult & result) {
    switch (result.code) {
      case rclcpp_action::ResultCode::SUCCEEDED:
        RCLCPP_INFO(this->get_logger(), "Target reached. Delivery SUCCEEDED!");
        break;
      case rclcpp_action::ResultCode::ABORTED:
        RCLCPP_ERROR(this->get_logger(), "Navigation ABORTED by Nav2.");
        break;
      case rclcpp_action::ResultCode::CANCELED:
        RCLCPP_ERROR(this->get_logger(), "Navigation CANCELED.");
        break;
      default:
        RCLCPP_ERROR(this->get_logger(), "Unknown result code.");
        break;
    }
  }
};

int main(int argc, char ** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<DeliveryServer>());
  rclcpp::shutdown();
  return 0;
}
