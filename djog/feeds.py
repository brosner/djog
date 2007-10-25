
from django.core import urlresolvers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.encoding import smart_str
from django.contrib.syndication.feeds import Feed
from django.contrib.comments.models import FreeComment

from djog import site
from djog.models import Entry, Tag

class EntryFeed(Feed):
    def title(self):
        return "%s: Latest Entries" % site.get_blog().title

    def link(self):
        return site.get_blog().get_absolute_url()
    
    def description(self):
        return "The latest entries on %s" % site.get_blog().title
    
    def items(self):
        return Entry.objects.order_by('-pub_date')[:10]

class CommentsByEntryFeed(Feed):
    def get_object(self, bits):
        if len(bits) != 4:
            raise ObjectDoesNotExist
        return Entry.objects.get(slug__exact=bits[3])
    
    def title(self, obj):
        return "%s: Comments on \"%s\"" % (site.get_blog().title, obj.title)
    
    def link(self, obj):
        return "%s#comments" % obj.get_absolute_url()
    
    def description(self, obj):
        return "The latest comments on \"%s\"" % obj.title
    
    def items(self, obj):
        return FreeComment.objects.filter(content_type__model='entry').filter(object_id=obj.pk).order_by('-submit_date')[:10]

class EntriesByTagFeed(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Tag.objects.get(slug__exact=bits[0])
    
    def title(self, obj):
        return "%s: Entries Tagged with \"%s\"" % (site.get_blog().title, obj.tag)
    
    def link(self, obj):
        return "%s" % obj.get_absolute_url()
    
    def description(self, obj):
        return "The latest stories tagged with \"%s\"" % obj.tag
    
    def items(self, obj):
        return Entry.objects.filter(tags__tag=obj.tag)[:10]

class SearchFeed(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return smart_str(bits[0])
    
    def title(self, obj):
        return "%s: Search Results for \"%s\"" % (site.get_blog().title, obj)
    
    def link(self, obj):
        return "%s?s=%s" % (urlresolvers.reverse('djog_search'), obj)
    
    def description(self, obj):
        return "Search results for \"%s\"" % obj
    
    def items(self, obj):
        return Entry.objects.filter(Q(title__icontains=obj) | Q(text__icontains=obj))

    