from django.db import models
from django.contrib.auth.models import User
from aaron.blog import search
import datetime, httplib, urllib, urlparse, re

class Entry(models.Model):
	title = models.CharField(max_length=100, unique=True)
	slug = models.SlugField(prepopulate_from=("title",), max_length=100, unique=True)
	text = models.TextField()
	author = models.ForeignKey(User)
	tags = models.ManyToManyField("Tag", filter_interface=models.HORIZONTAL)
	pub_date = models.DateTimeField(default=datetime.datetime.now)
	
	search = search.SphinxSearch()

	def __unicode__(self):
		return self.title

	class Meta:
		ordering = ('-pub_date',)
		get_latest_by = 'pub_date'

	class Admin:
		list_display = ('pub_date', 'title',)
		search_fields = ['title', 'text']

	def get_absolute_url(self):
		return "/blog/%s/%s/" % (self.pub_date.strftime("%Y/%b/%d").lower(), self.slug)
	
	def get_rss_url(self):
		return "/blog/feeds/comments/%s/%s/" % (self.pub_date.strftime("%Y/%b/%d").lower(), self.slug)
	
	def get_trackback_url(self):
		return "/blog/trackback/%s/" % self.pk

class Tag(models.Model):
	tag = models.CharField(max_length=50, unique=True, core=True)
	slug = models.SlugField(prepopulate_from=("tag",), max_length=50, unique=True)

	def __unicode__(self):
		return self.tag

	class Admin:
		pass

	def num_stories(self):
		return Entry.objects.filter(tags__tag=self).count()

	def get_absolute_url(self):
		return "/blog/tags/%s/" % (self.slug)
	
	def get_rss_url(self):
		return "/blog/feeds/tags/%s/" % self.slug

class TrackBack(models.Model):
	entry = models.ForeignKey(Entry, edit_inline=models.STACKED, num_in_admin=1)
	url = models.URLField(max_length=255, core=True)
	tbURL = models.URLField(max_length=255, null=True, blank=True, editable=False)
	status = models.BooleanField(null=True, blank=True, editable=False)
	error = models.CharField(max_length=255, null=True, blank=True, editable=False)
	
	def __unicode__(self):
		return self.url
	
	def autodiscover(self):
		url = urlparse.urlparse(self.url)
		host = url[1]
		path = url[2]
		conn = httplib.HTTPConnection(host)
		conn.request("GET", path)
		response = conn.getresponse()
		data = response.read()
		tbpattern = r'trackback:ping="(.*?)"'
		reg = re.search(tbpattern, data)
		if reg:
			self.tbURL = reg.group(1)
	
	def ping(self):
		params = urllib.urlencode({'title': self.entry.title, 'url': "http://71.201.176.194:8080%s" % self.entry.get_absolute_url(), 'excerpt': self.entry.text, 'blog_name': "Alex's Blog"})
		headers = ({"Content-type": "application/x-www-form-urlencoded", "User-Agent": "Python"})
		tbURLTuple = urlparse.urlparse("%s" % self.tbURL)
		host = tbURLTuple[1]
		path = tbURLTuple[2]
		connection = httplib.HTTPConnection(host)
		connection.request("POST", path, params, headers)
		response = connection.getresponse()
		httpResponse = response.reason
		data = response.read()
		errorpattern = r'<error>(.*?)</error>'
		reg = re.search(errorpattern, data)
		if reg:
			tbErrorCode = reg.group(1)
			if int(tbErrorCode) == 0:
				self.status = True
			else:
				errorpattern2 = r'<message>(.*?)</message'
				reg2 = re.search(errorpattern2, self.tbResponse)
				if reg2:
					self.error = reg2.group(1)
		connection.close()
	
	def save(self):
		self.autodiscover()
		self.ping()
		super(TrackBack, self).save()
	
	class Admin:
		pass

class IncomingTrackBack(models.Model):
	title = models.CharField(max_length=255, null=True, blank=True, editable=False)
	excerpt = models.CharField(max_length=255, null=True, blank=True, editable=False)
	url = models.URLField(max_length=255, editable=False)
	blog = models.CharField(max_length=255, null=True, blank=True, editable=False)
	entry = models.ForeignKey(Entry)
	time = models.DateTimeField(default=datetime.datetime.now)
	
	def __unicode__(self):
		return "%s: %s" % (self.blog, self.title)
	
	class Admin:
		pass
