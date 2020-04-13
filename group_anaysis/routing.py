from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from group_anaysis.socket_view import search_topic, compare_topic

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([path('socket_search_topics_by_person_ids/', search_topic.SearchTopicsByPersonIds),
                   path('socket_compare_topics_by_person_ids/', compare_topic.ComparedTopicsByPersonIds)])
    ),
})
