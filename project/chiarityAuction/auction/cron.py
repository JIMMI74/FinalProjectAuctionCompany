from .views import batch
from .models import AuctionListing

def newbatch():
    print('lancio batch')
    result = batch()
    print('fine batch', result)
    # if result == 'ok':
    #     state = AuctionListing.objects.filter(active=True)
    #     print('state', State)
    #     for obj in state:
    #         obj.active = False
    #         obj.save()
    #         print('fine batch', obj)


