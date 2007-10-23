
from django.core import urlresolvers
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic.date_based import *
from django.shortcuts import render_to_response
from django.utils.encoding import smart_str
from django.contrib.syndication.views import feed

from djog.feeds import *
from djog.models import Blog

class DjogSite(object):
    
    def __init__(self):
        self.feeds = {
            'latest': LatestEntries,
            'comments': LatestCommentsByEntry,
            'tags': LatestEntriesByTag,
            'search': EntriesBySearch,
        }
    
    def get_blog(self):
        # TODO: look at this a bit more and find a good way to ensure it has
        # an object.
        return Blog.on_site.all()[0]
    
    def archive_index(self, request, **kwargs):
        defaults = dict(
            queryset = self.get_blog().entry_set.all(),
            date_field = 'pub_date',
        )
        defaults.update(kwargs)
        return archive_index(request, **defaults)

    def archive_year(self, request, **kwargs):
        defaults = dict(
            queryset = self.get_blog().entry_set.all(),
            date_field = 'pub_date',
            template_name = 'djog/entry_date.html',
        )
        defaults.update(kwargs)
        return archive_year(request, **defaults)

    def archive_month(self, request, **kwargs):
        defaults = dict(
            queryset = self.get_blog().entry_set.all(),
            date_field = 'pub_date',
            template_name = 'djog/entry_date.html',
        )
        defaults.update(kwargs)
        return archive_month(request, **defaults)

    def archive_day(self, request, **kwargs):
        defaults = dict(
            queryset = self.get_blog().entry_set.all(),
            date_field = 'pub_date',
            template_name = 'djog/entry_date.html',
        )
        defaults.update(kwargs)
        return archive_day(request, **defaults)

    def entry(self, request, **kwargs):
        defaults = dict(
            queryset = self.get_blog().entry_set.all(),
            date_field = 'pub_date',
        )
        defaults.update(kwargs)
        return object_detail(request, **defaults)
    
    def entries_by_tag(self, request, slug):
        tag = Tag.objects.get(slug=slug)
        entries = Entry.objects.filter(tags__slug=slug)
        return render_to_response('djog/tag_list.html', {
            'entries': entries,
            'tag': tag,
        }, context_instance=RequestContext(request))
    
    def feed(self, request, url):
        return feed(request, url, self.feeds)
    
    def search(self, request):
        if not request.GET.has_key('s'):
            return HttpResponseRedirect(urlresolvers.reverse('djog_index'))
        search = smart_str(request.GET['s'])
        results = Entry.objects.filter(
            Q(title__icontains=search) | Q(text__icontains=search)
        )
        return render_to_response('djog/search.html', {
            'term': search,
            'results': results,
        }, context_instance=RequestContext(request))
    
    def trackback(self, request, id):
        if request.method != 'POST':
            return render_to_response('trackback.xml', {
                'error_code': 1,
                'message': "Request type must be POST"
            })
        if not request.POST.get('url'):
            return render_to_response('trackback.xml', {
                'error_code': 1,
                'message': "URL not specified"
            })
        tb = IncomingTrackBack()
        tb.entry_id = int(id)
        tb.title = request.POST.get('title')
        tb.excerpt = request.POST.get('excerpt')
        tb.url = request.POST.get('url')
        tb.blog = request.POST.get('blog_name')
        tb.save()
        return render_to_response('trackback.xml', {
            'error_code': 0
        })

site = DjogSite()
