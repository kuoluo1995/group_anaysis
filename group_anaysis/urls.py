from django.contrib import admin
from django.urls import path, include

from group_anaysis import view

urlpatterns = [
    path('search_ranges_by_name', view.search_ranges_by_name),
    path('search_person_by_ranges', view.search_person_by_ranges),
    path('admin/', admin.site.urls),
]
