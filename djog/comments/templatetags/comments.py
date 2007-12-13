
from django.template import TemplateSyntaxError
from django.template import Node, Library, Variable
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from djog.comments.models import Comment

register = Library()

class CommentFormNode(Node):
    def __init__(self):
        pass
    
    def render(self, context):
        return u""
def do_comment_form(parser, token):
    return CommentFormNode()
register.tag("comment_form", do_comment_form)

class CommentCountNode(Node):
    def __init__(self, package, module, context_var_name, obj_id, var_name):
        self.package, self.module = package, module
        if context_var_name is not None:
            context_var_name = Variable(context_var_name)
        self.context_var_name, self.obj_id = context_var_name, obj_id
        self.var_name = var_name
    
    def render(self, context):
        comment_count = Comment.objects.filter(
            object_id = self.obj_id,
            content_type__app_label = self.package,
            content_type__model = self.module,
            # site__id = settings.SITE_ID,
        ).count()
        context[self.var_name] = comment_count
        return u""
def do_comment_count(parser, token):
    bits = token.contents.split()
    if len(bits) != 6:
        raise TemplateSyntaxError, "%r tag requires 5 arguments" % bits[0]
    if bits[1] != "for":
        raise TemplateSyntaxError,
            "Second argument in %r tag must be 'for'" % bits[0]
    try:
        package, module = bits[2].split(".")
    except ValueError: # unpack list of wrong size
        raise TemplateSyntaxError,
            "Third argument in %r tag must be in the format 'package.module'" % bits[0]
    try:
        content_type = ContentType.objects.get(app_label=package, model=module)
    except ContentType.DoesNotExist:
        raise TemplateSyntaxError,
            "%r tag has invalid content-type '%s.%s'" % (bits[0], package, module)
    var_name, obj_id = None, None
    if bits[3].isdigit():
        obj_id = bits[3]
        try: # ensure the object ID is valid
            content_type.get_object_for_this_type(pk=obj_id)
        except ObjectDoesNotExist:
            raise TemplateSyntaxError,
                "%r tag refers to %s object with ID %s, which doesn't exist" % (
                    bits[0],
                    content_type.name,
                    obj_id,
                )
    else:
        var_name = bits[3]
    if bits[4] != "as":
        raise TemplateSyntaxError, "Fourth argument in %r must be 'as'" % bits[0]
    return CommentCountNode(package, module, var_name, obj_id, bits[5])
register.tag("get_comment_count", do_comment_count)

class CommentListNode(Node):
    def __init__(self):
        pass
    
    def render(self, context):
        return u""
def do_comment_list(parser, token):
    return CommentListNode()
register.tag("get_comment_list", do_comment_list)
