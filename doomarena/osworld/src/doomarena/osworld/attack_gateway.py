from doomarena.core.attack_gateways.attack_gateway import AttackGateway
from doomarena.core.attack_gateways.register_attack_gateway import (
    register_attack_gateway,
)
from doomarena.core.attack_config.attack_config import AttackConfig

import sys
sys.path.append(['/Users/mihir.bansal/Library/CloudStorage/OneDrive-ServiceNow/OSWorld'])
from osworld import DesktopEnv

@register_attack_gateway("osworld_gateway")
class OSWorldAttackGateway(DesktopEnv):
    def __init__(
        self, env, user, attack_configs: List[AttackConfig], task_name: str = None
    ):
    
    def reset(self, **kwargs):
        return super().reset(**kwargs) # Reset OS World environment
    
    def step(self, action):
        if self.attack_config.attackable_component.get("type") == "popup_inpainting":
            return super().step(action) # Execute action in OSWorld