from django.urls import path
from apps.core.consumers import ChatBotConsumer
print("ENTRA A ROUTING")

websocket_urlpatterns = [
    path('ws/chatbot/', ChatBotConsumer.as_asgi()),
]
