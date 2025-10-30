from django.db import models
from django.contrib.auth.models import User

class TelegramAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    api_id = models.CharField(max_length=100)
    api_hash = models.CharField(max_length=100)
    session_string = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.user.username}"

class Contact(models.Model):
    telegram_account = models.ForeignKey(TelegramAccount, on_delete=models.CASCADE)
    telegram_id = models.BigIntegerField()
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    last_interaction = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['telegram_account', 'telegram_id']

    def __str__(self):
        return f"{self.first_name} {self.last_name} (@{self.username})"

class Conversation(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    telegram_account = models.ForeignKey(TelegramAccount, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    unread_count = models.IntegerField(default=0)
    last_message_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['contact', 'telegram_account']

class Message(models.Model):
    MESSAGE_TYPES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    telegram_message_id = models.BigIntegerField()
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

class ResponseTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Analytics(models.Model):
    telegram_account = models.ForeignKey(TelegramAccount, on_delete=models.CASCADE)
    date = models.DateField()
    messages_sent = models.IntegerField(default=0)
    messages_received = models.IntegerField(default=0)
    new_contacts = models.IntegerField(default=0)
    active_conversations = models.IntegerField(default=0)

    class Meta:
        unique_together = ['telegram_account', 'date']