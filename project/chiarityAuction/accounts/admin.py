from django.contrib import admin
from accounts.models import Profile
from auction.models import AuctionListing, Bid, Comment, Watchlist,Message


admin.site.register([  Bid, Comment, Watchlist])

@admin.register(AuctionListing)
class AuctionListingAdmin(admin.ModelAdmin):

    list_display = ('pk', 'auction_number', 'current_winner','product', 'description', 'current_price', 'date', 'active', 'profile','photo'
                    ,'slug','starting_bid', 'start','end')
    list_filter = ('product', 'current_winner', 'description', 'current_price', 'date', 'active', 'profile')
    search_fields = ('product', 'description', 'current_price', 'date', 'active', 'profile')
    
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user')
    list_filter = ('user',)
    search_fields = ('user',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('author','id','email','auction_reference_code','info_details_auction','date')
    list_filter = ('email','auction_reference_code','info_details_auction','date')
    search_fields = ('email','auction_reference_code','info_details_auction','date')








""" @admin.unregister(User)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email', 'first_name', 'last_name') """