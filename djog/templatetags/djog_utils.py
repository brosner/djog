
from django import template
from djog.models import *

register = template.Library()

def show_entry(entry):
    return dict(entry=entry)
register.inclusion_tag("entry.html")(show_entry)


def show_tags():
    tags = Tag.objects.all().order_by("tag")
    return {"tags": [tag for tag in tags if tag.num_stories > 0]}
register.inclusion_tag("tags.html")(show_tags)


def show_archive():
    entries = Entry.objects.of_type(Entry.TYPE_POST)
    dates = []
    for date in entries._clone().dates("pub_date", "month"):
        dates.append(
            (date, (entries & Entry.objects.in_month(date.month)).count())
        )
    # TODO: rename counts to dates. counts is not very descriptive.
    return {"counts": dates}
register.inclusion_tag("monthly.html")(show_archive)


def show_pages():
    pages = Entry.objects.of_type(Entry.TYPE_PAGE)
    return {"pages": pages}
register.inclusion_tag("pages.html")(show_pages)


def searchify(term):
    return "search/%s" % term
register.filter("searchify", searchify)
