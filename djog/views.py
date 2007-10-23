
from django.core import urlresolvers
from django.contrib.comments.views.comments import post_free_comment
from django.http import HttpResponseRedirect

def post_free_comment_redirect(request):
    if request.POST.has_key('url'):
        url = request.POST['url']
    else:
        url = urlresolvers.reverse('djog_index')
    response = post_free_comment(request)
    return HttpResponseRedirect(url)
