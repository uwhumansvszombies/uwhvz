from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from app.mail import send_signup_email
from app.models import Player, SignupLocation, User, SupplyCode, PlayerRole
from app.util import moderator_required, require_post_parameters, most_recent_game


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
    template_name = 'dashboard/moderator/manage_players.html'

    def get(self, request):
        players = Player.objects.filter(active=True).all()
        locations = SignupLocation.objects.all()
        game = most_recent_game()
        return render(request, self.template_name, {
            'game': game,
            'players': players,
            'signup_locations': locations,
        })

    def post(self, request):
        location_id, email = require_post_parameters(request, 'signup_location', 'email')
        if User.objects.filter(email=email).exists():
            messages.warning(request, f'There is already an account associated with: {email}.')
            return redirect('manage_players')

        location = SignupLocation.objects.get(pk=location_id)
        game = most_recent_game()
        send_signup_email(request, game, location, email)
        messages.success(request, f'Sent an email to: {email}.')
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
        messages.success(request, f'Generated new code: {supply_code}.')
        return redirect('generate_supply_codes')
