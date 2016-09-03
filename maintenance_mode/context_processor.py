from maintenance_mode.core import get_maintenance_mode


def maintenance_mode_context_processor(request):
    """
    This function passes maintenance mode status to each view rendered with a RequestContext.
    :param request:
    :return:
    """
    return {'maintenance_mode': get_maintenance_mode()}
