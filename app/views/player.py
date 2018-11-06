from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.utils import json

from app.mail import send_tag_email, send_stun_email
from app.models import Player, PlayerRole, Tag, SupplyCode, Modifier, ModifierType
from app.util import most_recent_game, game_required, running_game_required, player_required, get_game_participants
from app.views.forms import ReportTagForm, ClaimSupplyCodeForm, MessagePlayersForm


def render_player_info(request, **kwargs):
    template_name = "mobile/dashboard/player.html" if request.user_agent.is_mobile else "dashboard/player.html"

    game = most_recent_game()
    try:
        player = request.user.participant(game)
    except ObjectDoesNotExist:
        return redirect('dashboard')
    team_score = sum([p.score() for p in Player.objects.filter(role=player.role).all()])

    report_tag_form = kwargs.get('report_tag_form', ReportTagForm())
    claim_supply_code_form = kwargs.get('claim_supply_code_form', ClaimSupplyCodeForm())
    message_players_form = kwargs.get('message_players_form', MessagePlayersForm(player=player))
    return render(request, template_name, {
        'game': game,
        'player': player,
        'team_score': team_score,
        'report_tag_form': report_tag_form,
        'claim_supply_code_form': claim_supply_code_form,
        'message_players_form': message_players_form,
    })


@method_decorator(login_required, name='dispatch')
@method_decorator(game_required, name='dispatch')
class PlayerInfoView(View):
    def get(self, request):
        game = most_recent_game()
        if not game.is_running or not request.user.participant(game).is_player:
            return redirect('dashboard')
        else:
            return render_player_info(request)


@method_decorator(running_game_required, name='dispatch')
@method_decorator(player_required, name='dispatch')
class ReportTagView(View):
    def get(self, request):
        return redirect('player_info')

    def post(self, request):
        report_tag_form = ReportTagForm(request.POST)
        if not report_tag_form.is_valid():
            return render_player_info(request, report_tag_form=report_tag_form)

        game = most_recent_game()
        initiating_player = request.user.participant(game)

        cleaned_data = report_tag_form.cleaned_data
        receiver_code = cleaned_data['player_code'].upper()

        try:
            receiving_player = Player.objects.get(code=receiver_code, active=True)
        except ObjectDoesNotExist:
            report_tag_form.add_error('player_code', "No player with that code exists.")
            return render_player_info(request, report_tag_form=report_tag_form)

        tag_modifier_amount = 0
        try:
            tag_modifier = Modifier.objects.get(faction=initiating_player.faction, modifier_type=ModifierType.TAG)
            tag_modifier_amount = tag_modifier.modifier_amount
        except ObjectDoesNotExist:
            pass

        try:
            tag = Tag.objects.create_tag(initiating_player, receiving_player, cleaned_data['datetime'],
                                         cleaned_data['location'], cleaned_data['description'], tag_modifier_amount)
        except ValueError as err:
            messages.error(request, err)
            return redirect('player_info')

        if initiating_player.is_human:
            send_stun_email(request, tag)
            messages.success(request,
                             f"You've successfully submitted a stun on {receiving_player.user.get_full_name()}.")
        else:
            send_tag_email(request, tag)
            messages.success(request,
                             f"You've successfully submitted a tag on {receiving_player.user.get_full_name()}.")
        return redirect('player_info')


