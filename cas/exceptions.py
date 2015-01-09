from django.core.exceptions import ValidationError


class CasTicketException(ValidationError):
    """
    The ticket fails to validate
    """

    pass


class CasConfigException(ValidationError):
    """
    The config is wrong
    """

    pass
