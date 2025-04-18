ATTACK_GATEWAY_REGISTRY = {}


def register_attack_gateway(name):
    """
    Decorator to register a attack gateway class.
    """

    def decorator(attack_gateway_cls):
        ATTACK_GATEWAY_REGISTRY[name] = attack_gateway_cls
        return attack_gateway_cls

    return decorator
