
import datetime, httplib, urllib, urlparse, re

from django.core import urlresolvers
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from djog.managers import EntryManager

class Blog(models.Model):
    site = models.ForeignKey(Site)
    title = models.CharField(_("title"), max_length=100)
    
    objects = models.Manager()
    on_site = CurrentSiteManager()
    
    class Meta:
        verbose_name = _("blog")
        verbose_name_plural = _("blogs")
    
    class Admin:
        pass
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return urlresolvers.reverse('djog_index')

class Entry(models.Model):
    TYPE_POST = 0
    TYPE_PAGE = 1
    
    ENTRY_TYPES = (
        (TYPE_POST, _("Post")),
        (TYPE_PAGE, _("Page")),
    )

    blog = models.ForeignKey(Blog, verbose_name=_("blog"))
    title = models.CharField(_("title"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), prepopulate_from=("title",), max_length=100, unique=True)
    text = models.TextField(_("text"))
    author = models.ForeignKey(User, verbose_name=_("author"))
    tags = models.ManyToManyField("Tag", verbose_name=_("tag"), filter_interface=models.HORIZONTAL)
    pub_date = models.DateTimeField(_("publish date"), default=datetime.datetime.now)
    entry_type = models.IntegerField(_("entry type"), choices=ENTRY_TYPES,
        help_text=_("Select what type of entry this is, currently there are regular blog posts, and pages (ex. about or contact page)."),
        radio_admin=True, default=TYPE_POST)
    
    objects = EntryManager()
    
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("entry")
        verbose_name_plural = _("entries")
        ordering = ("-pub_date",)
        get_latest_by = "pub_date"
        unique_together = (("slug", "entry_type"),)

    class Admin:
        list_display = ("id", "title", "pub_date",)
        list_display_links = ("id", "title",)
        list_filter = ("entry_type",)
        search_fields = ("title", "text",)
        date_hierarchy = "pub_date"

    def get_absolute_url(self):
        if self.entry_type == self.TYPE_POST:
            return urlresolvers.reverse('djog_post', 
                kwargs={'year': self.pub_date.strftime("%Y"),
                        'month': self.pub_date.strftime("%b").lower(),
                        'day': self.pub_date.strftime("%d"),
                        'slug': self.slug})
        elif self.entry_type == self.TYPE_PAGE:
            return urlresolvers.reverse('djog_page',
                kwargs={'slug': self.slug})
    
    def get_rss_url(self):
        return urlresolvers.reverse('djog_feed', kwargs=dict(
            url = 'comments/%s/%s' % (
                self.pub_date.strftime("%Y/%b/%d").lower(), self.slug
            )
        ))
    
    def get_trackback_url(self):
        return urlresolvers.reverse('djog_trackback', kwargs=dict(id=self.pk))

class Tag(models.Model):
    blog = models.ForeignKey(Blog, verbose_name=_("blog"))
    tag = models.CharField(_("tag"), max_length=50, unique=True, core=True)
    slug = models.SlugField(_("slug"), prepopulate_from=("tag",), max_length=50, unique=True)

    def __unicode__(self):
        return self.tag
    
    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        
    class Admin:
        pass

    def _get_num_stories(self):
        if not hasattr(self, "_num_stories"):
            self._num_stories = Entry.objects.filter(
                tags__tag=unicode(self)
            ).count()
        return self._num_stories
    num_stories = property(_get_num_stories)

    def get_absolute_url(self):
        return urlresolvers.reverse('djog_entries_by_tag',
            kwargs={'slug': self.slug})
    
    def get_rss_url(self):
        return urlresolvers.reverse('djog_feed', kwargs=dict(
            url = 'tags/%s' % self.slug
        ))

class TrackBack(models.Model):
    entry = models.ForeignKey(Entry, verbose_name=_("entry"), edit_inline=models.STACKED, num_in_admin=1)
    url = models.URLField(_("URL"), max_length=255, core=True)
    tbURL = models.URLField(_("trackback URL"), max_length=255, null=True, blank=True, editable=False)
    status = models.BooleanField(_("status"), null=True, blank=True, editable=False)
    error = models.CharField(_("error"), max_length=255, null=True, blank=True, editable=False)
    
    def __unicode__(self):
        return self.url
    
    class Meta:
        verbose_name = _("trackback")
        verbose_name_plural = _("trackbacks")
        
    class Admin:
        pass
    
    def _connect_to_url(self, url):
        # ensure the url starts with http since the connection wont work
        if not url.startswith('http'):
            url = 'http://' + url
        url_bits = urlparse.urlparse(url)
        if url_bits[0] == 'https':
            conn = httplib.HTTPSConnection(url_bits[1])
        else:
            conn = httplib.HTTPConnection(url_bits[1])
        return conn, url_bits[2]
    
    def autodiscover(self):
        conn, path = self._connect_to_url(self.url)
        conn.request('GET', path)
        response = conn.getresponse()
        tb_regex = re.search(r'trackback:ping="(.*?)"', response.read())
        if tb_regex:
            self.tbURL = tb_regex.group(1)
    
    def ping(self):
        params = urllib.urlencode({
            'title': self.entry.title,
            'url': '%s/%s' % (
                Site.objects.get_current(),
                self.entry.get_absolute_url()
            ),
            'excerpt': self.entry.text,
            'blog_name': unicode(self.entry.blog),
        })
        conn, path = self._connect_to_url(str(self.tbURL))
        conn.request("POST", path, params, ({
            "Content-type": "application/x-www-form-urlencoded",
            "User-Agent": "Python"
        }))
        response = conn.getresponse()
        data = response.read()
        error_regex = re.search(r'<error>(.*?)</error>', data)
        if error_regex:
            tb_error_code = error_regex.group(1)
            if int(tb_error_code) == 0:
                self.status = True
            else:
                msg_regex = re.search(r'<message>(.*?)</message', data)
                if msg_regex:
                    self.error = msg_regex.group(1)
        conn.close()
    
    def save(self, **kwargs):
        self.autodiscover()
        self.ping()
        super(TrackBack, self).save(**kwargs)

class IncomingTrackBack(models.Model):
    title = models.CharField(_("title"), max_length=255, null=True, blank=True, editable=False)
    excerpt = models.CharField(_("excerpt"), max_length=255, null=True, blank=True, editable=False)
    url = models.URLField(_("URL"), max_length=255, editable=False)
    blog = models.CharField(_("blog"), max_length=255, null=True, blank=True, editable=False)
    entry = models.ForeignKey(Entry, verbose_name=_("entry"))
    time = models.DateTimeField(_("time"), default=datetime.datetime.now)
    
    def __unicode__(self):
        return "%s: %s" % (self.blog, self.title)
    
    class Meta:
        verbose_name = _("incoming trackback")
        verbose_name_plural = _("incoming trackbacks")
    
    class Admin:
        pass

class Configuration(models.Model):
    blog = models.ForeignKey(Blog, verbose_name=_("blog"))
    option = models.CharField(_("option"), max_length=255)
    value = models.CharField(_("option"), max_length=255)
    
    def __unicode__(self):
        return "%s: %s" % (self.option, self.value)
    