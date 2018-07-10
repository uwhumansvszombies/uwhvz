from django import forms
from enumfields import EnumField

from app.models import PlayerRole, SignupLocation


class ModeratorSignupPlayerForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                'class': 'ui-input',
            }
        )
    )

    location = forms.ModelChoiceField(
        label="Signup Location",
        empty_label=None,
        queryset=SignupLocation.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        )
    )

    player_role = EnumField(PlayerRole, max_length=1).formfield(
        required=False,
        help_text=
        'If the game is running and this is blank, the player won\'t be able to sign up for the game.'
        'However, if the game is in signup mode, the player will sign up as normal.',
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
            }
        ),
    )
