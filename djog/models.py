
import datetime, httplib, urllib, urlparse, re

from django.core import urlresolvers
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

class Entry(models.Model):
    title = models.CharField(_('Title'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), prepopulate_from=("title",), max_length=100, unique=True)
    text = models.TextField(_('Text'))
    author = models.ForeignKey(User, verbose_name=_('Author'))
    tags = models.ManyToManyField("Tag", verbose_name=_('Tag'), filter_interface=models.HORIZONTAL)
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = _('Entries')
        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'

    class Admin:
        list_display = ('pub_date', 'title',)
        search_fields = ['title', 'text']

    def get_absolute_url(self):
        return urlresolvers.reverse('djog_entry', 
            kwargs={'year': self.pub_date.strftime("%Y"),
                    'month': self.pub_date.strftime("%b").lower(),
                    'day': self.pub_date.strftime("%d")
                    'slug': self.slug})
    
    def get_rss_url(self):
        return "/blog/feeds/comments/%s/%s/" % (self.pub_date.strftime("%Y/%b/%d").lower(), self.slug)
    
    def get_trackback_url(self):
        return urlresolvers.reverse('trackback',
            kwargs={'id': self.pk})

class Tag(models.Model):
    tag = models.CharField(_('Tag'), max_length=50, unique=True, core=True)
    slug = models.SlugField(_('Slug'), prepopulate_from=("tag",), max_length=50, unique=True)

    def __unicode__(self):
        return self.tag

    class Admin:
        pass

    def num_stories(self):
        return Entry.objects.filter(tags__tag=unicode(self)).count()

    def get_absolute_url(self):
        return urlresolvers.reverse('EntriesByTag',
            kwargs={'slug': self.slug})
    
    def get_rss_url(self):
        return "/blog/feeds/tags/%s/" % self.slug

class TrackBack(models.Model):
    entry = models.ForeignKey(Entry, verbose_name=_('Entry'), edit_inline=models.STACKED, num_in_admin=1)
    url = models.URLField(_('URL'), max_length=255, core=True)
    tbURL = models.URLField(_('Trackback URL'), max_length=255, null=True, blank=True, editable=False)
    status = models.BooleanField(_('Status'), null=True, blank=True, editable=False)
    error = models.CharField(_('Error'), max_length=255, null=True, blank=True, editable=False)
    
    def __unicode__(self):
        return self.url
    
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
            # TODO: make this configurable (i dont care about alex's blog hehe)
            'blog_name': "Alex's Blog"
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
    
    def save(self):
        self.autodiscover()
        self.ping()
        super(TrackBack, self).save()
    
    class Admin:
        pass

class IncomingTrackBack(models.Model):
    title = models.CharField(_('Title'), max_length=255, null=True, blank=True, editable=False)
    excerpt = models.CharField(_('Excerpt'), max_length=255, null=True, blank=True, editable=False)
    url = models.URLField(_('URL'), max_length=255, editable=False)
    blog = models.CharField(_('Blog'), max_length=255, null=True, blank=True, editable=False)
    entry = models.ForeignKey(Entry, verbose_name=_('Entry'))
    time = models.DateTimeField(_('Time'), default=datetime.datetime.now)
    
    def __unicode__(self):
        return "%s: %s" % (self.blog, self.title)
    
    class Admin:
        pass

class Configuration(models.Model):
    site = models.ForeignKey(Site)
    option = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    
    def __unicode__(self):
        return "%s: %s" % (self.option, self.value)