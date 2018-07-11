from django import forms

from app.models import SignupLocation


class VolunteerSignupPlayerForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                'class': 'ui-input'
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
