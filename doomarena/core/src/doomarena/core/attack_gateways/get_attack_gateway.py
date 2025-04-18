from .register_attack_gateway import ATTACK_GATEWAY_REGISTRY


def get_attack_gateway(name, **kwargs):
    """
    Retrieve a attack gateway instance based on the provided name.
    """
    if name not in ATTACK_GATEWAY_REGISTRY:
        raise ValueError(f"Attack Gateway '{name}' is not registered.")

    attack_gateway_cls = ATTACK_GATEWAY_REGISTRY[name]
    return attack_gateway_cls(**kwargs)
