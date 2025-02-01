from django import forms
from django_ace import AceWidget
from ..models import Post

class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=AceWidget(
            mode='html',
            theme='monokai',
            width='900px',
            height='500px',
            fontsize='15px',
        )
    )

    class Meta:
        model = Post
        fields = '__all__'