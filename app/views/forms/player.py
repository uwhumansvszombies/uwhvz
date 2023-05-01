from django import forms
from datetime import datetime
from pytz import timezone


class ChangeCodeForm(forms.Form):
    code = forms.CharField(
        label="Change Code",
        min_length=2,
        max_length=9,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': 'e.g. A1B2C3'
            }
        )
    )


class ReportTagForm(forms.Form):
    player_code = forms.CharField(
        label="Other Player's Code (normally 6 characters)",
        min_length=2,
        max_length=9,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': "e.g. A1B2C3"
            }
        )
    )
    now = datetime.now().replace(tzinfo=timezone('Canada/Eastern'))
    datetime = forms.SplitDateTimeField(
        label="Date/Time",
        widget=forms.SplitDateTimeWidget(
            date_attrs={
                'class': 'ui-input',
                'type': 'date',
                'placeholder': "{}".format(now.strftime("%Y-%m-%d"))
            },
            time_attrs={
                'class': 'ui-input',
                'type': 'time',
                'placeholder': "{}".format(now.strftime("%H:%M"))
            }
        )
    )
    location = forms.CharField(
        label="Location (optional)",
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': "e.g. RCH, DC Green"
            }
        )
    )
    description = forms.CharField(
        label="Description (optional)",
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'ui-input',
                'rows': '5',
                'placeholder': "Tell us how you tagged the player!"
            }
        )
    )


class ClaimSupplyCodeForm(forms.Form):
    code = forms.CharField(
        label="Supply Code",
        min_length=1,
        max_length=9,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': 'e.g. A1B2C3'
            }
        )
    )


class MessagePlayersForm(forms.Form):
    def __init__(self, *args, **kwargs):
        player = kwargs.pop('player')
        super().__init__(*args, **kwargs)
        if player.is_human:
            self.fields['recipients'].choices = [("All", "All")]
        else:
            self.fields['recipients'].choices = [("All", "All"), ("Zombies", "Zombies")]

    recipients = forms.ChoiceField(
        label="Recipients",
        choices=[("All", "All"), ("Zombies", "Zombies")],
        widget=forms.Select(
            attrs={
                'class': 'custom-select',
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
