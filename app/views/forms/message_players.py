from django import forms


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
                'rows': '5',
                'placeholder': 'Your message'
            }
        )
    )
