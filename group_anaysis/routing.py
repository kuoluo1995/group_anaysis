from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from services import socket_service

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([path('socket_search_topics_by_person_ids/', socket_service.SocketSearchTopicsByPersonIds), ])
    ),
})
