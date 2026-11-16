#ifndef TSB_BT_CORE__ACTIONS__COMMAND_MEMORY_HPP_
#define TSB_BT_CORE__ACTIONS__COMMAND_MEMORY_HPP_

#include <string>

#include "behaviortree_cpp/action_node.h"

namespace tsb_bt_core
{

class CommandMemory : public BT::SyncActionNode
{
public:
  CommandMemory(
    const std::string& name,
    const BT::NodeConfig& config)
  : BT::SyncActionNode(name, config)
  {}

  static BT::PortsList providedPorts()
  {
    return {
      BT::InputPort<std::string>("command"),
      BT::OutputPort<bool>("repeat_command"),
      BT::OutputPort<std::string>("last_command")
    };
  }

  BT::NodeStatus tick() override
  {
    auto cmd = getInput<std::string>("command");

    if (!cmd) {
      return BT::NodeStatus::FAILURE;
    }

    const std::string current = cmd.value();

    auto bb = config().blackboard;

    std::string previous;

    if (!bb->get("last_command_memory", previous)) {
      previous = "";
    }

    const bool repeated =
      (current == previous) &&
      (
        current == "SQUARE" ||
        current == "CIRCLE" ||
        current == "REGULAR_POLYGON"
      );

    setOutput("repeat_command", repeated);
    setOutput("last_command", previous);

    bb->set("last_command_memory", current);

    return BT::NodeStatus::SUCCESS;
  }
};

}  // namespace tsb_bt_core

#endif
