# -*- coding: utf-8 -*-


class UnknownServiceEnvironmentNotConfiguredError(Exception):
    """
    Raised when unknown service-environment is not configured for plugin.
    """
    pass


class ServiceEnvironmentDoesNotExistError(Exception):
    """
    Raise this exception when service does not exist
    """
    pass
