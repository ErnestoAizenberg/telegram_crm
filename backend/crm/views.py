from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import Contact, Conversation, Message, ResponseTemplate, TelegramAccount, Analytics
from .serializers import *

class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    
    def get_queryset(self):
        return Contact.objects.filter(
            telegram_account__user=self.request.user
        ).select_related('telegram_account')

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        return Conversation.objects.filter(
            telegram_account__user=self.request.user
        ).select_related('contact', 'telegram_account')
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        content = request.data.get('content')
        
        # Send message via Telegram client
        # This would integrate with your TelegramCRMClient
        success = True  # Placeholder
        
        if success:
            return Response({'status': 'message sent'})
        else:
            return Response({'error': 'failed to send'}, status=400)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')
        queryset = Message.objects.filter(
            conversation__telegram_account__user=self.request.user
        )
        
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
            
        return queryset.select_related('conversation')

class AnalyticsViewSet(viewsets.ViewSet):
    def list(self, request):
        user = request.user
        time_range = request.query_params.get('range', '7d')
        
        if time_range == '7d':
            start_date = datetime.now() - timedelta(days=7)
        elif time_range == '30d':
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = datetime.now() - timedelta(days=7)
        
        analytics = Analytics.objects.filter(
            telegram_account__user=user,
            date__gte=start_date
        )
        
        # Calculate metrics
        total_messages_sent = sum(a.messages_sent for a in analytics)
        total_messages_received = sum(a.messages_received for a in analytics)
        total_new_contacts = sum(a.new_contacts for a in analytics)
        
        response_data = {
            'messages_sent': total_messages_sent,
            'messages_received': total_messages_received,
            'new_contacts': total_new_contacts,
            'response_rate': (total_messages_sent / total_messages_received * 100) if total_messages_received > 0 else 0,
        }
        
        return Response(response_data)