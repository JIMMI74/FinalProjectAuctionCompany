from accounts.models import Profile
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.messages import constants
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db import connection, transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView
from notifications.models import Notification
from notifications.models import Notification
from notifications.signals import notify
from notifications.signals import notify
from .forms import AuctionListingForm, DescriptionForm, MessageForm
from .models import AuctionListing, User, Bid, Comment, Watchlist, Message
from datetime import datetime
from json import dumps
from zoneinfo import ZoneInfo
import redis
import os
db_redis = redis.StrictRedis(host='127.0.0.1', port=6379, password='', db=0)
print(db_redis, 'Registration')
#print(db_redis.get('notifications'))

time = timezone.now()
date_time = time.strftime("%m/%d/%Y, %H:%M:%S")
notifications = Notification.objects.all()


@login_required
def company(request):
    return render(request, "auction/company.html")

@login_required
def index(request):
    active_listings = AuctionListing.objects.filter(active=True).all().order_by('-auction_number')
    print(request.user.id, 'USER ID')

    return render(request, "auction/index.html", context={'active_listings': active_listings})


def create_listing(request):
    if request.method == "GET":
        return render(request, "auction/create_listing.html", {
            'form': AuctionListingForm()
        })
    if request.method == "POST":
        timezoneUser = ZoneInfo(request.META['TZ'])
        form = AuctionListingForm(request.POST, request.FILES)
        if form.is_valid():
            new_listing = AuctionListing()
            new_listing = form.save(commit=False)
            username = Profile.objects.get(user=request.user.pk)
            print(username, 'Username')
            new_listing.profile = username
            print (new_listing.profile, 'Owner')
            new_listing.current_price = form.cleaned_data['starting_bid']
            new_listing.description = form.cleaned_data['description']
            new_listing.product = form.cleaned_data['product']
            new_listing.photo = form.cleaned_data['photo']
            new_listing.date = form.cleaned_data['date'].replace(tzinfo=timezoneUser)
            new_listing.start= form.cleaned_data['start'].replace(tzinfo=timezoneUser)
            new_listing.end = form.cleaned_data['end'].replace(tzinfo=timezoneUser)
            if(new_listing.start > new_listing.end):
                messages.add_message(request=request, level=constants.ERROR, message='Start date must be before end date')
                return redirect('/create_listing')
            presently = timezone.now()
            presently.replace(minute=0 , second=0, microsecond=0)
            #adesso.replace(tzinfo=timezone)
            print(new_listing.start, 'START')
            print(presently, 'NOW')
            if(new_listing.start > presently):
                print('start > presently')
                new_listing.active = False
            new_listing.save()
            """ print(new_listing.author, 'AUHTOR')
            print(User)
            new_listing.current_price = form.starting_bid
            """
            form.save()
            messages.success(request, f'good job ! '
                                      f'Your object has been created successfully. '
                                      f'If you have started the auction time you can see it in the active listing.')
            notify.send(request.user, recipient=new_listing.profile.user, verb=f'Your object {new_listing.product} '
                                                                               f'has been created successfully.',
                        target=new_listing)
            return redirect('/index/')
        for error in form.errors.values():
            messages.add_message(request=request, level=constants.ERROR, message=error)
    HttpResponseRedirect('/index/'), {'form': AuctionListingForm()}


def listing_view(request, id):
    profile = Profile.objects.get(user=request.user.pk)
    listing = AuctionListing.objects.get(id=id)
    if listing == None:
        messages.error(request, "Object no present")
        return render(request, ('auction/index.html'))
    else:
        comments = Comment.objects.filter(auction_listing=listing).order_by('date')

    return render(request, "auction/view.html", {'listing': listing, 'comments': comments, 'profile': profile})


