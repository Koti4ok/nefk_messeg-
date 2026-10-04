from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('post_type', 'content', 'image', 'video', 'link')
        widgets = {
            'post_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Що у вас нового?'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'video': forms.FileInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }
        labels = {
            'post_type': 'Тип',
            'content': 'Текст',
            'image': 'Зображення',
            'video': 'Відео',
            'link': 'Посилання',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш коментар...'
            })
        }
        labels = {'content': ''}
