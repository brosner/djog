
from django.conf.urls.defaults import *

from dlog.models import Entry, Tag
from dlog.feeds import *
from dlog.views import *

blog_dict = {
    'queryset': Entry.objects.all(),
    'date_field': 'pub_date',
}

date_dict = dict(blog_dict, template_name='blog/entry_date.html')

feeds = {
    'latest': LatestEntries,
    'comments': LatestCommentsByEntry,
    'tags': LatestEntriesByTag,
    'search': EntriesBySearch,
}

urlpatterns = patterns('',
    (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$', 'django.views.generic.date_based.object_detail', dict(blog_dict, slug_field='slug')),
    (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', 'django.views.generic.date_based.archive_day', date_dict),
    (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'django.views.generic.date_based.archive_month', date_dict),
    (r'^(?P<year>\d{4})/$', 'django.views.generic.date_based.archive_year', date_dict),
    (r'^$', 'django.views.generic.date_based.archive_index', blog_dict),
    (r'^tags/(?P<slug>[-\w]+)/$', 'dlog.views.EntriesByTag'),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^search/$', 'dlog.views.Search'),
    (r'^trackback/(?P<id>\d+)/$', 'dlog.views.trackback'),
    (r'^comments/postfree/', 'dlog.views.post_free_comment_redirect'),
    (r'^comments/', include('django.contrib.comments.urls.comments')),
)