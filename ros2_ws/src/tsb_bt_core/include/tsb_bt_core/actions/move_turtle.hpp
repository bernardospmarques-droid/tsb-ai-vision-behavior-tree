#ifndef TSB_BT_CORE__ACTIONS__MOVE_TURTLE_HPP_
#define TSB_BT_CORE__ACTIONS__MOVE_TURTLE_HPP_

#include <chrono>
#include <string>
#include <utility>

#include "behaviortree_cpp/action_node.h"
#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"

namespace tsb_bt_core
{

/**
 * @brief Converts a semantic direction into a velocity command for Turtlesim.
 *
 * ROS interface:
 *   Publishes geometry_msgs/msg/Twist on /turtle1/cmd_vel.
 *
 * BT interface:
 *   Input port "command": UP, DOWN, LEFT or RIGHT.
 *
 * This is a StatefulActionNode because the movement takes place over time.
 * The node returns RUNNING while the turtle is moving and publishes a stop
 * command when the movement ends or is interrupted.
 */
class MoveTurtle : public BT::StatefulActionNode
{
public:
  static constexpr const char * kCmdVelTopic = "/turtle1/cmd_vel";

  MoveTurtle(
    const std::string & name,
    const BT::NodeConfig & config,
    rclcpp::Node::SharedPtr node)
  : BT::StatefulActionNode(name, config),
    node_(std::move(node))
  {
    cmd_vel_pub_ = node_->create_publisher<geometry_msgs::msg::Twist>(
      kCmdVelTopic,
      rclcpp::QoS(10));
  }

  static BT::PortsList providedPorts()
  {
    return {
      BT::InputPort<std::string>(
        "command",
        "Direction to move: UP | DOWN | LEFT | RIGHT"),

      BT::InputPort<double>(
        "linear_speed",
        2.0,
        "Absolute linear speed"),

      BT::InputPort<double>(
        "angular_speed",
        1.5,
        "Absolute angular speed"),

      BT::InputPort<double>(
        "duration",
        0.8,
        "Movement duration in seconds")
    };
  }

  BT::NodeStatus onStart() override
  {
    const auto command_result = getInput<std::string>("command");
    const auto linear_result = getInput<double>("linear_speed");
    const auto angular_result = getInput<double>("angular_speed");
    const auto duration_result = getInput<double>("duration");

    if (!command_result) {
      RCLCPP_ERROR(
        node_->get_logger(),
        "[%s] Missing input 'command': %s",
        name().c_str(),
        command_result.error().c_str());

      publishStop();
      return BT::NodeStatus::FAILURE;
    }

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

    const std::string command = command_result.value();
    const double linear_speed = linear_result.value();
    const double angular_speed = angular_result.value();

    duration_seconds_ = duration_result.value();

    if (
      linear_speed < 0.0 ||
      angular_speed < 0.0 ||
      duration_seconds_ <= 0.0)
    {
      RCLCPP_ERROR(
        node_->get_logger(),
        "[%s] Speeds must be non-negative and duration must be positive",
        name().c_str());

      publishStop();
      return BT::NodeStatus::FAILURE;
    }

    active_twist_ = geometry_msgs::msg::Twist();

    if (command == "UP") {
      active_twist_.linear.x = linear_speed;
      active_twist_.angular.z = 0.0;
    } else if (command == "DOWN") {
      active_twist_.linear.x = -linear_speed;
      active_twist_.angular.z = 0.0;
    } else if (command == "LEFT") {
      active_twist_.linear.x = 0.0;
      active_twist_.angular.z = angular_speed;
    } else if (command == "RIGHT") {
      active_twist_.linear.x = 0.0;
      active_twist_.angular.z = -angular_speed;
    } else {
      RCLCPP_WARN(
        node_->get_logger(),
        "[%s] Unsupported command: %s",
        name().c_str(),
        command.c_str());

      publishStop();
      return BT::NodeStatus::FAILURE;
    }

    start_time_ = std::chrono::steady_clock::now();

    config().blackboard->set("movement_running", true);

    cmd_vel_pub_->publish(active_twist_);

    RCLCPP_INFO(
      node_->get_logger(),
      "[%s] Command %s: linear.x=%.2f angular.z=%.2f duration=%.2f",
      name().c_str(),
      command.c_str(),
      active_twist_.linear.x,
      active_twist_.angular.z,
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
        "[%s] Movement completed",
        name().c_str());

      config().blackboard->set("movement_running", false);

      return BT::NodeStatus::SUCCESS;
    }

    cmd_vel_pub_->publish(active_twist_);

    return BT::NodeStatus::RUNNING;
  }

  void onHalted() override
  {
    publishStop();

    config().blackboard->set("movement_running", false);

    RCLCPP_INFO(
      node_->get_logger(),
      "[%s] Movement interrupted; turtle stopped",
      name().c_str());
  }

private:
  void publishStop()
  {
    geometry_msgs::msg::Twist stop_twist;

    stop_twist.linear.x = 0.0;
    stop_twist.angular.z = 0.0;

    cmd_vel_pub_->publish(stop_twist);
  }

  rclcpp::Node::SharedPtr node_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;

  geometry_msgs::msg::Twist active_twist_;
  std::chrono::steady_clock::time_point start_time_;
  double duration_seconds_{0.8};
};

}  // namespace tsb_bt_core

#endif  // TSB_BT_CORE__ACTIONS__MOVE_TURTLE_HPP_
