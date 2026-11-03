#ifndef TSB_BT_CORE__ACTIONS__MOVE_FORWARD_HPP_
#define TSB_BT_CORE__ACTIONS__MOVE_FORWARD_HPP_

#include <chrono>
#include <string>
#include <utility>

#include "behaviortree_cpp/action_node.h"
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"

namespace tsb_bt_core
{

class MoveForward : public BT::StatefulActionNode
{
public:
  static constexpr const char * kCmdVelTopic = "/turtle1/cmd_vel";

  MoveForward(
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
        "speed",
        2.0,
        "Forward linear speed"),

      BT::InputPort<double>(
        "duration",
        1.5,
        "Movement duration in seconds")
    };
  }

  BT::NodeStatus onStart() override
  {
    const auto speed_result = getInput<double>("speed");
    const auto duration_result = getInput<double>("duration");

    if (!speed_result) {
      RCLCPP_ERROR(
        node_->get_logger(),
        "[%s] Invalid input 'speed': %s",
        name().c_str(),
        speed_result.error().c_str());

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

    speed_ = speed_result.value();
    duration_seconds_ = duration_result.value();

    if (speed_ <= 0.0 || duration_seconds_ <= 0.0) {
      RCLCPP_ERROR(
        node_->get_logger(),
        "[%s] Speed and duration must be positive",
        name().c_str());

      publishStop();
      return BT::NodeStatus::FAILURE;
    }

    active_twist_ = geometry_msgs::msg::Twist();
    active_twist_.linear.x = speed_;
    active_twist_.angular.z = 0.0;

    start_time_ = std::chrono::steady_clock::now();

    publisher_->publish(active_twist_);

    RCLCPP_INFO(
      node_->get_logger(),
      "[%s] Moving forward: speed=%.2f, duration=%.2f",
      name().c_str(),
      speed_,
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
        "[%s] Forward movement completed",
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
      "[%s] Forward movement interrupted",
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

  double speed_{2.0};
  double duration_seconds_{1.5};
};

}  // namespace tsb_bt_core

#endif  // TSB_BT_CORE__ACTIONS__MOVE_FORWARD_HPP_
