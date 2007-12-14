
from django import template
from djog.models import *

register = template.Library()

def show_tags():
    tags = Tag.objects.all().order_by('tag')
    return {'tags': tags}
register.inclusion_tag('tags.html')(show_tags)

def show_archive():
    months = Entry.objects.filter(entry_type=Entry.TYPE_POST).dates('pub_date', "month")
    counts = []
    for month in months:
        count = Entry.objects.filter(entry_type=Entry.TYPE_POST, pub_date__month=month.month).count()
        counts.append((month, count))
    return {'counts': counts}
register.inclusion_tag('monthly.html')(show_archive)

def show_pages():
    Pages = Entry.objects.filter(entry_type=Entry.TYPE_PAGE)
    return {'pages': Pages}
register.inclusion_tag('pages.html')(show_pages)

def searchify(term):
    return "search/%s" % term
register.filter('searchify', searchify)
