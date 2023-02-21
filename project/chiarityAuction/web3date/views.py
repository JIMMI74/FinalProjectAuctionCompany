from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User
from auction.models import *
from django.utils import timezone
from notifications.models import Notification
from notifications.signals import notify
from auction.models import AuctionListing
from .serializers import ElementAuctionSerializer
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.messages import constants
from django.utils import timezone
from django.http import request


import redis

db_redis = redis.StrictRedis(host='127.0.0.1', port=6379, password='', db=0)
#print(db_redis.get('notifications')) # request in terminal if redis is ok


time = timezone.now()
date_time = time.strftime("%m/%d/%Y, %H:%M:%S")
notifications = Notification.objects.all()



@login_required
def registeroperation(request):
    user = User.objects.get(username=request.user)

    active_listings = AuctionListing.objects.filter(active=False, saved_on_redis=False).all()

    slider1 = active_listings[0:13]

    print(request.user.id, 'USER ID operation')
    for obj in active_listings:
        if (obj.end < time) or (obj.manualClose == True):
            print('check obj auction', obj.saved_on_redis)
            if obj.current_winner is None:
                obj.saved_on_redis = True
                obj.save()
                db_redis.rpush(f'{obj.auction_number} - {obj.product} - {obj.profile}', 'No winner for this auction')
                notify.send(request.user, recipient=request.user, verb=f'Auction - {obj.auction_number} - {obj.product} '
                                                                       f'- is ended up without winners!', timestamp=time)
                return render(request, "register_operation.html", context={'active_listings': active_listings})

            else:
                obj.active = False
                obj.saved_on_redis = True
                obj.writeOnChain()
                print(obj.hash, 'HASH')
                obj.save()

                db_redis.rpush(f'{obj.profile}- -{obj.auction_number}- -{obj.product}- {obj.current_winner}-'
                               f'{obj.current_price} --{obj.end}', f'Congratulations, you won the auction - '
                                                                   f'{obj.profile} - for the price of {obj.current_price}!')

                notify.send(obj, recipient=user, verb=f' Auction - {obj.auction_number}-{obj.product} -- is over: {obj.current_winner} '
                                                      f'has won! Purchased at the price of {obj.current_price} -', timestamp=time)

                notify.send(obj, recipient=obj.current_winner, verb=f'Congratulations you have won the {obj.auction_number}'
                                                                    f' - - {obj.product} '
                                                                    f'auction!', timestamp=time, pkobject=obj.pk)
                return render(request, "register_operation.html", context={'active_listings': active_listings})
    context = {"active_listings": active_listings, "slider1": slider1,"notifications": notifications, "user": user}

    return render(request, "register_operation.html", context)


@login_required
def detailsauctions(request):
    response = []
    details = AuctionListing.objects.filter(active=False, manualClose=True).all()

    for detail in details:

        response.append(
            {
                'Code': detail.auction_number,
                'price close': detail.current_price,
                'product': detail.product,
                'description': detail.description,
                'starting bid': detail.starting_bid,
                'hash': detail.hash,
                'txId': detail.txId,


            }
        )

    return HttpResponse(json.dumps(response), content_type='application/json')




def JSON_profile_view(request, pk):
    auction_date = get_object_or_404(AuctionListing, pk=pk)
    json = ElementAuctionSerializer(auction_date)
    return JsonResponse(json.data)




def Json_auction(request, pk):
    auction = get_object_or_404(AuctionListing, pk=pk)

    context = {
        'auction': auction,
        'notifications': notifications,
    }

    return render(request, 'web3date/send_message_auction.html', context)


#



def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user.pk).order_by('-timestamp')

    notifications.mark_all_as_read()
    notifications.update()

    context = {'notifications': notifications}

    return render(request, 'web3date/notifications.html', context)



def about_view(request):
    context = {
        'notifications': notifications,
    }

    return render(request, 'web3date/about.html', context)


def notifications_delete_view(request):
    notifications = Notification.objects.filter(recipient=request.user.pk)
    notifications.delete()
    return redirect('/notifications/')







