from django import forms
from .models import Message, Conversation


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content', 'image', 'file', 'video')
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Напишіть повідомлення...',
                'autocomplete': 'off',
                'id': 'msg-input',
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'video': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'content': '',
            'image': 'Фото',
            'file': 'Файл',
            'video': 'Відео',
        }


class NewConversationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Ім'я користувача"}),
        label='Знайти користувача'
    )
