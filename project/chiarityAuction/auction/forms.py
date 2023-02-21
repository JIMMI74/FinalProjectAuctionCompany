
from django import forms
from .models import AuctionListing, Message



class AuctionListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['product', 'photo', 'description', 'starting_bid', 'date', 'start', 'end']
        widgets = {'product': forms.TextInput(attrs={'placeholder': '20 characters max.'}),
                   'description': forms.Textarea(attrs={'placeholder': '50 characters max; ''for more information leave'
                                                                       'an expression of interest in the forum; '
                                                                       'we will contact you by email'}),
                   'start': forms.DateTimeInput(attrs={'type': 'datetime-local', 'required': 'true'}),
                   'end': forms.DateTimeInput(attrs={'type': 'datetime-local'})}

        

class DescriptionForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['description', 'photo']
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}

        

class MessageForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={"placeholder": "example@gmail.com"}))
    info_details_auction = forms.CharField(widget=forms.Textarea(attrs={'rows': 10,
                                                                        "placeholder":
                                                                            "Write here to get all the details of the auction"}))





    class Meta:
        model = Message
        fields = ["auction_reference_code", "email","date", "info_details_auction"]
        labels = {'auction_reference_code': 'Auction Code', 'email': 'Email', 'date': 'Date'}




