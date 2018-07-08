from django import forms


class ReportTagForm(forms.Form):
    player_code = forms.CharField(
        label="Other Player's Code",
        min_length=6,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input',
                'placeholder': 'e.g. A1B2C3'
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
                'placeholder': 'e.g. RCH, DC Green'
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
                'placeholder': 'Tell us how you tagged the player!'
            }
        )
    )
