import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm.models import TelegramAccount, Contact, Conversation, Message

class TelegramCRMClient:
    def __init__(self, account: TelegramAccount):
        self.account = account
        self.client = TelegramClient(
            StringSession(account.session_string),
            int(account.api_id),
            account.api_hash
        )
        
    async def start(self):
        await self.client.start(phone=lambda: self.account.phone_number)
        self.account.session_string = self.client.session.save()
        self.account.is_active = True
        self.account.save()
        
        # Add event handlers
        self.client.add_event_handler(self.handle_new_message)
        
    async def handle_new_message(self, event):
        # Process incoming messages
        sender = await event.get_sender()
        
        # Get or create contact
        contact, created = await self.get_or_create_contact(sender)
        
        # Get or create conversation
        conversation, created = await self.get_or_create_conversation(contact)
        
        # Create message record
        message = Message.objects.create(
            conversation=conversation,
            telegram_message_id=event.id,
            message_type='incoming',
            content=event.text,
            timestamp=event.date
        )
        
        # Update conversation
        conversation.unread_count += 1
        conversation.last_message_at = event.date
        conversation.save()
        
        # Broadcast via WebSocket
        await self.broadcast_new_message(message)
    
    async def get_or_create_contact(self, telegram_user):
        contact, created = Contact.objects.get_or_create(
            telegram_account=self.account,
            telegram_id=telegram_user.id,
            defaults={
                'username': telegram_user.username or '',
                'first_name': telegram_user.first_name or '',
                'last_name': telegram_user.last_name or '',
                'phone_number': telegram_user.phone or '',
            }
        )
        return contact, created
    
    async def get_or_create_conversation(self, contact):
        conversation, created = Conversation.objects.get_or_create(
            contact=contact,
            telegram_account=self.account
        )
        return conversation, created
    
    async def send_message(self, contact, content):
        try:
            result = await self.client.send_message(contact.telegram_id, content)
            
            # Create message record
            conversation = await self.get_or_create_conversation(contact)
            message = Message.objects.create(
                conversation=conversation,
                telegram_message_id=result.id,
                message_type='outgoing',
                content=content,
                timestamp=result.date
            )
            
            await self.broadcast_new_message(message)
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    async def broadcast_new_message(self, message):
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        await channel_layer.group_send(
            f"conversation_{message.conversation.id}",
            {
                'type': 'new_message',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'message_type': message.message_type,
                    'timestamp': message.timestamp.isoformat(),
                    'conversation_id': message.conversation.id,
                }
            }
        )