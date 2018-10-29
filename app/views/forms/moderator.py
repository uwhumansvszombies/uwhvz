from django import forms
from enumfields import EnumField

from app.models import PlayerRole, SignupLocation
from app.util import most_recent_game


def get_signup_locations():
    return ((x.id, x) for x in SignupLocation.objects.filter(game=most_recent_game()).all())


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

    player_role = EnumField(PlayerRole, max_length=1).formfield(
        required=False,
        help_text=
        'Hint: If the player role is blank and the game is running, the player will NOT be able to sign up for the game. '
        'However, if this is blank and the game is in signup mode, the player will sign up normally.',
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        ),
    )

    def clean_location(self):
        data = self.cleaned_data['location']
        return SignupLocation.objects.get(pk=data)
