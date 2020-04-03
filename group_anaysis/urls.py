from django.urls import path

from group_anaysis import view

urlpatterns = [
    # debug
    path('test_init_ranges/', view.test_init_ranges),
    path('test_search_ranges_by_name/', view.test_search_ranges_by_name),
    path('test_search_person_by_ranges/', view.test_search_person_by_ranges),
    path('test_search_address_by_address_ids/', view.test_search_address_by_address_ids),
    path('test_search_topics_by_person_ids/', view.test_search_topics_by_person_ids),
    path('test_adjust_topic_weights/', view.test_adjust_topic_weights),
    path('test_search_person_ids_by_draws/', view.test_search_person_ids_by_draws),
    # online
    path('init_ranges/', view.init_ranges),
    path('search_ranges_by_name/', view.search_ranges_by_name),
    path('search_person_by_ranges/', view.search_person_by_ranges),
    path('search_address_by_address_ids/', view.search_address_by_address_ids),
    path('search_topics_by_person_ids/', view.search_topics_by_person_ids),
    path('search_community_by_links/', view.search_community_by_links),
    path('adjust_topic_weights/', view.adjust_topic_weights),
    path('search_person_ids_by_draws/', view.search_person_ids_by_draws)
]
