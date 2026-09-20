from django import forms
from .models import NotificationSettings


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = NotificationSettings
        fields = (
            'notify_friend_request',
            'notify_likes',
            'notify_comments',
            'notify_messages',
            'notify_group_invites',
        )
        widgets = {
            'notify_friend_request': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_likes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_messages': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_group_invites': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'notify_friend_request': 'Запити у друзі',
            'notify_likes': 'Лайки',
            'notify_comments': 'Коментарі',
            'notify_messages': 'Повідомлення',
            'notify_group_invites': 'Запрошення до груп',
        }
