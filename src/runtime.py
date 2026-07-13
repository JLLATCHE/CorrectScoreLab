"""
Runtime de métodos CorrectScoreLab
"""

ENABLED_METHODS = {}


def register(method_name):

    ENABLED_METHODS[method_name] = True


def enable(method_name):

    ENABLED_METHODS[method_name] = True


def disable(method_name):

    ENABLED_METHODS[method_name] = False


def is_enabled(method_name):

    return ENABLED_METHODS.get(method_name, True)


def enable_all():

    for method in ENABLED_METHODS:

        ENABLED_METHODS[method] = True


def disable_all():

    for method in ENABLED_METHODS:

        ENABLED_METHODS[method] = False


def active_methods():

    return [

        method

        for method, enabled in ENABLED_METHODS.items()

        if enabled

    ]