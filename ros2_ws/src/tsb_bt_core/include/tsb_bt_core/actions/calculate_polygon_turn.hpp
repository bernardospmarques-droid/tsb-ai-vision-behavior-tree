#ifndef TSB_BT_CORE__ACTIONS__CALCULATE_POLYGON_TURN_HPP_
#define TSB_BT_CORE__ACTIONS__CALCULATE_POLYGON_TURN_HPP_

#include <cmath>
#include <string>

#include "behaviortree_cpp/action_node.h"

namespace tsb_bt_core
{

class CalculatePolygonTurn : public BT::SyncActionNode
{
public:
  CalculatePolygonTurn(
    const std::string & name,
    const BT::NodeConfig & config)
  : BT::SyncActionNode(name, config)
  {
  }

  static BT::PortsList providedPorts()
  {
    return {
      BT::InputPort<int>("number_of_sides", 6, "Number of polygon sides, from 3 to 12"),
      BT::InputPort<double>("angular_speed", 1.5, "Absolute angular speed in rad/s"),
      BT::OutputPort<double>("turn_duration", "Calculated duration for one exterior turn")
    };
  }

  BT::NodeStatus tick() override
  {
    const auto sides_result = getInput<int>("number_of_sides");
    const auto speed_result = getInput<double>("angular_speed");

    if (!sides_result || !speed_result) {
      return BT::NodeStatus::FAILURE;
    }

    const int sides = sides_result.value();
    const double angular_speed = std::abs(speed_result.value());

    if (sides < 3 || sides > 12 || angular_speed <= 0.0) {
      return BT::NodeStatus::FAILURE;
    }

    constexpr double pi = 3.14159265358979323846;
    const double turn_duration = (2.0 * pi) / (static_cast<double>(sides) * angular_speed);
    setOutput("turn_duration", turn_duration);
    return BT::NodeStatus::SUCCESS;
  }
};

}  // namespace tsb_bt_core

#endif  // TSB_BT_CORE__ACTIONS__CALCULATE_POLYGON_TURN_HPP_
