from .register_attack_config import ATTACK_CONFIG_REGISTRY


def get_attack_config(name, **kwargs):
    """
    Retrieve an attack config instance based on the provided name.
    """
    if name not in ATTACK_CONFIG_REGISTRY:
        raise ValueError(f"Attack Config '{name}' is not registered.")

    attack_config_cls = ATTACK_CONFIG_REGISTRY[name]
    return attack_config_cls(**kwargs)
