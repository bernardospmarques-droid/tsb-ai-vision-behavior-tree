# Valgrind Results

Command executed:

valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./ros2_ws/build/tsb_bt_core/bt_executor

Summary:

- definitely lost: 0 bytes
- indirectly lost: 0 bytes
- possibly lost: 279474 bytes
- still reachable: 5092614 bytes

The remaining allocations are associated with ROS 2 Jazzy runtime libraries (FastDDS, rmw_fastrtps, rclcpp, lttng-ust) and do not indicate application-level memory leaks.

Conclusion:

No definite memory leaks were detected in the project code.
