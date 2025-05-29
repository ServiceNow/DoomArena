from doomarena.core.attack_gateways.register_attack_gateway import (
    register_attack_gateway,
)
from PIL import Image
from io import BytesIO
from doomarena.osworld.popup_inpainting_attack import (
    find_largest_non_overlapping_box,
    extract_bounding_boxes_from_image,
    inject_popup_inpainting_attack,
    is_single_color_image,
)
import sys

from desktop_env.desktop_env import DesktopEnv


@register_attack_gateway("osworld_attack_gateway")
class OSWorldAttackGateway(DesktopEnv):
    def __init__(self, **kwargs):
        self.attack_configs = kwargs.pop("attack_configs")

        assert (
            len(self.attack_configs) <= 1
        ), "At most one attack configuration is allowed for OSWorldAttackGateway."

        super().__init__(
            **kwargs,
        )

        self.inpainting_steps = []
        self.is_inpainting_attack_executed = False

    def reset(self, **kwargs):
        # Reset OS World environment
        self.whole_attack_bounding_box = None

        self.inpainting_steps = []
        self.is_inpainting_attack_executed = False

        return super().reset(**kwargs)

    def execute_inpainting_attack(self, observation, injection_str, action: str):
        if "screenshot" in observation:
            current_observation = observation["screenshot"]
            if not is_single_color_image(current_observation):
                OCR_boxes = extract_bounding_boxes_from_image(current_observation)
                # try not to block any tags or detected texts
                current_boundingbox = OCR_boxes[1:]

                largest_non_overlapping_box = find_largest_non_overlapping_box(
                    (1920, 956), current_boundingbox
                )

                (
                    current_observation,
                    whole_attack_bounding_box,
                    x_tgt,
                    y_tgt,
                    attack_string,
                ) = inject_popup_inpainting_attack(
                    injection_str=injection_str,
                    current_observation=current_observation,
                    largest_non_overlapping_box=largest_non_overlapping_box,
                )

                # Save the target coordinates, attack bounding box, and attack string
                self.inpainting_steps.append(
                    {
                        "whole_attack_bounding_box": whole_attack_bounding_box,
                        "x_tgt": x_tgt,
                        "y_tgt": y_tgt,
                        "attack_string": attack_string,
                        "action": action,
                    }
                )
                # Patch the attack back
                observation["screenshot"] = current_observation
                self.is_inpainting_attack_executed = True
            else:
                self.is_inpainting_attack_executed = False
                print(
                    "Attack analysis 0: Skip attack this round! The OS might be sleeping..."
                )
        else:
            self.is_inpainting_attack_executed = False
        return observation

    def step(self, action, pause=2):

        observation, reward, done, info = super().step(action, pause)
        for attack_config in self.attack_configs:
            if attack_config.attackable_component.get("type") == "popup_inpainting":
                injection_str = attack_config.attack.get_next_attack()
                malicious_observation = self.execute_inpainting_attack(
                    observation, injection_str, action,  # the action is passed for evaluation purposes
                )
                return malicious_observation, reward, done, info
            else:
                self.is_inpainting_attack_executed = False

        return observation, reward, done, info

    def attack_success(self) -> float:
        """
        Determines the success of an attack based on provided configurations and metrics.

        Returns:
            bool: True if the sum of the attack success scores is greater than 0,
                  indicating at least one successful attack configuration. False otherwise.
        """
        attack_success = False
        assert len(self.attack_configs) <= 1, "At most one attack configuration is allowed for OSWorldAttackGateway."
        for idx, config in enumerate(self.attack_configs):
            attack_success = config.success_filter(self)
        return attack_success
