from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
import notifications.urls
from auction.views import index, create_listing, listing_view, edit_listing,close_auction, watchlist, set_bid, \
    comment, my_wins, batchHttp, notifications_view, notifications_delete_view, \
    history_auctions, messagecompany
from accounts.views import userWin, createdAuction,company
from web3date.views import registeroperation



urlpatterns = [
    path("", company, name="company"),
    path('index/', index, name='index'),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("listing_view/<int:id>/", listing_view, name="listing_view"),
    path("create_listing/", create_listing, name="create_listing"),
    path("edit_listing/<int:id>/", edit_listing, name="edit_listing"),
    path("watchlist/", watchlist, name="watchlist"),
    path("watchlist/<int:id>/", watchlist, name="watchlist"),
    path("close_auction/<int:id>/", close_auction, name="close_auction"),
    path("set_bid/<int:id>/", set_bid, name="set_bid"),
    path("comment/<int:id>/", comment, name="comment"),
    path("my_wins/",my_wins, name="my_wins"),
    path("batch/",batchHttp, name="batch"),
    path("userwin/",userWin, name="mywinner"),
    path("createdAuction/", createdAuction, name="mycreated"),
    path("operation/", registeroperation, name='operation'),
    path('notifications/', notifications_view, name='message_notification'),
    path('notifications/delete/', notifications_delete_view, name='delete'),
    path("web3date/", include("web3date.urls")),
    path("history/", history_auctions, name="history"),
    path("messagecompany/<str:username>/",messagecompany, name="messagecompany"),




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