def edit_listing(request, id):
    if request.method == 'GET':
        new_listing = AuctionListing.objects.get(id=id)
        assert new_listing.profile == Profile.objects.get(user=request.user.pk), HttpResponseForbidden()
        print(new_listing.profile, 'AUTHOR')

        if new_listing.active:
            messages.warning(request, "you can only change the image and description together,"
                                      " or just the image.. do you want to proceed?")
            forms = DescriptionForm(initial={
                'description': new_listing.description,
                'photo': new_listing.photo,
            })
            print('description')
            print('photo')

            return render(request, "auction/edit_listing.html",
                          {'form': forms, 'id': id, 'type_form': 'DescriptionForm'})
        else:
            form = AuctionListingForm(initial={
                'product': new_listing.product,
                'photo': new_listing.photo,
                'description': new_listing.description,
                'starting_bid': new_listing.starting_bid,
                'start': new_listing.start,
                'end': new_listing.end,
            })
            return render(request, "auction/edit_listing.html",
                          {'form': form, 'id': id, 'type_form': 'AuctionListingForm'})

    if request.method == 'POST':
        print(request.POST, 'POST')
        listing = AuctionListing.objects.get(id=id)
        print(listing, 'LISTING')
        if request.POST['type_form'] == 'DescriptionForm':
            form = DescriptionForm(request.POST, request.FILES)
            if form.is_valid():
                listing.description = form.cleaned_data['description']
                listing.photo = form.cleaned_data['photo']
                listing.save()
                print(listing, 'SAVE')
                messages.success(request, f'good job ! '
                                      f'Your object has been edited successfully. '
                                      f'If you have started the auction time you can see it in the active listing.')

                context = {'listing': listing, 'fom': form}
                return redirect(f'/listing_view/{listing.id}/', context)
            else:
                for error in form.errors.values():
                    messages.add_message(request=request, level=constants.ERROR, message=error)
                return redirect(f'/edit_listing/{listing.id}/')


        elif request.POST['type_form'] == 'AuctionListingForm':
            form = AuctionListingForm(request.POST, request.FILES)
            listing = AuctionListing.objects.get(id=id)
            if form.is_valid():
                listing.product = form.cleaned_data['product']
                listing.description = form.cleaned_data['description']
                listing.photo = form.cleaned_data['photo']
                listing.starting_bid = form.cleaned_data['starting_bid']
                listing.save()
            messages.success(request, f'good job ! '
                                      f'Your object has been edited successfully. '
                                      f'If you have started the auction time you can see it in the active listing.')
            form.save()
        context = {'listing': listing, 'form': form}
        return redirect(f'/listing_view/{listing.id}/', context)

    else:
        return HttpResponseRedirect('/index/')


@login_required
def set_bid(request, id):
    now = timezone.now()
    user = request.user.pk
    if request.method == 'POST':
        bid = request.POST.get('bid')
        listing = AuctionListing.objects.get(id=id)
        if not user == listing.profile.user_id:
            print(user, 'USER PER BID')
            print(listing.profile.user_id, 'PROFILE PER BID')
            if listing.active == False:
                messages.add_message(request, constants.ERROR, message="Listing is not active.")
                return redirect(f'/listing_view/{listing.id}/')
            #if listing.start > now:
            if float(bid) < listing.current_price:
                messages.add_message(request, constants.ERROR, message="Bid has to be greater than current price.")
                return redirect(f'/listing_view/{listing.id}/')
            listing.current_price = bid
            listing.current_winner = request.user
            listing.save()
            db_redis.rpush('bids', f'{listing.id} - {bid} - {request.user} - {now} - {listing.current_winner} '
                                   f'- {listing.current_price}')
            print(db_redis.lrange('bids', 0, -1))
            messages.success(request, 'Your bid has been recorded!')
            notify.send(request.user, recipient=request.user,
                        verb=f'{request.user.username} has bid {bid}$ on  product: {listing.product}', timestamp=now)
            messages.add_message(request, constants.SUCCESS, message="Your bid has been placed!")
            return redirect(f"/listing_view/{listing.id}/")
        else:
            messages.add_message(request, constants.ERROR, message="You can't bid on your own listing.")
            return redirect(f'/listing_view/{listing.id}/')
    return render(request, 'auction/view.html')



@login_required
def close_auction(request, id):
    if request.method == 'POST':
        listing = AuctionListing.objects.get(id=id)
        if listing.profile == Profile.objects.get(user=request.user.pk) and listing.active == True:
            listing.active = False
            listing.manualClose = True
            listing.save()
            messages.add_message(request, constants.ERROR, message=" OK ! You closed the auction early!.")
            return redirect('/index/')

        else:
            messages.warning(request, 'You don''t close this auction early.')
            return redirect(f"/listing_view/{listing.id}/")
    return redirect('/index/')
  
        
@login_required
def comment(request, id):
    if request.method == 'POST':
        listing = AuctionListing.objects.get(id=id)
        print(id, 'chi E?')
        text = request.POST.get("comment")
        print(request.POST)
        new_comment = Comment()
        new_comment.text = text
        new_comment.auction_listing = listing
        new_comment.author = Profile.objects.get(user=request.user.pk)
        new_comment.save()
        return redirect(f"/listing_view/{listing.id}/")
    return redirect('/index/')

