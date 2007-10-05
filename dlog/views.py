
from django.contrib.comments.views.comments import post_free_comment
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.encoding import smart_str

from dlog.models import *

def post_free_comment_redirect(request):
	if request.POST.has_key('url'):
		url = request.POST['url']
	else:
		url = '/blog/'
	response = post_free_comment(request)
	return HttpResponseRedirect(url)

def EntriesByTag(request, slug):
	tag = Tag.objects.get(slug=slug)
	entries = Entry.objects.filter(tags__slug=slug)
	return render_to_response('blog/tag_list.html', {'entries': entries, 'tag': tag})

def Search(request):
	if not request.GET.has_key('s'):
		return HttpResponseRedirect('/blog/')
	search = smart_str(request.GET['s'])
	all = Entry.search.query(search)
	
	return render_to_response('blog/search.html', {'term': search, 'results': all})

def trackback(request, id):
	if request.method != 'POST':
		return render_to_response('trackback.xml', {'error_code': 1, 'message': "Request type must be POST"})
	if not request.POST.get('url'):
		return render_to_response('trackback.xml', {'error_code': 1, 'message': "URL not specified"})
	tb = IncomingTrackBack()
	tb.entry_id = int(id)
	tb.title = request.POST.get('title')
	tb.excerpt = request.POST.get('excerpt')
	tb.url = request.POST.get('url')
	tb.blog = request.POST.get('blog_name')
	tb.save()
	return render_to_response('trackback.xml', {'error_code': 0})