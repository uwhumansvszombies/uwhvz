from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import Group

from app.mail import send_signup_email
from app.models import Player, SignupInvite, SignupLocation, SupplyCode, PlayerRole, Spectator, Moderator, Purchase, Game, User
from app.util import moderator_required, most_recent_game, running_game_required, get_game_participants, necromancer_required
from app.views.forms import *

from datetime import datetime
from pytz import utc


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
class GameStartView(View):
    def get(self, request):
        return redirect('manage_game')

    def post(self, request):
        form = GameStartForm(request.POST)
        if not form.is_valid():
            messages.error(request, "There was an error with your request")
            return redirect('manage_game')
        
        cd = form.cleaned_data
        game_title = cd['name']
        Game.objects.create_game(name=game_title, started_on=cd['start_time'], started_by=request.user)
        
        game=most_recent_game()
        
        if not 'Online' in list(SignupLocation.objects.filter(game=game).values_list('name', flat=True)):
            SignupLocation.objects.create_signup_location('Online', game)
            
        messages.success(request, f"The Game \"{game_title}\" is open for signups.")
        return redirect('manage_game')
    
@method_decorator(moderator_required, name='dispatch')
class GameSetView(View):
    def get(self, request):
        return redirect('manage_game')

    def post(self, request):
        game = most_recent_game()
        try:
            game.started_on = utc.localize(datetime.now())
            game.save()
        
            messages.success(request, f"The Game \"{game.name}\" has started.")
            return redirect('manage_game')
        except:
            messages.error(request, f"There was an error with the starting of the game \"{game.name}\"")
            return redirect('manage_game')
        
@method_decorator(moderator_required, name='dispatch')
class GameEndView(View):
    def get(self, request):
        return redirect('manage_game')

    def post(self, request):
        game = most_recent_game()
        try:
            game.ended_on = utc.localize(datetime.now())
            game.ended_by = request.user
            game.save()
            messages.success(request, f"The Game \"{game.name}\" has ended.")
            return redirect('manage_game')
        except:
            messages.error(request, f"There was an error with the ending of the game \"{game.name}\"")
            return redirect('manage_game')  
    

@method_decorator(moderator_required, name='dispatch')
class ManageGameView(View):
    template_name = "dashboard/moderator/manage_game.html"

    def get(self, request, form = GameStartForm(), **kwargs):
        game = most_recent_game()
        participant = request.user.participant(game)
        message_players_form = kwargs.get('message_players_form', ModMessageForm())
        time_to_start = game.started_on - utc.localize(datetime.now())
        return render(request, self.template_name, {
            'game': game,
            'time_to_start':time_to_start,
            'participant':participant,
            'message_players_form': message_players_form,
            'form': form,
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
            
        elif cd['recipients'] == "Volunteers":
            recipients = list(User.objects \
                .filter(game=game, active=True, groups__name="Volunteer") \
                .values_list('user__email', flat=True))    
            subject_set = '[hvz-volunteers]'        
            
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
class AddSignupView(View):
    def get(self, request):
        return redirect('manage_players')

    def post(self, request):
        game = most_recent_game()
        signup_loc_form = AddSignupForm(request.POST)
        if not signup_loc_form.is_valid():
            return redirect('manage_players')
        
        cd = signup_loc_form.cleaned_data
        loc = cd['location']
        if loc in list(SignupLocation.objects.filter(game=game).values_list('name', flat=True)):
            messages.error(request, "That location already exists")
            return redirect('manage_players')
        
        SignupLocation.objects.create_signup_location(loc, game)
        
        messages.success(request, f"Added signup location {loc}")
        
        return redirect('manage_players')



@method_decorator(necromancer_required, name='dispatch')
class ManageStaffView(View):
    template_name = "dashboard/moderator/manage_staff.html"

    def render_manage_staff(self, request, add_mod_form=AddModForm(), add_volunteer_form=AddVolunteerForm()):
        game = most_recent_game()
        all_mods = Moderator.objects.filter(game=game)
        all_volunteers = User.objects.filter(groups__name="Volunteers")

        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'all_mods':all_mods,
            'all_volunteers':all_volunteers,
            'add_mod_form': add_mod_form,
            'add_volunteer_form': add_volunteer_form,
             })
        
    def get(self, request):
        return self.render_manage_staff(request)
       

    def post(self, request):
        #legacy_form = LegacyForm(request.POST)
        #if not legacy_form.is_valid():
            #return self.render_manage_players(request, legacy_form=LegacyForm())

        #game = most_recent_game()
        #cleaned_data = legacy_form.cleaned_data
        #legacy_points, legacy_user, legacy_details = cleaned_data['legacy_points'],\
            #cleaned_data['legacy_user'], cleaned_data['legacy_details']
        
        ## This will be used to implement the legacy object
        #messages.success(request, f"Succesfully gave {legacy_points} legacy points to {legacy_user}.")
        return redirect('manage_staff')