@login_required
def messagecompany(request, username):
    user = get_object_or_404(User, username=username)
    print(user, 'USER')
    profile = Profile.objects.get(user=request.user.pk)
    print(profile, 'PROFILE')
    if request.method == "GET":
        return render(request, "auction/message_company.html", {
            'form': MessageForm()
        })
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)

            new_message.author = profile
            print(new_message.author, 'AUTHOR')
            new_message.email = form.cleaned_data['email']
            new_message.auction_reference_code = form.cleaned_data['auction_reference_code']
            new_message.info_details_auction = form.cleaned_data['info_details_auction']
            new_message.date = form.cleaned_data['date']
            form.save()
            notify.send(request.user, recipient=user,
                        verb=f'{request.user.username} has sent you a message for the Auction Code n.{new_message.auction_reference_code}', timestamp=timezone.now())
            messages.success(request, 'Your message has been sent. You will receive information about the auction shortly. check your e-mail!')
            return redirect('/index/')
        else:
            for error in form.errors.values():
                messages.add_message(request=request, level=constants.ERROR, message=error)
    else:
        form = MessageForm()
    return render(request, 'auction/message_company.html', {'form': form, 'profile': profile,' username': username})

    

@login_required
def my_wins(request):
    if request.method == 'GET':
        winned_auctions = AuctionListing.objects.filter(active=False, current_winner=request.user.pk)
        return render(request, "auction/my_wins.html", {'winned_auctions': winned_auctions})






@login_required
def watchlist(request):
    if request.method == 'GET':
        if request.GET.get('listing_id'):
            id=request.POST.get('listing_id')
            watchlist = Watchlist.objects.filter(user_id=request.user.pk, auction_listings_id=id, active=True).all()
            if watchlist:
                return HttpResponse('si')
            else: 
                return HttpResponse('no')
        else:
            watchlist = Watchlist.objects.filter(user=request.user.pk).all()
            if watchlist:
                return HttpResponse('oggetti presenti')
            else:
                return HttpResponse('no oggetti')
    else:
        if request.POST.get('listing_id'):
            id=request.POST.get('listing_id')
            watchlist = Watchlist.objects.filter(user_id=request.user.pk, auction_listings_id=id).all()
            listing = AuctionListing.objects.get(id=request.POST.get('listing_id'))
            print(231,{id,watchlist,listing},request.user.pk)
            if not watchlist:
                watchlist1 = Watchlist()
                watchlist1.user = Profile.objects.get(user=request.user.pk) 
                watchlist1.auction_listings = listing
                print(dir(watchlist1))
                print(watchlist1.user_id,watchlist1.auction_listings_id)
                watchlist1.save()
                messages.add_message(request, constants.SUCCESS, message="Listing added to watchlist.")
                return HttpResponseRedirect('/accounts/user/'+str(request.user.username))
            else:
                messages.error(request,"Oggeto gia presente")
                return HttpResponseRedirect('/index/')
        
        else:
            messages.error(request,"errore listing id ")
            return render(request,('auction/index.html'))




def batch():
    with connection.cursor() as cursor:
        try:
            print('in cursor........')
            #cursor.execute("UPDATE auction_auctionlisting SET active = true ")
            #cursor.execute("SELECT * FROM auction_auctionlisting WHERE  start <= datetime('now') and  datetime('now') >= end ")
            #cursor.execute("SELECT id,start FROM auction_auctionlisting ")
            #cursor.execute("SELECT  datetime('now') as now  ")
            #row = cursor.fetchall()
            #print(row)
            cursor.execute("UPDATE auction_auctionlisting SET active = ( start <= datetime('now') and  datetime('now') <= end ) where manualClose = False ")
            cursor.fetchall() # ritorno emelenti modificati 
            return True
        except:
            return False

def batchHttp(request):
    result = batch()
    if result:
        return HttpResponse("ok")
    else:
        return HttpResponse("error")



def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user.pk).order_by('-timestamp')

    notifications.mark_all_as_read()
    notifications.update()
    print('notification:', notifications)
    context = {'notifications': notifications}

    return render(request, 'auction/notifications.html', context)

def notifications_delete_view(request):
    notifications = Notification.objects.filter(recipient=request.user.pk)
    notifications.delete()
    return redirect('/notifications/')


def history_auctions(request):
    active_listings = AuctionListing.objects.filter(active=False).order_by('-date')
    print(request.user.id, 'USER ID')

    return render(request, "auction/history.html", context={'active_listings': active_listings})


