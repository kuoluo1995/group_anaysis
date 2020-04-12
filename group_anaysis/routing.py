from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from group_anaysis import socket_view

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([path('socket_search_topics_by_person_ids/', socket_view.SocketSearchTopicsByPersonIds), ])
    ),
})
