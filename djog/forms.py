from django import newforms as forms

class CommentForm(forms.Form):
	person_name = forms.CharField(label='Name (required)', widget=forms.TextInput(attrs={'size':'22'}))
	comment = forms.CharField(label='', widget=forms.Textarea(attrs={'cols':'60'}))
