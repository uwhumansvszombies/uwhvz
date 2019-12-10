from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import EmailMultiAlternatives

from app.mail import send_signup_email
from app.models import Player, SignupInvite, SignupLocation, SupplyCode, PlayerRole, Spectator, Moderator, Purchase
from app.util import moderator_required, most_recent_game, running_game_required, get_game_participants
from app.views.forms import ModeratorSignupPlayerForm, ModMessageForm, GenerateSupplyCodeForm, ShopForm


@method_decorator(moderator_required, name='dispatch')
class KillUnsuppliedHumansView(View):
    def get(self, request):
        return redirect('manage_game')

    def post(self, request):
        minimum_score_threshold = 5
        game = most_recent_game()
        human_players = Player.objects.filter(game=game, role=PlayerRole.HUMAN, active=True)

        for human in human_players:
            if human.score() < minimum_score_threshold:
                human.kill()

        return redirect('manage_game')


@method_decorator(moderator_required, name='dispatch')
class ManageGameView(View):
    template_name = "dashboard/moderator/manage_game.html"

    def get(self, request, **kwargs):
        game = most_recent_game()
        participant = request.user.participant(game)
        message_players_form = kwargs.get('message_players_form', ModMessageForm())
        return render(request, self.template_name, {
            'game': game,
            'participant':participant,
            'message_players_form': message_players_form,
        })
    
    def post(self, request):   
        game = most_recent_game()
        message_players_form = ModMessageForm(request.POST)
        if not message_players_form.is_valid():
            return self.get(request, message_players_form=message_players_form)

        cd = message_players_form.cleaned_data
        recipients = []
        subject_set = '[hvz-all]'
        if cd['recipients'] == "All":
            recipients = list(Player.objects \
                .filter(game=game, active=True) \
                .values_list('user__email', flat=True))
        elif cd['recipients'] == "Zombies":
            recipients = list(Player.objects \
                .filter(game=game, active=True, role=PlayerRole.ZOMBIE) \
                .values_list('user__email', flat=True))
            subject_set = '[hvz-zombies]'
        elif cd['recipients'] == "Humans":
            recipients = list(Player.objects \
                .filter(game=game, active=True, role=PlayerRole.HUMAN) \
                .values_list('user__email', flat=True))    
            subject_set = '[hvz-humans]'
            
        recipients.extend(list(Moderator.objects \
                .filter(game=game, active=True) \
                .values_list('user__email', flat=True)))
        
        recipients.extend(list(Spectator.objects \
                .filter(game=game, active=True) \
                .values_list('user__email', flat=True)))        

        EmailMultiAlternatives(
            subject=f"{subject_set} {cd['subject']}",
            body=cd['message'],
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[],
            bcc=recipients
        ).send()

        if cd['recipients'] == "All":
            messages.success(request, "You've sent an email to all players.")
        elif cd['recipients'] == "Zombies":
            messages.success(request, "You've sent an email to all zombies.")
        elif cd['recipients'] == "Humans":
            messages.success(request, "You've sent an email to all humans.")
        return redirect('manage_game')        
    
    #participants = get_game_participants(game)
    #spectators = Spectator.objects.filter(game=game)
    #moderators = Moderator.objects.filter(game=game)
    #humans = Player.objects.filter(game=game, active=True, role=PlayerRole.HUMAN)
    #zombies = Player.objects.filter(game=game, active=True, role=PlayerRole.ZOMBIE)

    #all_emails = [p.user.email for p in participants]
    #spectator_emails = [s.user.email for s in spectators]
    #moderator_emails = [m.user.email for m in moderators]
    #human_emails = [h.user.email for h in humans] + spectator_emails + moderator_emails
    #zombie_emails = [z.user.email for z in zombies] + spectator_emails + moderator_emails    



@method_decorator(moderator_required, name='dispatch')
class ManageOZView(View):
    template_name = "dashboard/moderator/manage_oz.html"

    def get(self, request):
        game = most_recent_game()
        players = Player.objects.filter(game=game, in_oz_pool=True).order_by('user__first_name')
        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'players': players,
        })


@method_decorator(moderator_required, name='dispatch')
class ManagePlayersView(View):
    template_name = "dashboard/moderator/manage_players.html"

    def render_manage_players(self, request, mod_signup_player_form=ModeratorSignupPlayerForm()):
        game = most_recent_game()
        participants = get_game_participants(game).order_by('user__first_name')
        locations = SignupLocation.objects.filter(game=game)

        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'participants': participants,
            'signup_locations': locations,
            'mod_signup_player_form': mod_signup_player_form,
        })

    def get(self, request):
        return self.render_manage_players(request)

    def post(self, request):
        mod_signup_player_form = ModeratorSignupPlayerForm(request.POST)
        if not mod_signup_player_form.is_valid():
            return self.render_manage_players(request, mod_signup_player_form=mod_signup_player_form)

        game = most_recent_game()
        cleaned_data = mod_signup_player_form.cleaned_data
        location, email, participant_role = cleaned_data['location'], cleaned_data['email'], cleaned_data[
            'participant_role']

        signup_invite = SignupInvite.objects.create_signup_invite(game, location, email, participant_role)
        send_signup_email(request, signup_invite, game)
        messages.success(request, f"Sent a signup email to {email}.")
        return redirect('manage_players')


@method_decorator(moderator_required, name='dispatch')
@method_decorator(running_game_required, name='dispatch')
class GenerateSupplyCodesView(View):
    template_name = "dashboard/moderator/generate_supply_codes.html"

    def get(self, request, **kwargs):
        game = most_recent_game()
        supply_codes = SupplyCode.objects.filter(game=game, active=True)
        make_codes_form = kwargs.get('make_codes_form', GenerateSupplyCodeForm())
        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'supply_codes': supply_codes,
            'make_codes_form': make_codes_form,
        })

    def post(self, request):
        make_codes_form = GenerateSupplyCodeForm(request.POST)
        if not make_codes_form.is_valid():
            return self.get(request, make_codes_form=make_codes_form)        
        cd = make_codes_form.cleaned_data
        
        game = most_recent_game()
        supply_code = SupplyCode.objects.create_supply_code(game, cd['value'], cd['code'])
        messages.success(request, f"Generated new supply code \"{supply_code}\".")
        return redirect('generate_supply_codes')

@method_decorator(moderator_required, name='dispatch')
@method_decorator(running_game_required, name='dispatch')
class ManageShopView(View):
    template_name = "dashboard/moderator/manage_shop.html"

    def get(self, request, **kwargs):
        game = most_recent_game()
        all_sales = Purchase.objects.filter(game=game, active=True)
        make_sale_form = kwargs.get('make_sale_form', ShopForm())
        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'all_sales': all_sales,
            'make_sale_form': make_sale_form,
        })

    def post(self, request):
        make_sale_form = ShopForm(request.POST)
        if not make_sale_form.is_valid():
            return self.get(request, make_sale_form=make_sale_form)        
        cd = make_sale_form.cleaned_data
        
        game = most_recent_game()
        supply_code = Purchase.objects.create_purchase(cd['buyer'], cd['cost'], game)
        messages.success(request, f"Succesfully sold to\"{buyer}\".")
        return redirect('manage_shop')
