
from django import template
from dlog.models import *

register = template.Library()

@register.inclusion_tag('tags.html')
def show_tags():
	tags = Tag.objects.all().order_by('tag')
	return {'tags': tags}

@register.inclusion_tag('monthly.html')
def show_archive():
	months = Entry.objects.dates('pub_date', "month")
	counts = []
	for month in months:
		count = Entry.objects.filter(pub_date__month=month.month).count()
		counts.append((month, count))
	return {'counts': counts}
