
from django import newforms as forms
from django.utils.translation import ugettext_lazy as _


class CommentForm(forms.Form):
    """
    A form representing a comment on an entry.
    """
    person_name = forms.CharField(
        label = _("Name (required)"),
        widget = forms.TextInput(attrs=dict(size="22")))
        
    comment = forms.CharField(
        label = "",
        widget = forms.Textarea(attrs=dict(cols="60")))
