from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post
from .services import GPT2Service

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border rounded',
            'placeholder': _('Your Name')
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-2 border rounded',
            'placeholder': 'Your Email'
        }),
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border rounded',
            'placeholder': 'Subject'
        }),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full p-2 border rounded',
            'placeholder': 'Your Message',
            'rows': 5
        }),
    ) 