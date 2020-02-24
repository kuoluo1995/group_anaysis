from django.urls import path

from group_anaysis import view

urlpatterns = [
    # debug
    path('test_init_ranges/', view.test_init_ranges),
    path('test_search_ranges_by_name/', view.test_search_ranges_by_name),
    path('test_search_person_by_ranges/', view.test_search_person_by_ranges),
    path('test_search_topics_by_person_ids/', view.test_search_topics_by_person_ids),
    # online
    path('init_ranges/', view.init_ranges),
    path('search_ranges_by_name/', view.search_ranges_by_name),
    path('search_person_by_ranges/', view.search_person_by_ranges),
    path('search_topics_by_person_ids/', view.search_topics_by_person_ids),
]
