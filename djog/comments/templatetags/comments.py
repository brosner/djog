
from django import template

register = template.Library()

class CommentFormNode(template.Node):
    def __init__(self):
        pass
    
    def render(self, context):
        return u""
def do_comment_form(parser, token):
    return CommentFormNode()
register.tag("comment_form", do_comment_form)

class CommentCountNode(template.Node):
    def __init__(self):
        pass
    
    def render(self, context):
        return u""
def do_comment_count(parser, token):
    return CommentCountNode()
register.tag("get_comment_count", do_comment_count)

class CommentListNode(template.Node):
    def __init__(self):
        pass
    
    def render(self, context):
        return u""
def do_comment_list(parser, token):
    return CommentListNode()
register.tag("get_comment_list", do_comment_list)