@method_decorator(running_game_required, name='dispatch')
@method_decorator(player_required, name='dispatch')
class ClaimSupplyCodeView(View):
    def get(self, request):
        return redirect('player_info')

    def post(self, request):
        claim_supply_code_form = ClaimSupplyCodeForm(request.POST)
        if not claim_supply_code_form.is_valid():
            return render_player_info(request, claim_supply_code_form=claim_supply_code_form)

        game = most_recent_game()
        player = request.user.participant(game)

        cleaned_data = claim_supply_code_form.cleaned_data
        cleaned_supply_code = cleaned_data['code'].upper()
        try:
            supply_code = SupplyCode.objects.get(game=game, code=cleaned_supply_code, claimed_by__isnull=True,
                                                 active=True)
        except ObjectDoesNotExist:
            claim_supply_code_form.add_error('code', "That supply code does not exist or has already been redeemed.")
            return render_player_info(request, claim_supply_code_form=claim_supply_code_form)

        if not player.is_human:
            messages.error(request, "Only humans can redeem supply codes.")
            return redirect('player_info')

        supply_code_modifier_amount = 0
        try:
            supply_code_modifier = Modifier.objects.get(faction=player.faction, modifier_type=ModifierType.SUPPLY_CODE)
            supply_code_modifier_amount = supply_code_modifier.modifier_amount
        except ObjectDoesNotExist:
            pass

        supply_code.claim(player, supply_code_modifier_amount)
        messages.success(request, "The code has been redeemed successfully.")
        return redirect('player_info')


@method_decorator(player_required, name='dispatch')
@method_decorator(running_game_required, name='dispatch')
class MessagePlayersView(View):
    def get(self, request):
        return redirect('player_info')

    def post(self, request):
        game = most_recent_game()
        player = request.user.player(game)

        message_players_form = MessagePlayersForm(request.POST, player=player)
        if not message_players_form.is_valid():
            return render_player_info(request, message_players_form=message_players_form)

        cd = message_players_form.cleaned_data
        recipients = []
        if cd.recipients == "All":
            recipients = Player.objects. \
                filter(game=game, active=True). \
                values_list('email', flat=True)
        elif cd.recipients == "Zombies":
            if not player.is_zombie:
                messages.error(request, "Only zombies can email only zombies.")
                return redirect('player_info')
            recipients = Player.objects. \
                filter(game=game, active=True, role=PlayerRole.ZOMBIE). \
                values_list('email', flat=True)

        send_mail(
            subject=f"Message from {request.user.get_full_name()}",
            message=cd.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients
        )

        messages.success(request, "You messaged the players successfully")
        return redirect('player_info')


@method_decorator(login_required, name='dispatch')
@method_decorator(running_game_required, name='dispatch')
class PlayerListView(View):
    template_name = 'dashboard/player_list.html'

    def get(self, request):
        game = most_recent_game()

        try:
            participant = request.user.participant(game)
        except ObjectDoesNotExist:
            return redirect('dashboard')

        participants = get_game_participants(game).order_by('user__first_name')

        return render(request, self.template_name, {
            'game': game,
            'participant': participant,
            'participants': participants
        })


@method_decorator(login_required, name='dispatch')
@method_decorator(game_required, name='dispatch')
class ZombieTreeView(View):
    template_name = 'dashboard/zombie_tree.html'

    def get(self, request):
        game = most_recent_game()

        try:
            participant = request.user.participant(game)
        except ObjectDoesNotExist:
            return redirect('dashboard')

        if game.is_running and participant.is_player and participant.is_human and not \
            (participant.is_moderator or participant.is_spectator or participant.user.is_staff):
            raise PermissionDenied

        player_codes = {}
        nodes = []
        edges = []
        # Since we don't want repeated instances of OZs, we use a set instead of a list.
        ozs = set()

        tags = Tag.objects.filter(initiator__role=PlayerRole.ZOMBIE, receiver__role=PlayerRole.HUMAN, active=True)

        for tag in tags:
            edges.append({'from': tag.initiator.code, 'to': tag.receiver.code})

            player_codes[tag.initiator.code] = tag.initiator.user.get_full_name()
            player_codes[tag.receiver.code] = tag.receiver.user.get_full_name()

            if not Player.objects.filter(game=game, code=tag.initiator.code, role=PlayerRole.HUMAN).exists():
                ozs.add(tag.initiator)

        for code, name in player_codes.items():
            nodes.append({'id': code, 'label': name})

        nodes.append({'id': 'NECROMANCER', 'label': "Necromancer"})
        for oz in ozs:
            edges.append({'from': 'NECROMANCER', 'to': oz.code})

        return render(request, self.template_name, {
            'game': game,
            'participant': participant,
            'nodes': json.dumps(nodes),
            'edges': json.dumps(edges),
        })
