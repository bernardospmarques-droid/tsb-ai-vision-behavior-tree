#ifndef TSB_BT_CORE__ACTIONS__MOVE_CIRCULAR_HPP_
#define TSB_BT_CORE__ACTIONS__MOVE_CIRCULAR_HPP_

#include <chrono>
#include <string>
#include <utility>

#include "behaviortree_cpp/action_node.h"
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"

namespace tsb_bt_core
{

/**
 * @brief Moves the Turtlesim turtle along a circular trajectory.
 *
 * A circular trajectory is obtained by publishing linear and angular
 * velocity simultaneously.
 *
 * Approximate radius:
 *   radius = linear_speed / angular_speed
 *
 * Approximate duration for one full revolution:
 *   duration = 2 * pi / abs(angular_speed)
 */
class MoveCircular : public BT::StatefulActionNode
{
public:
  static constexpr const char * kCmdVelTopic = "/turtle1/cmd_vel";

  MoveCircular(
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
        "linear_speed",
        2.0,
        "Linear speed in turtlesim units per second"),

      BT::InputPort<double>(
        "angular_speed",
        1.0,
        "Angular speed in radians per second"),

      BT::InputPort<double>(
        "duration",
        6.283,
        "Movement duration in seconds")
    };
  }

  BT::NodeStatus onStart() override
  {
    const auto linear_result =
      getInput<double>("linear_speed");

    const auto angular_result =
      getInput<double>("angular_speed");

    const auto duration_result =
      getInput<double>("duration");

    if (!linear_result) {
      RCLCPP_ERROR(
        node_->get_logger(),
        "[%s] Invalid input 'linear_speed': %s",
        name().c_str(),
        linear_result.error().c_str());

      publishStop();
      return BT::NodeStatus::FAILURE;
    }

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

    linear_speed_ = linear_result.value();
    angular_speed_ = angular_result.value();
    duration_seconds_ = duration_result.value();

    if (linear_speed_ == 0.0) {
      RCLCPP_ERROR(
        node_->get_logger(),
        "[%s] Linear speed cannot be zero",
        name().c_str());

      publishStop();
      return BT::NodeStatus::FAILURE;
    }

    if (angular_speed_ == 0.0) {
      RCLCPP_ERROR(
        node_->get_logger(),
        "[%s] Angular speed cannot be zero",
        name().c_str());

      publishStop();
      return BT::NodeStatus::FAILURE;
    }

    if (duration_seconds_ <= 0.0) {
      RCLCPP_ERROR(
        node_->get_logger(),
        "[%s] Duration must be positive",
        name().c_str());

      publishStop();
      return BT::NodeStatus::FAILURE;
    }

    active_twist_ = geometry_msgs::msg::Twist();

    active_twist_.linear.x = linear_speed_;
    active_twist_.angular.z = angular_speed_;

    start_time_ = std::chrono::steady_clock::now();

    publisher_->publish(active_twist_);

    const double approximate_radius =
      linear_speed_ / angular_speed_;

    RCLCPP_INFO(
      node_->get_logger(),
      "[%s] Circular movement started: linear=%.2f, angular=%.2f, "
      "duration=%.3f, approximate radius=%.2f",
      name().c_str(),
      linear_speed_,
      angular_speed_,
      duration_seconds_,
      approximate_radius);

    return BT::NodeStatus::RUNNING;
  }

  BT::NodeStatus onRunning() override
  {
    const auto current_time =
      std::chrono::steady_clock::now();

    const std::chrono::duration<double> elapsed =
      current_time - start_time_;

    if (elapsed.count() >= duration_seconds_) {
      publishStop();

      RCLCPP_INFO(
        node_->get_logger(),
        "[%s] Circular movement completed",
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
      "[%s] Circular movement interrupted; turtle stopped",
      name().c_str());
  }

private:
  void publishStop()
  {
    geometry_msgs::msg::Twist stop_message;

    stop_message.linear.x = 0.0;
    stop_message.angular.z = 0.0;

    publisher_->publish(stop_message);
  }

  rclcpp::Node::SharedPtr node_;

  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr
    publisher_;

  geometry_msgs::msg::Twist active_twist_;

  std::chrono::steady_clock::time_point start_time_;

  double linear_speed_{2.0};
  double angular_speed_{1.0};
  double duration_seconds_{6.283};
};

}  // namespace tsb_bt_core

#endif  // TSB_BT_CORE__ACTIONS__MOVE_CIRCULAR_HPP_

