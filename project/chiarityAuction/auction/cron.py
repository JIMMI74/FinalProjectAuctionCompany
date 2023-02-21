from .views import batch
from .models import AuctionListing

def newbatch():
    print('lancio batch')
    result = batch()
    print('fine batch', result)
   

