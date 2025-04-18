from .register_attacks import ATTACK_REGISTRY


def get_attacks(name, **kwargs):
    """
    Retrieve a attacks instance based on the provided name.
    """
    if name not in ATTACK_REGISTRY:
        raise ValueError(f"Attack '{name}' is not registered.")

    attacks_cls = ATTACK_REGISTRY[name]
    return attacks_cls(**kwargs)
