from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
from enumfields import EnumField

from app.models import ParticipantRole, SignupLocation, Player, User
from app.util import most_recent_game

from datetime import datetime


def get_signup_locations():
    return ((x.id, x) for x in SignupLocation.objects.filter(game=most_recent_game()))

def get_players():
    return ((x.id, f'{str(x)} - {x.shop_score()}') for x in Player.objects.filter(game=most_recent_game()))

def get_users():
    return ((x.id, x.get_full_name()) for x in User.objects.filter(is_active=True))


class ModeratorSignupPlayerForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                'class': 'ui-input',
            }
        )
    )

    location = forms.ChoiceField(
        label="Signup Location",
        choices=get_signup_locations,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        )
    )

    participant_role = EnumField(ParticipantRole, max_length=1).formfield(
        label="Role",
        required=False,
        help_text=
        "If the player role is blank and the game is running, the player will NOT be able to sign up for the game. "
        "However, if this is blank and the game is in signup mode, the player will sign up normally.",
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        ),
    )

    def clean_location(self):
        data = self.cleaned_data['location']
        return SignupLocation.objects.get(pk=data)

class ModMessageForm(forms.Form):

    recipients = forms.ChoiceField(
        label="Recipients",
        choices=[("All", "All"), ("Humans", "Humans"), ("Zombies", "Zombies"), ("Volunteers", "Volunteers")],
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        )
    )
    
    subject = forms.CharField(
        label="Subject",
        required=True,
        widget=forms.Textarea(
            attrs={
                'class': 'ui-input',
                'rows': '1',
                'placeholder': 'Message subject'
            }
        )
    )    

    message = forms.CharField(
        label="Message",
        required=True,
        widget=forms.Textarea(
            attrs={
                'class': 'ui-input',
                'rows': '10',
                'placeholder': 'Your message'
            }
        )
    )

class GenerateSupplyCodeForm(forms.Form):
    code = forms.CharField(
        label="Supply Code ID",
        min_length=6,
        max_length=6,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': 'Leave blank to auto-gen'
            }
        )
    )
    value = forms.IntegerField(
        label="Value",
        initial=5,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'input_type':'number'
            }
        )
    )  
    
class AddSignupForm(forms.Form):
    location = forms.CharField(
        label="Location",
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': 'e.g. MC'
            }
        )
    )
    
class GameStartForm(forms.Form):
    name = forms.CharField(
        label="Name",
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': 'e.g. Fall 3100 HvZ'
            }
        )
    )
    
    start_time = forms.DateTimeField(
        label="Date/Time to Start",
        help_text=f"Note the time difference between the server and you. Current server time is {datetime.now()}.",
         widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm",
                                       "pickSeconds": False},
                               attrs={
                                   'class': 'ui-input',
                                   'placeholder': "YYYY-MM-DD HH:mm"}))
    
class ShopForm(forms.Form):
    buyer = forms.ChoiceField(
        label="Buyer",
        choices=get_players,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        )
    )
    
    purchase = forms.CharField(
        label="Purchase Info",
        required=False,
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': 'Leave a note of what was bought!'
            }
        )
    )
    cost = forms.IntegerField(
        label="Cost",
        min_value=0,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'input_type':'number'
            }
        )
    )

class AddModForm(forms.Form):
    mod = forms.ChoiceField(
        label="User To Become A Mod",
        choices=get_users,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        )
    )
    
class AddVolunteerForm(forms.Form):
    volunteer = forms.ChoiceField(
        label="User To Become A Volunteer",
        choices=get_users,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        )
    )