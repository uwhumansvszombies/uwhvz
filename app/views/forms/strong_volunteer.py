from django import forms

from app.util import most_recent_game


class StrongVolunteerSignupPlayerForm(forms.Form):
    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input'
            }
        )
    )

    last_name = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input'
            }
        )
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                'class': 'ui-input'
            }
        )
    )

    def clean_location(self):
        data = self.cleaned_data['location']
        return SignupLocation.objects.get(pk=data)
