from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from app.mail import send_tag_email, send_stun_email
from app.models import Player, Tag, SupplyCode, Modifier, ModifierType
from app.util import most_recent_game, game_required, running_game_required
from app.views.forms import ReportTagForm, ClaimSupplyCodeForm


def render_player_info(request, report_tag_form=ReportTagForm(),
                       claim_supply_code_form=ClaimSupplyCodeForm()):
    template_name = 'mobile/dashboard/player.html' if request.user_agent.is_mobile else 'dashboard/player.html'

    game = most_recent_game()
    try:
        player = request.user.player_set.get(game=game, active=True)
    except ObjectDoesNotExist:
        return redirect('dashboard')
    team_score = sum([p.score() for p in Player.objects.filter(role=player.role).all()])
    return render(request, template_name, {
        'game': game,
        'player': player,
        'team_score': team_score,
        'report_tag_form': report_tag_form,
        'claim_supply_code_form': claim_supply_code_form,
    })


@method_decorator(login_required, name='dispatch')
@method_decorator(game_required, name='dispatch')
class PlayerInfoView(View):
    def get(self, request):
        game = most_recent_game()
        if not game.is_running:
            return redirect('dashboard')
        else:
            return render_player_info(request)


@method_decorator(login_required, name='dispatch')
@method_decorator(running_game_required, name='dispatch')
class ReportTagView(View):
    def get(self, request):
        return redirect('player_info')

    def post(self, request):
        report_tag_form = ReportTagForm(request.POST)
        if not report_tag_form.is_valid():
            return render_player_info(request, report_tag_form=report_tag_form)

        game = most_recent_game()
        initiating_player = request.user.player(game)
        cleaned_data = report_tag_form.cleaned_data
        try:
            receiving_player = Player.objects.get(code=cleaned_data['player_code'], active=True)
        except ObjectDoesNotExist:
            report_tag_form.add_error('player_code', 'No player with that code exists.')
            return render_player_info(request, report_tag_form=report_tag_form)

        modifier_amount = 0
        try:
            modifier = Modifier.objects.get(faction=initiating_player.faction, modifier_type=ModifierType.TAG)
            modifier_amount = modifier.modifier_amount
        except ObjectDoesNotExist:
            pass

        tag = Tag.objects.create_tag(initiating_player, receiving_player, cleaned_data['datetime'],
                                     cleaned_data['location'], cleaned_data['description'], modifier_amount)
        if receiving_player.is_human:
            send_tag_email(request, tag)
            messages.info(request, f'You\'ve reported a tag on {receiving_player.user.get_full_name()}.')
        else:
            send_stun_email(request, tag)
            messages.info(request, f'You\'ve reported a stun on {receiving_player.user.get_full_name()}.')
        return redirect('player_info')


@method_decorator(login_required, name='dispatch')
@method_decorator(running_game_required, name='dispatch')
class ClaimSupplyCodeView(View):
    def get(self, request):
        return redirect('player_info')

    def post(self, request):
        claim_supply_code_form = ClaimSupplyCodeForm(request.POST)
        if not claim_supply_code_form.is_valid():
            return render_player_info(request, claim_supply_code_form=claim_supply_code_form)

        game = most_recent_game()
        player = request.user.player(game)
        cleaned_data = claim_supply_code_form.cleaned_data
        try:
            supply_code = SupplyCode.objects.get(code=cleaned_data['code'], claimed_by__isnull=True)
        except ObjectDoesNotExist:
            claim_supply_code_form.add_error('code', "That supply code does not exist or has already been redeemed.")
            return render_player_info(request, claim_supply_code_form=claim_supply_code_form)

        if not player.is_human:
            messages.error(request, "Only humans can redeem supply codes.")
            return redirect('player_info')

        modifier_amount = 0
        try:
            modifier = Modifier.objects.get(faction=player.faction, modifier_type=ModifierType.SUPPLY_CODE)
            modifier_amount = modifier.modifier_amount
        except ObjectDoesNotExist:
            pass

        supply_code.claim(player, modifier_amount)
        messages.success(request, 'The code has been redeemed successfully.')
        return redirect('player_info')


@method_decorator(login_required, name='dispatch')
@method_decorator(running_game_required, name='dispatch')
class PlayerListView(View):
    template_name = 'dashboard/player_list.html'

    def get(self, request):
        players = Player.objects.filter(active=True).all()
        game = most_recent_game()
        return render(request, self.template_name, {
            'game': game,
            'player': request.user.player(game),
            'players': players
        })
