from django import forms
from enumfields import EnumField

from app.models import ParticipantRole, SignupLocation, Player, User, PlayerRole
from app.util import most_recent_game

from datetime import datetime, date


def get_signup_locations():
    return ((x.id, x) for x in SignupLocation.objects.filter(game=most_recent_game()))

def get_players():
    return ((x.id, f'{str(x)} - {x.shop_score()}') for x in Player.objects.filter(game=most_recent_game()))

def get_users():
    return ((x.id, f'{x.get_full_name()} - {x.email}') for x in User.objects.filter(is_active=True))

def get_users_legacy():
    return ((x.id, f'{x.get_full_name()}, {x.email} - {x.legacy_points()}') for x in User.objects.filter(is_active=True))

def get_months():
    return ((i, date(2008, i, 1).strftime('%B')) for i in range(1,13))

def get_text(file):
    return ''.join(open(file,'r'))

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
        min_value=0,
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
    
class OZShuffleForm(forms.Form):
    amount = forms.IntegerField(
        label="Number of Random OZs",
        initial=Player.objects.filter(game=most_recent_game()).distinct().count()//10,
        min_value=0,
        max_value=Player.objects.filter(game=most_recent_game()).exclude(role=PlayerRole.ZOMBIE).distinct().count(),
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'input_type':'number'
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
    
    day = forms.IntegerField(
        label="Day",
        min_value=0,
        max_value=31,
        help_text=
        "Please don't try to be smart and enter a day that doesn't exist.",        
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'input_type':'number'
            }
        )
    )
    
    month = forms.ChoiceField(
        label="Month",
        choices=get_months,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        )
    )    
    
    year = forms.IntegerField(
        label="Year",
        min_value=1,
        max_value=9999,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'input_type':'number'
            }
        )
    )    
    
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
    
class AddLegacyForm(forms.Form):
    legacy_user = forms.ChoiceField(
        label="User to add Tokens to",
        choices=get_users_legacy,
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        )
    )
    legacy_details = forms.CharField(
        label="Token Info",
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': 'Leave a note of what this is for'
            }
        )
    )
    legacy_points = forms.IntegerField(
        label="Number of Tokens",
        initial=0,
        help_text=
        "This value can be positive or negative. A positive value indicates a gain of tokens, a negative value indicates a loss of tokens.\
        Users can never have a negative number of tokens. Necromancers will usually receive 2 for each game they run, and all others receive 1.",           
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'input_type':'number'
            }
        )
    )    
    
class SignupEmailForm(forms.Form):
    signup_email_html = forms.CharField(
        label="Signup Email - HTML",
        initial=get_text('/users/hvz/uwhvz/app/templates/jinja2/email/signup.html'),
        widget=forms.Textarea(
            attrs={
                'class': 'ui-input',
            }
        )
    )
    
    signup_email_txt = forms.CharField(
        label="Signup Email - txt",
        initial=get_text('/users/hvz/uwhvz/app/templates/jinja2/email/signup.txt'),
        widget=forms.Textarea(
            attrs={
                'class': 'ui-input',
            }
        )
    )    
    
class ReminderEmailForm(forms.Form):
    reminder_email_html = forms.CharField(
        label="Reminder Email - HTML",
        initial=get_text('/users/hvz/uwhvz/app/templates/jinja2/email/signup_reminder.html'),
        widget=forms.Textarea(
            attrs={
                'class': 'ui-input',
            }
        )
    )
    
    reminder_email_txt = forms.CharField(
        label="Reminder Email - txt",
        initial=get_text('/users/hvz/uwhvz/app/templates/jinja2/email/signup_reminder.txt'),
        widget=forms.Textarea(
            attrs={
                'class': 'ui-input',
            }
        )
    )

class StartEmailForm(forms.Form):
    start_email_html = forms.CharField(
        label="Game Start Email - HTML",
        initial=get_text('/users/hvz/uwhvz/app/templates/jinja2/email/game_start.html'),
        widget=forms.Textarea(
            attrs={
                'class': 'ui-input',
            }
        )
    )
    
    start_email_txt = forms.CharField(
        label="Game Start Email - txt",
        initial=get_text('/users/hvz/uwhvz/app/templates/jinja2/email/game_start.txt'),
        widget=forms.Textarea(
            attrs={
                'class': 'ui-input',
            }
        )
    )    