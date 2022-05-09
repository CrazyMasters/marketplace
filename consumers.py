from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from rest_framework.utils import json

# локальные импорты
from .models import Order


class OrderConsumer(WebsocketConsumer):
    queryset = Order.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.scope["user"])

    def get_object(self):
        try:
            return self.get_queryset().get(id=self.scope['url_route']['kwargs']['pk'])
        except self.queryset.model.DoesNotExist:
            return None

    def connect(self):
        try:
            self.order = self.get_object()
            if self.order:
                self.room_name = self.order.id
                self.room_group_name = f'order-{self.room_name}'
                async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
                self.accept()
        except Order.DoesNotExist:
            self.disconnect(404)

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': text_data_json["type"],
                'message': message
            }
        )

    def order_change(self, event):
        self.send(text_data=event["message"])


class OrderAdminConsumer(WebsocketConsumer):
    queryset = Order.objects.all()

    def get_queryset(self):
        return self.queryset.filter(store__user=self.scope["user"])

    def get_object(self):
        try:
            return self.get_queryset().get(id=self.scope['url_route']['kwargs']['pk'])
        except self.queryset.model.DoesNotExist:
            return None

    def connect(self):
        self.room_name = self.scope['user'].id
        self.room_group_name = f'order-admin-{self.room_name}'
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': text_data_json["type"],
                'message': message
            }
        )

    def new_order(self, event):
        self.send(text_data=event["message"])

        # Receive message from room group

    def order_paid(self, event):
        self.send(text_data=event["message"])
