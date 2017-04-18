from maintenance_mode.core import get_maintenance_mode


def maintenance_mode_context_processor(request):
    """
    This function passes maintenance mode status to each view rendered with a RequestContext. It's used as context
    processor.
    https://docs.djangoproject.com/en/1.9/ref/templates/api/#writing-your-own-context-processors
    https://docs.djangoproject.com/en/1.9/ref/templates/api/#django.template.RequestContext
    :param request:
    :return: maintenance mode status
    """
    return {'maintenance_mode': get_maintenance_mode()}
