
from djog import site


def blog(request):
    return dict(
        site = site,
        blog = site.get_blog(),
    )
