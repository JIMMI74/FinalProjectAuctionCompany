from django.urls import path, include
import notifications.urls
from .views import detailauction, JSON_profile_view, detail_element_auction,notifications_delete_view, Json_auction
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('detailjson/', detailauction, name='detailjson'),
    path('JSON_profile_view/<int:pk>/', JSON_profile_view, name='JSON_profile_view'),
    path('send_message/<int:pk>/', Json_auction, name='send_message'),
    path('notifications/delete/', notifications_delete_view, name='delete'),
]
