# chat/routing.py
from django.urls import re_path

from .consumers import OrderConsumer
from .consumers import OrderAdminConsumer

websocket_urlpatterns = [
    # chats
    re_path(r'ws/orders/(?P<pk>\w+)/$', OrderConsumer.as_asgi()),
    re_path(r'ws/admin/orders/', OrderAdminConsumer.as_asgi()),
]
