from django.urls import path, include
import notifications.urls
from .views import detailsauctions, JSON_profile_view,notifications_delete_view, Json_auction

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('JSON_detailsauctions/', detailsauctions, name='JSON_detailsauctions'),
    path('JSON_profile_view/<int:pk>/', JSON_profile_view, name='JSON_profile_view'),
    path('send_message/<int:pk>/', Json_auction, name='send_message'),
    path('notifications/delete/', notifications_delete_view, name='delete'),



]
