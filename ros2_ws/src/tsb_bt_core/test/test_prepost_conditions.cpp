#include <behaviortree_cpp/bt_factory.h>

#include <chrono>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>

namespace
{

void require(const bool condition, const std::string & message)
{
  if (!condition) {
    throw std::runtime_error(message);
  }
}

BT::NodeStatus tick_to_completion(BT::Tree & tree)
{
  BT::NodeStatus status = BT::NodeStatus::IDLE;

  for (int iteration = 0; iteration < 1000; ++iteration) {
    status = tree.tickOnce();

    if (status != BT::NodeStatus::RUNNING) {
      return status;
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }

  throw std::runtime_error("Tree did not finish within 1000 ticks");
}

BT::NodeStatus run_tree(
  BT::BehaviorTreeFactory & factory,
  const std::string & xml,
  const BT::Blackboard::Ptr & blackboard)
{
  auto tree = factory.createTreeFromText(xml, blackboard);
  return tick_to_completion(tree);
}

template<typename T>
T blackboard_value(
  const BT::Blackboard::Ptr & blackboard,
  const std::string & key)
{
  T value{};

  if (!blackboard->get(key, value)) {
    throw std::runtime_error(
      "Blackboard key was not written: " + key);
  }

  return value;
}

void test_skip_if(BT::BehaviorTreeFactory & factory)
{
  const auto blackboard = BT::Blackboard::create();
  blackboard->set("condition", true);

  const char * xml = R"(
    <root BTCPP_format="4" main_tree_to_execute="Test">
      <BehaviorTree ID="Test">
        <AlwaysFailure _skipIf="condition"/>
      </BehaviorTree>
    </root>
  )";

  require(
    run_tree(factory, xml, blackboard) == BT::NodeStatus::SKIPPED,
    "_skipIf=true must return SKIPPED");
}

void test_failure_if(BT::BehaviorTreeFactory & factory)
{
  const auto blackboard = BT::Blackboard::create();
  blackboard->set("condition", true);

  const char * xml = R"(
    <root BTCPP_format="4" main_tree_to_execute="Test">
      <BehaviorTree ID="Test">
        <AlwaysSuccess _failureIf="condition"/>
      </BehaviorTree>
    </root>
  )";

  require(
    run_tree(factory, xml, blackboard) == BT::NodeStatus::FAILURE,
    "_failureIf=true must return FAILURE");
}

void test_success_if(BT::BehaviorTreeFactory & factory)
{
  const auto blackboard = BT::Blackboard::create();
  blackboard->set("condition", true);

  const char * xml = R"(
    <root BTCPP_format="4" main_tree_to_execute="Test">
      <BehaviorTree ID="Test">
        <AlwaysFailure _successIf="condition"/>
      </BehaviorTree>
    </root>
  )";

  require(
    run_tree(factory, xml, blackboard) == BT::NodeStatus::SUCCESS,
    "_successIf=true must return SUCCESS");
}

void test_while(BT::BehaviorTreeFactory & factory)
{
  const auto blackboard = BT::Blackboard::create();
  blackboard->set("continue_running", false);

  const char * xml = R"(
    <root BTCPP_format="4" main_tree_to_execute="Test">
      <BehaviorTree ID="Test">
        <AlwaysSuccess _while="continue_running"/>
      </BehaviorTree>
    </root>
  )";

  require(
    run_tree(factory, xml, blackboard) == BT::NodeStatus::SKIPPED,
    "_while=false before execution must return SKIPPED");
}

void test_on_success(BT::BehaviorTreeFactory & factory)
{
  const auto blackboard = BT::Blackboard::create();
  blackboard->set("hook", false);

  const char * xml = R"(
    <root BTCPP_format="4" main_tree_to_execute="Test">
      <BehaviorTree ID="Test">
        <AlwaysSuccess _onSuccess="hook = true"/>
      </BehaviorTree>
    </root>
  )";

  require(
    run_tree(factory, xml, blackboard) == BT::NodeStatus::SUCCESS,
    "AlwaysSuccess must return SUCCESS");

  require(
    blackboard_value<bool>(blackboard, "hook"),
    "_onSuccess did not update the blackboard");
}

void test_on_failure(BT::BehaviorTreeFactory & factory)
{
  const auto blackboard = BT::Blackboard::create();
  blackboard->set("hook", false);

  const char * xml = R"(
    <root BTCPP_format="4" main_tree_to_execute="Test">
      <BehaviorTree ID="Test">
        <AlwaysFailure _onFailure="hook = true"/>
      </BehaviorTree>
    </root>
  )";

  require(
    run_tree(factory, xml, blackboard) == BT::NodeStatus::FAILURE,
    "AlwaysFailure must return FAILURE");

  require(
    blackboard_value<bool>(blackboard, "hook"),
    "_onFailure did not update the blackboard");
}

void test_post(BT::BehaviorTreeFactory & factory)
{
  const auto blackboard = BT::Blackboard::create();
  blackboard->set("hook", false);

  const char * xml = R"(
    <root BTCPP_format="4" main_tree_to_execute="Test">
      <BehaviorTree ID="Test">
        <AlwaysSuccess _post="hook = true"/>
      </BehaviorTree>
    </root>
  )";

  require(
    run_tree(factory, xml, blackboard) == BT::NodeStatus::SUCCESS,
    "Postcondition test must return SUCCESS");

  require(
    blackboard_value<bool>(blackboard, "hook"),
    "_post did not update the blackboard");
}

void test_on_halted(BT::BehaviorTreeFactory & factory)
{
  const auto blackboard = BT::Blackboard::create();
  blackboard->set("hook", false);

  const char * xml = R"(
    <root BTCPP_format="4" main_tree_to_execute="Test">
      <BehaviorTree ID="Test">
        <Sleep msec="5000" _onHalted="hook = true"/>
      </BehaviorTree>
    </root>
  )";

  auto tree = factory.createTreeFromText(xml, blackboard);

  const auto first_status = tree.tickOnce();

  require(
    first_status == BT::NodeStatus::RUNNING,
    "Sleep must be RUNNING before haltTree()");

  tree.haltTree();

  require(
    blackboard_value<bool>(blackboard, "hook"),
    "_onHalted did not update the blackboard");
}

}  // namespace

int main()
{
  try {
    BT::BehaviorTreeFactory factory;

    test_skip_if(factory);
    test_failure_if(factory);
    test_success_if(factory);
    test_while(factory);
    test_on_success(factory);
    test_on_failure(factory);
    test_post(factory);
    test_on_halted(factory);

    std::cout
      << "[PASS] All 8 BehaviorTree.CPP pre/post conditions passed:"
      << std::endl
      << "       _skipIf _failureIf _successIf _while"
      << std::endl
      << "       _onSuccess _onFailure _post _onHalted"
      << std::endl;

    return 0;
  } catch (const std::exception & exception) {
    std::cerr
      << "[FAIL] Pre/post-condition test: "
      << exception.what()
      << std::endl;
    return 1;
  }
}
