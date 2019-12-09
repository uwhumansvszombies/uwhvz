from django import forms
from enumfields import EnumField

from app.models import ParticipantRole, SignupLocation
from app.util import most_recent_game


def get_signup_locations():
    return ((x.id, x) for x in SignupLocation.objects.filter(game=most_recent_game()))


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
        choices=[("All", "All"), ("Humans", "Humans"), ("Zombies", "Zombies")],
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
        label="SupplyCode",
        min_length=6,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': 'e.g. A1B2C3'
            }
        )
    )
    value = forms.CharField(
        label="Value",
        initial=5,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'input_type':'number'
            }
        )
    )    