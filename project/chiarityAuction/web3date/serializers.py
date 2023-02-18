from rest_framework import serializers
from auction.models import AuctionListing


class ElementAuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionListing
        fields = ['product', 'description', 'starting_bid', 'current_price', 'current_winner', 'manualClose',
                  'date', 'start', 'end',]
