# ROS 2 bag playback validation

- Validation date: 2026-11-13T17:19:45+00:00
- Bag: integrated_20261113_170856
- Storage format: MCAP
- ROS distribution: Jazzy
- Recorded duration: 192.717422863 seconds
- Total recorded messages: 15114
- Playback completed: YES
- Turtlesim movement observed during playback: YES
- Playback method: standalone turtlesim_node and ros2 bag play
- Replayed movement topic: /turtle1/cmd_vel

## Recorded topic counts

- /rosout: 175
- /turtle1/cmd_vel: 3286
- /turtle1/pose: 11637
- /vision/canvas_png: 4
- /vision/command: 8
- /vision/image: 4

## Result

The rosbag was successfully reproduced against a standalone Turtlesim node. Visible turtle movement confirmed that the recorded velocity commands were republished and consumed correctly.
