
from django.dispatch import dispatcher
from django.db.models import signals
from django.contrib.sites.models import Site

from djog.models import Blog
from djog import models as blog_app


def create_default_blog(app, created_models, verbosity):
    if Blog in created_models and Site in created_models:
        if verbosity >= 2:
            print 'Creating default Blog object'
        # assign the blog to the current site
        s = Site.objects.get_current()
        b = Blog(site=s, title='Default Blog')
        b.save()

dispatcher.connect(create_default_blog, sender = blog_app,
                                        signal = signals.post_syncdb)
