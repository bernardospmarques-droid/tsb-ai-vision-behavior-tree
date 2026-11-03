#ifndef TSB_BT_CORE__ACTIONS__ROTATE_HPP_
#define TSB_BT_CORE__ACTIONS__ROTATE_HPP_

#include <chrono>
#include <string>
#include <utility>

#include "behaviortree_cpp/action_node.h"
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"

namespace tsb_bt_core
{

class Rotate : public BT::StatefulActionNode
{
public:
  static constexpr const char * kCmdVelTopic = "/turtle1/cmd_vel";

  Rotate(
    const std::string & name,
    const BT::NodeConfig & config,
    rclcpp::Node::SharedPtr node)
  : BT::StatefulActionNode(name, config),
    node_(std::move(node))
  {
    publisher_ = node_->create_publisher<geometry_msgs::msg::Twist>(
      kCmdVelTopic,
      rclcpp::QoS(10));
  }

  static BT::PortsList providedPorts()
  {
    return {
      BT::InputPort<double>(
        "angular_speed",
        1.5708,
        "Angular speed in radians per second"),

      BT::InputPort<double>(
        "duration",
        1.0,
        "Rotation duration in seconds")
    };
  }

  BT::NodeStatus onStart() override
  {
    const auto angular_result = getInput<double>("angular_speed");
    const auto duration_result = getInput<double>("duration");

    if (!angular_result) {
      RCLCPP_ERROR(
        node_->get_logger(),
        "[%s] Invalid input 'angular_speed': %s",
        name().c_str(),
        angular_result.error().c_str());

      publishStop();
      return BT::NodeStatus::FAILURE;
    }

    if (!duration_result) {
      RCLCPP_ERROR(
        node_->get_logger(),
        "[%s] Invalid input 'duration': %s",
        name().c_str(),
        duration_result.error().c_str());

      publishStop();
      return BT::NodeStatus::FAILURE;
    }

    angular_speed_ = angular_result.value();
    duration_seconds_ = duration_result.value();

    if (angular_speed_ == 0.0 || duration_seconds_ <= 0.0) {
      RCLCPP_ERROR(
        node_->get_logger(),
        "[%s] Angular speed cannot be zero and duration must be positive",
        name().c_str());

      publishStop();
      return BT::NodeStatus::FAILURE;
    }

    active_twist_ = geometry_msgs::msg::Twist();
    active_twist_.linear.x = 0.0;
    active_twist_.angular.z = angular_speed_;

    start_time_ = std::chrono::steady_clock::now();

    publisher_->publish(active_twist_);

    RCLCPP_INFO(
      node_->get_logger(),
      "[%s] Rotating: angular_speed=%.4f, duration=%.2f",
      name().c_str(),
      angular_speed_,
      duration_seconds_);

    return BT::NodeStatus::RUNNING;
  }

  BT::NodeStatus onRunning() override
  {
    const auto now = std::chrono::steady_clock::now();

    const std::chrono::duration<double> elapsed =
      now - start_time_;

    if (elapsed.count() >= duration_seconds_) {
      publishStop();

      RCLCPP_INFO(
        node_->get_logger(),
        "[%s] Rotation completed",
        name().c_str());

      return BT::NodeStatus::SUCCESS;
    }

    publisher_->publish(active_twist_);

    return BT::NodeStatus::RUNNING;
  }

  void onHalted() override
  {
    publishStop();

    RCLCPP_INFO(
      node_->get_logger(),
      "[%s] Rotation interrupted",
      name().c_str());
  }

private:
  void publishStop()
  {
    geometry_msgs::msg::Twist stop_message;
    publisher_->publish(stop_message);
  }

  rclcpp::Node::SharedPtr node_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;

  geometry_msgs::msg::Twist active_twist_;
  std::chrono::steady_clock::time_point start_time_;

  double angular_speed_{1.5708};
  double duration_seconds_{1.0};
};

}  // namespace tsb_bt_core

#endif  // TSB_BT_CORE__ACTIONS__ROTATE_HPP_
