ATTACK_CONFIG_REGISTRY = {}


def register_attack_config(name):
    """
    Decorator to register an attack config class.
    """

    def decorator(attack_config_cls):
        ATTACK_CONFIG_REGISTRY[name] = attack_config_cls
        return attack_config_cls

    return decorator
