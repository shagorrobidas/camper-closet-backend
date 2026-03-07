from .models import SiteConfiguration


def site_config(request):
    """
    Context processor to pass SiteConfiguration to all templates globally.
    """
    try:
        config = SiteConfiguration.load()
    except Exception:
        config = None
    return {'site_config': config}
