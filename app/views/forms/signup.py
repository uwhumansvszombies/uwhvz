from django import forms


class UserSignupForm(forms.Form):
    first_name = forms.CharField(
        label="First name",
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input'
            }
        )
    )

    last_name = forms.CharField(
        label="Last name",
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input'
            }
        )
    )

    password1 = forms.CharField(
        label="Enter Password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'ui-input',
            }
        )
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'ui-input',
            }
        )
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "The passwords entered do not match.",
                code='passwords_do_not_match'
            )
        return password2


class UnrestrictedUserSignupForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                'class': 'ui-input'
            }
        )
    )

    first_name = forms.CharField(
        label="First name",
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input'
            }
        )
    )

    last_name = forms.CharField(
        label="Last name",
        widget=forms.TextInput(
            attrs={
                'class': 'ui-input'
            }
        )
    )

    password1 = forms.CharField(
        label="Enter Password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'ui-input',
            }
        )
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'ui-input',
            }
        )
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "The passwords entered do not match.",
                code='passwords_do_not_match'
            )
        return password2
