import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer для чату в реальному часі."""

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close()
            return

        # Перевіряємо доступ до розмови
        has_access = await self.user_in_conversation(user, self.conversation_id)
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get('content', '').strip()
        if not content:
            return

        user = self.scope['user']
        msg = await self.save_message(user, self.conversation_id, content)

        # Розсилаємо всім учасникам кімнати
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': msg['id'],
                'content': msg['content'],
                'sender': msg['sender'],
                'sender_name': msg['sender_name'],
                'avatar': msg['avatar'],
                'time': msg['time'],
            }
        )

        # Створюємо сповіщення для інших учасників
        await self.create_notifications(user, self.conversation_id, content)

    async def chat_message(self, event):
        """Надсилаємо повідомлення в WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'id': event['message_id'],
            'content': event['content'],
            'sender': event['sender'],
            'sender_name': event['sender_name'],
            'avatar': event['avatar'],
            'time': event['time'],
        }))

    @database_sync_to_async
    def user_in_conversation(self, user, conversation_id):
        from .models import Conversation
        try:
            conv = Conversation.objects.get(pk=conversation_id)
            return conv.participants.filter(id=user.id).exists()
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, user, conversation_id, content):
        from .models import Conversation, Message
        conv = Conversation.objects.get(pk=conversation_id)
        msg = Message.objects.create(
            conversation=conv,
            sender=user,
            content=content,
        )
        return {
            'id': msg.id,
            'content': msg.content,
            'sender': user.username,
            'sender_name': user.get_full_name() or user.username,
            'avatar': user.get_avatar_url(),
            'time': msg.created_at.strftime('%H:%M'),
        }

    @database_sync_to_async
    def create_notifications(self, sender, conversation_id, content):
        from .models import Conversation
        from notifications.models import Notification, NotificationSettings
        try:
            conv = Conversation.objects.get(pk=conversation_id)
            for participant in conv.participants.exclude(id=sender.id):
                try:
                    s = participant.notification_settings
                    if not s.notify_messages:
                        continue
                except Exception:
                    pass
                Notification.objects.create(
                    recipient=participant,
                    sender=sender,
                    notif_type='message',
                    text=f'Нове повідомлення від {sender.get_full_name() or sender.username}',
                    link=f'/chat/{conversation_id}/',
                )
        except Exception:
            pass