@method_decorator(necromancer_required, name='dispatch')    
class ManageModsView(View):
    def get(self, request):
        return redirect('manage_staff')

    def post(self, request):
        game = most_recent_game()
        add_mod_form = AddModForm(request.POST)
        if not add_mod_form.is_valid():
            return redirect('manage_staff')
        
        cd = add_mod_form.cleaned_data
        mod_id = cd['mod']
        if mod_id in list(Moderator.objects.filter(game=game).values_list('id', flat=True)):
            messages.error(request, "That mod already exists in this game")
            return redirect('manage_staff')
        
        mod = User.objects.get(id=mod_id)
        
        Moderator.objects.create_moderator(user=mod, game=game)
        
        messages.success(request, f"Added mod {mod.get_full_name()}")
        
        return redirect('manage_staff')

@method_decorator(necromancer_required, name='dispatch')    
class ManageVolunteersView(View):
    def get(self, request):
        return redirect('manage_staff')

    def post(self, request):
        game = most_recent_game()
        add_volunteer_form=AddVolunteerForm(request.POST)
        if not add_volunteer_form.is_valid():
            return redirect('manage_staff')
        
        cd = add_volunteer_form.cleaned_data
        vol_id = cd['volunteer']
        if vol_id in list(User.objects.filter(groups__name="Volunteers").values_list('id', flat=True)):
            messages.error(request, "That volunteer already exists")
            return redirect('manage_staff')
        
        volunteer = User.objects.get(id=vol_id, game=game)
        vol_group = Group.objects.get(name='Volunteer')
        vol_group.user_set.add(volunteer)
        vol_group.save()
        
        messages.success(request, f"Added signup location {volunteer.get_full_name}")
        
        return redirect('manage_staff')




@method_decorator(moderator_required, name='dispatch')
class ManagePlayersView(View):
    template_name = "dashboard/moderator/manage_players.html"

    def render_manage_players(self, request, mod_signup_player_form=ModeratorSignupPlayerForm(), signup_loc_form=AddSignupForm()):
        game = most_recent_game()
        participants = get_game_participants(game).order_by('user__first_name')
        locations = SignupLocation.objects.filter(game=game)

        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'participants': participants,
            'signup_locations': locations,
            'mod_signup_player_form': mod_signup_player_form,
            'signup_loc_form': signup_loc_form,
        })

    def get(self, request):
        return self.render_manage_players(request)

    def post(self, request, **kwargs):
        signup_loc_form = kwargs.get('signup_loc_form', AddSignupForm())
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
        buyer = Player.objects.get(id=cd['buyer'],game=game)
        
        if buyer.shop_score() < int(cd['cost']):
            messages.error(request, f"{buyer} does not have enough points for this purchase!")
            return redirect('manage_shop')
        
        supply_code = Purchase.objects.create_purchase(buyer=buyer, cost=int(cd['cost']), details=cd['purchase'], game=game)
        messages.success(request, f"Succesfully sold {cd['purchase']} to {buyer}.")
        return redirect('manage_shop')
