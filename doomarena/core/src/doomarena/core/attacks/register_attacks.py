ATTACK_REGISTRY = {}


def register_attacks(name):
    """
    Decorator to register a attack class.
    """

    def decorator(attack_cls):
        ATTACK_REGISTRY[name] = attack_cls
        return attack_cls

    return decorator
