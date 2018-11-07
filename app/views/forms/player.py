from django import forms


class ReportTagForm(forms.Form):
    player_code = forms.CharField(
        label="Other Player's Code",
        min_length=6,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': "e.g. A1B2C3"
            }
        )
    )
    datetime = forms.SplitDateTimeField(
        label="Date/Time",
        widget=forms.SplitDateTimeWidget(
            date_attrs={
                'class': 'ui-input',
                'type': 'date'
            },
            time_attrs={
                'class': 'ui-input',
                'type': 'time'
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
        min_length=6,
        max_length=6,
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
