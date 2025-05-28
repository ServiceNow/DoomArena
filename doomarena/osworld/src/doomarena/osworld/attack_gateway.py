from doomarena.core.attack_gateways.register_attack_gateway import (
    register_attack_gateway,
)
from PIL import Image
from io import BytesIO
from doomarena.osworld.popup_inpainting_attack import (
    find_largest_non_overlapping_box,
    extract_bounding_boxes_from_image,
    agent_attack,
    is_single_color_image,
)
import sys

sys.path.append("../OSWorld")
from desktop_env.desktop_env import DesktopEnv


@register_attack_gateway("osworld_attack_gateway")
class OSWorldAttackGateway(DesktopEnv):
    def __init__(self, **kwargs):
        super().__init__(
            path_to_vm=kwargs["path_to_vm"],
            action_space=kwargs["action_space"],
            screen_size=kwargs["screen_size"],
            headless=kwargs["headless"],
            os_type=kwargs["os_type"],
            require_a11y_tree=kwargs["require_a11y_tree"],
        )
        self.attack_configs = kwargs["attack_configs"]
        self.whole_attack_bounding_box = None
        self.x_tgt = None
        self.y_tgt = None
        self.attack_string = None
        self.is_attack_executed = False
        self.env_state = []
        self.attack_success_ = 0

    def reset(self, **kwargs):
        # Reset OS World environment
        self.whole_attack_bounding_box = None
        self.x_tgt = None
        self.y_tgt = None
        self.is_attack_executed = False
        self.env_state = []
        self.attack_success_ = 0
        return super().reset(**kwargs)

    def execute_inpainting_attack(self, observation, injection_str):
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
                ) = agent_attack(
                    injection_str=injection_str,
                    current_observation=current_observation,
                    largest_non_overlapping_box=largest_non_overlapping_box,
                )

                self.whole_attack_bounding_box = whole_attack_bounding_box
                self.x_tgt = x_tgt
                self.y_tgt = y_tgt
                self.attack_string = attack_string

                if isinstance(current_observation, bytes):
                    current_observation = Image.open(
                        BytesIO(current_observation)
                    ).convert("RGB")
                image_bytes_io = BytesIO()
                current_observation.save(image_bytes_io, format="PNG")
                current_observation.save("output.png", format="PNG")
                current_observation = image_bytes_io.getvalue()
                observation["screenshot"] = current_observation
                self.is_attack_executed = True
            else:
                self.is_attack_executed = False
                print(
                    "Attack analysis 0: Skip attack this round! The OS might be sleeping..."
                )
        else:
            self.is_attack_executed = False
        return observation

    def step(self, action, pause=2):
        if self.is_attack_executed:
            self.env_state.append(
                {
                    "whole_attack_bounding_box": self.whole_attack_bounding_box,
                    "x_tgt": self.x_tgt,
                    "y_tgt": self.y_tgt,
                    "action": action,
                }
            )
        observation, reward, done, info = super().step(action, pause)
        for attack_config in self.attack_configs:
            if attack_config.attackable_component.get("type") == "popup_inpainting":
                injection_str = self.attack_config.attack.get_next_attack()
                malicious_observation = self.execute_inpainting_attack(
                    observation, injection_str
                )
                return malicious_observation, reward, done, info
            else:
                self.is_attack_executed = False

        return observation, reward, done, info

    def attack_success(self) -> bool:
        """
        Determines the success of an attack based on provided configurations and metrics.

        Returns:
            bool: True if the sum of the attack success scores is greater than 0,
                  indicating at least one successful attack configuration. False otherwise.
        """
        for idx, config in enumerate(self.attack_configs):
            self.attack_success_ = config.success_filter(self)
