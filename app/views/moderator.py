from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from app.mail import send_signup_email
from app.models import Player, SignupInvite, SignupLocation, User, SupplyCode, PlayerRole
from app.util import moderator_required, most_recent_game
from app.views.forms import ModeratorSignupPlayerForm


@method_decorator(moderator_required, name='dispatch')
class ManageGameView(View):
    template_name = 'dashboard/moderator/manage_game.html'

    def get(self, request):
        players = Player.objects.filter(active=True)
        all_emails = [p.user.email for p in players.all()]
        human_emails = [p.user.email for p in players.filter(role=PlayerRole.HUMAN).all()]
        zombie_emails = [p.user.email for p in players.filter(role=PlayerRole.ZOMBIE).all()]

        game = most_recent_game()
        return render(request, self.template_name, {
            'game': game,
            'all_emails': all_emails,
            'human_emails': human_emails,
            'zombie_emails': zombie_emails,
        })


@method_decorator(moderator_required, name='dispatch')
class ManageOZView(View):
    template_name = 'dashboard/moderator/manage_oz.html'

    def get(self, request):
        game = most_recent_game()
        players = Player.objects.filter(in_oz_pool=True)
        return render(request, self.template_name, {
            'game': game,
            'players': players
        })


@method_decorator(moderator_required, name='dispatch')
class ManagePlayersView(View):
    def render_manage_players(self, request, mod_signup_player_form=ModeratorSignupPlayerForm()):
        template = 'dashboard/moderator/manage_players.html'

        game = most_recent_game()
        players = Player.objects.filter(active=True).all()
        locations = SignupLocation.objects.all()

        return render(request, template, {
            'game': game,
            'signup_locations': locations,
            'mod_signup_player_form': mod_signup_player_form
        })

    def get(self, request):
        return self.render_manage_players(request)

    def post(self, request):
        mod_signup_player_form = ModeratorSignupPlayerForm(request.POST)
        if not mod_signup_player_form.is_valid():
            return self.render_manage_players(request, mod_signup_player_form=mod_signup_player_form)

        game = most_recent_game()
        cleaned_data = mod_signup_player_form.cleaned_data
        location, email, player_role = cleaned_data['location'], cleaned_data['email'], cleaned_data['player_role']

        if User.objects.filter(email=email).exists():
            messages.warning(request, f'There is already an account associated with: {email}.')
            return redirect('manage_players')

        signup_invite = SignupInvite.objects.create_signup_invite(game, location, email, player_role)
        send_signup_email(request, signup_invite)
        messages.success(request, f'Sent a signup email to {email}.')
        return redirect('manage_players')


@method_decorator(moderator_required, name='dispatch')
class GenerateSupplyCodesView(View):
    template_name = 'dashboard/moderator/generate_supply_codes.html'

    def get(self, request):
        supply_codes = SupplyCode.objects.all()
        game = most_recent_game()
        return render(request, self.template_name, {
            'game': game,
            'supply_codes': supply_codes
        })

    def post(self, request):
        game = most_recent_game()
        supply_code = SupplyCode.objects.create_supply_code(game)
        messages.success(request, f'Generated new supply code "{supply_code}".')
        return redirect('generate_supply_codes')
