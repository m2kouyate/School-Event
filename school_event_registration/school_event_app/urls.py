from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (EventListView, EventDetailView, EventCreateView,
                    EventUpdateView, EventDeleteView, EventTypeCreateView,
                    EventTypeUpdateView, EventTypeDeleteView, EventTypeDetailView, ParticipantCreateView,
                    EventImportView)

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('event/new/', EventCreateView.as_view(), name='event_create'),
    path('event/<int:pk>/edit/', EventUpdateView.as_view(), name='event_edit'),
    path('event/<int:pk>/delete/', EventDeleteView.as_view(), name='event_delete'),
    path('event-type/<int:pk>/', EventTypeDetailView.as_view(), name='eventtype_detail'),
    path('event-type/new/', EventTypeCreateView.as_view(), name='event_type_create'),
    path('event-type/<int:pk>/edit/', EventTypeUpdateView.as_view(), name='event_type_edit'),
    path('event-type/<int:pk>/delete/', EventTypeDeleteView.as_view(), name='event_type_delete'),
    path('event/<int:event_pk>/register/', ParticipantCreateView.as_view(), name='participant_create'),
    path('import/', EventImportView.as_view(), name='event_import'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

