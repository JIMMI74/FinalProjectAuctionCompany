from django.db import models
from django.contrib.auth.models import User
from accounts.models import Profile, User
from django.utils import timezone
from rest_framework import serializers
from web3date.utils import sendTransaction
import hashlib
import json
from django.core import serializers




class AuctionListing(models.Model):
    auction_number = models.IntegerField(default=0)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile")
    product = models.CharField(max_length=200)
    start = models.DateTimeField(blank=True)
    end = models.DateTimeField(blank=True)
    description = models.TextField(max_length=500)
    starting_bid = models.FloatField(default=0.01)
    current_price = models.FloatField()
    current_winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_winner", blank=True, null=True)
    date = models.DateTimeField(default=timezone.now, blank=True)
    active = models.BooleanField(default=True)
    saved_on_redis = models.BooleanField(default=False)
    manualClose = models.BooleanField(default=False)
    photo = models.ImageField(upload_to="pics/%y/%m/%d/")
    slug = models.SlugField(max_length=200, db_index=True)
    hash = models.CharField(max_length=64, default=None, null=True)
    txId = models.CharField(max_length=66, default=None, null=True)
    json_auction = models.TextField(default=None, null=True, max_length=5000)

    def save(self, *args, **kwargs):
        numbers = AuctionListing.objects.all()
        numbers = numbers.count()
        self.auction_number = numbers + 1
        super(AuctionListing, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.product}: $ {self.current_price}: ${self.date}"
    
    def writeOnChain(self):
            serializeobj = serializers.serialize('json', [self, self.current_winner])
            print('json self', serializeobj)
            self.hash = hashlib.sha256(serializeobj.encode('utf-8')).hexdigest()
            print('hash self',self.hash)
            self.txId = sendTransaction(self.hash)
            self.json_auction = serializeobj
            self.save()







            
class Watchlist(models.Model):
   
    auction_listings = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='watchlist')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='watchlist')



class Bid(models.Model):
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="bids")
    value = models.FloatField()


class Comment(models.Model):
    date = models.DateField(auto_created=True, default=timezone.now())
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="comments")
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=500)


