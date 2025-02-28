import numpy as np
import time

class HumanoidRobot:
    def __init__(self, joint_angles):
        """
        Initialize the humanoid robot with initial joint angles.

        :param joint_angles: A dictionary with joint names as keys and initial angles as values.
        """
        self.joint_angles = joint_angles
        self.update_interval = 0.1  # Time interval to update joint angles

    def set_joint_angle(self, joint_name, angle):
        """
        Set the angle of a specific joint.

        :param joint_name: The name of the joint to set.
        :param angle: The angle to set the joint to.
        """
        if joint_name in self.joint_angles:
            self.joint_angles[joint_name] = angle
        else:
            print(f"Joint {joint_name} does not exist.")

    def walk_forward(self, steps):
        """
        Simulate walking forward by updating joint angles.

        :param steps: Number of steps to walk.
        """
        for _ in range(steps):
            # Example joint angle updates for walking
            self.set_joint_angle('left_hip', 30)
            self.set_joint_angle('right_hip', -30)
            time.sleep(self.update_interval)

            self.set_joint_angle('left_hip', -30)
            self.set_joint_angle('right_hip', 30)
            time.sleep(self.update_interval)

    def display_joint_angles(self):
        """
        Display the current joint angles of the robot.
        """
        print("Current Joint Angles:")
        for joint, angle in self.joint_angles.items():
            print(f"{joint}: {angle} degrees")

# Example usage
initial_joint_angles = {
    'left_hip': 0,
    'right_hip': 0,
    'left_knee': 0,
    'right_knee': 0,
    'left_ankle': 0,
    'right_ankle': 0
}

robot = HumanoidRobot(initial_joint_angles)
robot.walk_forward(5)
robot.display_joint_angles()
