
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
from django.contrib.syndication.feeds import Feed
from django.contrib.comments.models import FreeComment

from djog.models import Entry, Tag

class LatestEntries(Feed):
    title = "Alex's Blog: Latest Entries"
    link = "/blog/latest/"
    description = "The latest entries on Alex's Blog"
    
    def items(self):
        return Entry.objects.order_by('-pub_date')[:10]

class LatestCommentsByEntry(Feed):
    def get_object(self, bits):
        if len(bits) != 4:
            raise ObjectDoesNotExist
        return Entry.objects.get(slug__exact=bits[3])
    
    def title(self, obj):
        return "Alex's Blog: Comments on \"%s\"" % obj.title
    
    def link(self, obj):
        return "%s#comments" % obj.get_absolute_url
    
    def description(self, obj):
        return "The latest comments on \"%s\"" % obj.title
    
    def items(self, obj):
        return FreeComment.objects.filter(content_type='14').filter(object_id=obj.pk).order_by('-submit_date')[:10]

class LatestEntriesByTag(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Tag.objects.get(slug__exact=bits[0])
    
    def title(self, obj):
        return "Alex's Blog: Entries Tagged with \"%s\"" % obj.tag
    
    def link(self, obj):
        return "%s" % obj.get_absolute_url
    
    def description(self, obj):
        return "The latest stories tagged with \"%s\"" % obj.tag
    
    def items(self, obj):
        return Entry.objects.filter(tags__tag=obj.tag)[:10]

class EntriesBySearch(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return smart_str(bits[0])
    
    def title(self, obj):
        return "Alex's Blog: Search Results for \"%s\"" % obj
    
    def link(self, obj):
        return "/blog/search/?s=%s" % obj
    
    def description(self, obj):
        return "Search results for \"%s\"" % obj
    
    def items(self, obj):
        return Entry.objects.filter(Q(title__icontains=obj) | Q(text__icontains=obj))

    