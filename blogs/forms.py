from django import forms
from .models import Comment
import bleach

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your comment...',
                'class': 'w-full p-2 border rounded text-gray-700 dark:text-gray-300 dark:bg-gray-700'
            }),
        }