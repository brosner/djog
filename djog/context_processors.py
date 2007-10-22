
from djog import site

def settings(request):
    return dict(
        site = site,
        blog = site.get_blog(),
    )
