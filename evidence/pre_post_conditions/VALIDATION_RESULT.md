# Pre/Post Conditions Validation

- Validation date: 2026-11-13T17:21:52+00:00
- Behavior tree: tree_prepost_demo.xml
- ROS distribution: Jazzy
- Input command: SQUARE
- Groot2 monitoring port: 1668
- Run-once mode: enabled

## Conditions demonstrated

- Blackboard initialization through a Script node
- _onSuccess after successful command acquisition
- _onFailure for command acquisition failure handling
- _while during behavior selection and execution
- _onSuccess after successful behavior execution
- _onFailure for behavior execution failure handling

## Execution result

- Command written to blackboard: SQUARE
- Linear movements completed: 4
- Angular movements completed: 4
- Linear speed: 2.00
- Angular speed: 1.50
- Linear movement duration: 1.50 seconds per side
- Angular movement duration: 1.05 seconds per turn
- Final tree status: SUCCESS
- Executor stopped after completion: YES

The separate demonstration tree executed the SQUARE behavior successfully while applying BehaviorTree.CPP Pre/Post Condition scripts. The production tree remained unchanged.
