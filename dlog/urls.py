
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

#
# date based urls using django's generic views
#
urlpatterns = patterns('django.views.generic.date_based',
	(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$',
		'object_detail', dict(blog_dict, slug_field='slug')),
    (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$', 'archive_day', date_dict),
    (r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'archive_month', date_dict),
    (r'^(?P<year>\d{4})/$', 'archive_year', date_dict),
    (r'^$', 'archive_index', blog_dict),
)

urlpatterns += patterns('',
    (r'^tags/(?P<slug>[-\w]+)/$', 'dlog.views.EntriesByTag'),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^search/$', 'dlog.views.Search'),
    (r'^trackback/(?P<id>\d+)/$', 'dlog.views.trackback'),
    (r'^comments/postfree/', 'dlog.views.post_free_comment_redirect'),
    (r'^comments/', include('django.contrib.comments.urls.comments')),
)