#ifndef TSB_BT_CORE__ACTIONS__GET_VISION_COMMAND_HPP_
#define TSB_BT_CORE__ACTIONS__GET_VISION_COMMAND_HPP_

#include <mutex>
#include <optional>
#include <string>
#include <utility>

#include "behaviortree_cpp/action_node.h"
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

namespace tsb_bt_core
{

/**
 * @brief Wait for a vision command and write it to the BT blackboard.
 *
 * The ROS callback runs in the executor thread. Behavior Tree ticks run
 * in the main thread, so access to latest_command_ is protected by a mutex.
 */
class GetVisionCommand : public BT::StatefulActionNode
{
public:
  static constexpr const char * kCommandTopic = "/vision/command";

  GetVisionCommand(
    const std::string & name,
    const BT::NodeConfig & config,
    rclcpp::Node::SharedPtr node)
  : BT::StatefulActionNode(name, config),
    node_(std::move(node))
  {
    subscription_ =
      node_->create_subscription<std_msgs::msg::String>(
      kCommandTopic,
      rclcpp::QoS(10),
      [this](const std_msgs::msg::String::SharedPtr message) {
        std::lock_guard<std::mutex> lock(mutex_);
        latest_command_ = message->data;
      });
  }

  static BT::PortsList providedPorts()
  {
    return {
      BT::OutputPort<std::string>(
        "command",
        "UP, DOWN, LEFT or RIGHT"),
    };
  }

  BT::NodeStatus onStart() override
  {
    RCLCPP_DEBUG(
      node_->get_logger(),
      "[%s] Waiting for a vision command",
      name().c_str());

    return readCommand();
  }

  BT::NodeStatus onRunning() override
  {
    return readCommand();
  }

  void onHalted() override
  {
    RCLCPP_DEBUG(
      node_->get_logger(),
      "[%s] Command wait halted",
      name().c_str());
  }

private:
  BT::NodeStatus readCommand()
  {
    std::optional<std::string> command;

    {
      std::lock_guard<std::mutex> lock(mutex_);

      if (!latest_command_.has_value()) {
        return BT::NodeStatus::RUNNING;
      }

      command = latest_command_;
      latest_command_.reset();
    }

    if (!isValidCommand(command.value())) {
      RCLCPP_WARN(
        node_->get_logger(),
        "[%s] Ignoring invalid command: %s",
        name().c_str(),
        command.value().c_str());

      return BT::NodeStatus::RUNNING;
    }

    setOutput("command", command.value());

    RCLCPP_INFO(
      node_->get_logger(),
      "[%s] Command written to blackboard: %s",
      name().c_str(),
      command.value().c_str());

    return BT::NodeStatus::SUCCESS;
  }

  static bool isValidCommand(const std::string & command)
  {
    return
      command == "UP" ||
      command == "DOWN" ||
      command == "LEFT" ||
      command == "RIGHT";
  }

  rclcpp::Node::SharedPtr node_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;

  std::mutex mutex_;
  std::optional<std::string> latest_command_;
};

}  // namespace tsb_bt_core

#endif  // TSB_BT_CORE__ACTIONS__GET_VISION_COMMAND_HPP_
