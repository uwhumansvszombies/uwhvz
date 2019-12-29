from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import Group

from app.mail import send_signup_email
from app.models import Player, SignupInvite, SignupLocation, SupplyCode, PlayerRole, Spectator, Moderator, Purchase, Game, User, Legacy
from app.util import moderator_required, most_recent_game, running_game_required, get_game_participants, necromancer_required
from app.views.forms import *

from datetime import datetime
from pytz import utc
from random import sample

def get_text(file):
    return ''.join(open(file,'r'))


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
        game_start_form = GameStartForm(request.POST)
        if not game_start_form.is_valid():
            messages.error(request, "There was an error with your request. Check your inputs again!")
            return redirect('manage_game')
        
        cd = game_start_form.cleaned_data
        game_title = cd['name']
        
        try:
            start_day = utc.localize(datetime(int(cd['year']), int(cd['month']),int(cd['day'])))
        except:
            messages.error(request, "That's not a valid day!")
            return redirect('manage_game')            
        Game.objects.create_game(name=game_title, started_on=start_day, started_by=request.user)
        
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

    def get(self, request, game_start_form = GameStartForm(), **kwargs):
        game = most_recent_game()
        participant = request.user.participant(game)
        message_players_form = kwargs.get('message_players_form', ModMessageForm())
        time_to_start = game.started_on - utc.localize(datetime.now())
        return render(request, self.template_name, {
            'game': game,
            'time_to_start':time_to_start,
            'participant':participant,
            'message_players_form': message_players_form,
            'game_start_form': game_start_form,
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

@method_decorator(moderator_required, name='dispatch')
class ManageOZView(View):
    template_name = "dashboard/moderator/manage_oz.html"

    def get(self, request, oz_shuffle_form=OZShuffleForm()):
        game = most_recent_game()
        players = Player.objects.filter(game=game, is_oz=True).exclude(role=PlayerRole.ZOMBIE).order_by('user__first_name')
        forced_oz = Player.objects.filter(game=game, role=PlayerRole.ZOMBIE).order_by('user__first_name')
        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'players': players,
            'forced_oz':forced_oz,
            'oz_shuffle_form':oz_shuffle_form,
        })
    
    def post(self, request):
        game = most_recent_game()
        if 'set_oz' in request.POST:
            for oz in Player.objects.filter(game=game, is_oz=True).exclude(role=PlayerRole.ZOMBIE).order_by('user__first_name'):
                oz.role=PlayerRole.ZOMBIE
                oz.save()
            return redirect('manage_oz')
        
        oz_shuffle_form = OZShuffleForm(request.POST)
        if not oz_shuffle_form.is_valid():
            return self.get(request, oz_shuffle_form=oz_shuffle_form)
        
        players = Player.objects.filter(game=game, in_oz_pool=True).exclude(role=PlayerRole.ZOMBIE).order_by('user__first_name')
        cd = oz_shuffle_form.cleaned_data
        
        to_make_ozs = sample(players,cd['amount'])
        
        for old_oz in Player.objects.filter(game=game, is_oz=True).exclude(role=PlayerRole.ZOMBIE).order_by('user__first_name'):
            old_oz.is_oz=False
            old_oz.save()
            
        for oz in to_make_ozs:
            oz.is_oz=True
            oz.save()
        
        messages.success(request, "Succesfully updated OZ list.")
        
        return redirect('manage_oz')

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
        return redirect('manage_staff')
    
@method_decorator(necromancer_required, name='dispatch')
class ManageLegacyView(View):
    template_name = "dashboard/moderator/manage_legacy.html"

    def render_manage_legacy(self, request, add_legacy_form=AddLegacyForm()):
        game = most_recent_game()
        
        all_legacies = []
        permanent_status = []
        points_for_permanent = 8
        token_transactions = Legacy.objects.all()
        
        for user in User.objects.all():
            if user.legacy_points():
                all_legacies.append(user)
                if sum(user.user_legacy().filter(value>0).values_list('value', flat=True)) >= points_for_permanent:
                    permanent_status.append(user)

        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'all_legacies': all_legacies,
            'permanent_status': permanent_status,
            'add_legacy_form': add_legacy_form,
            'token_transactions': token_transactions,
             })
    
    def get(self, request):
        return self.render_manage_legacy(request)

    def post(self, request):
        legacy_form = AddLegacyForm(request.POST)
        if not legacy_form.is_valid():
            return self.render_manage_legacy(request, add_legacy_form=add_legacy_form)
    
        game = most_recent_game()
        cleaned_data = legacy_form.cleaned_data
        legacy_points, legacy_user, legacy_details = int(cleaned_data['legacy_points']),\
            User.objects.get(id=cleaned_data['legacy_user']), cleaned_data['legacy_details']
        
        
        if legacy_points < 0 and -1*(legacy_points) > legacy_user.legacy_points():
            messages.error(request, f"{legacy_user} does not have {legacy_points} points available to spend!")
            return self.render_manage_legacy(request, add_legacy_form=AddLegacyForm())
        
        Legacy.objects.create_legacy(user=legacy_user,value=legacy_points,details=legacy_details)
        
        if legacy_points > 0:
            messages.success(request, f"Succesfully gave {legacy_points} tokens to {legacy_user.get_full_name()}.")
        else:
            messages.success(request, f"{legacy_user.get_full_name()} succesfully spent {abs(legacy_points)} tokens.")
        return redirect('manage_legacy')

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
        
        messages.success(request, f"Added volunteer {volunteer.get_full_name}")
        
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


@method_decorator(necromancer_required, name='dispatch')
class EmailTemplatesView(View):
    template_name = "dashboard/moderator/email_templates.html"

    def render_email_templates(self, request, signup_email_form=SignupEmailForm(initial=\
                {'signup_email_html':get_text('/users/hvz/uwhvz/app/templates/jinja2/email/signup.html'),\
                 'signup_email_txt':get_text('/users/hvz/uwhvz/app/templates/jinja2/email/signup.txt')}),\
                reminder_email_form=ReminderEmailForm(initial=\
                {'reminder_email_html':get_text('/users/hvz/uwhvz/app/templates/jinja2/email/signup_reminder.html'),\
                 'reminder_email_txt':get_text('/users/hvz/uwhvz/app/templates/jinja2/email/signup_reminder.txt')}),\
                start_email_form=StartEmailForm(initial=\
                {'start_email_html':get_text('/users/hvz/uwhvz/app/templates/jinja2/email/game_start.html'),\
                 'start_email_txt':get_text('/users/hvz/uwhvz/app/templates/jinja2/email/game_start.txt')})):
        
        game = most_recent_game()
        
        messages.success(request, get_text('/users/hvz/uwhvz/app/templates/jinja2/email/signup.txt'))
        
        
        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'signup_email_form': signup_email_form,
            'reminder_email_form':reminder_email_form,
            'start_email_form':start_email_form,
             })
        
    def get(self, request):
        return self.render_email_templates(request)
       

    def post(self, request):
        if "change_signup" in request.POST:
            signup_email_form = SignupEmailForm(request.POST)
            
            if not signup_email_form.is_valid():
                return self.render_email_templates(request, signup_email_form=signup_email_form)        
            cd = signup_email_form.cleaned_data
            
            try:
                f = open('/users/hvz/uwhvz/app/templates/jinja2/email/signup.html','w')
                f.write(cd['signup_email_html'])
                f.close()
                SignupEmailForm().fields['signup_email_html'].initial=cd['signup_email_html']
                f = open('/users/hvz/uwhvz/app/templates/jinja2/email/signup.txt','w')
                f.write(cd['signup_email_txt'])
                f.close()
                SignupEmailForm().fields['signup_email_txt'].initial=cd['signup_email_txt']
            except:
                messages.error(request, "There was an error updating the signup email.")
                return redirect('email_templates')            
            
            messages.success(request, "Succesfully updated signup email.")
            return self.render_email_templates(request, signup_email_form=signup_email_form)
        
        if "change_reminder" in request.POST:
            reminder_email_form=ReminderEmailForm(request.POST)
            
            if not reminder_email_form.is_valid():
                return self.render_email_templates(request, reminder_email_form=reminder_email_form)       
            cd = signup_email_form.cleaned_data
            
            try:
                f = open('/users/hvz/uwhvz/app/templates/jinja2/email/signup_reminder.html','w')
                f.write(cd['reminder_email_html'])
                f.close()
                ReminderEmailForm().fields['reminder_email_html'].initial=cd['reminder_email_html']
                f = open('/users/hvz/uwhvz/app/templates/jinja2/email/signup_reminder.txt','w')
                f.write(cd['reminder_email_txt'])
                f.close()
                ReminderEmailForm().fields['reminder_email_txt'].initial=cd['reminder_email_txt']
            except:
                messages.error(request, "There was an error updating the reminder email.")
                return redirect('email_templates')
            
            messages.success(request, "Succesfully updated reminder email.")
            return self.render_email_templates(request, reminder_email_form=reminder_email_form) 
        
        if "change_start" in request.POST:
            start_email_form=StartEmailForm(request.POST)
            
            if not start_email_form.is_valid():
                return self.render_email_templates(request, start_email_form=start_email_form) 
            cd = start_email_form.cleaned_data
            
            try:
                f = open('/users/hvz/uwhvz/app/templates/jinja2/email/game_start.html','w')
                f.write(cd['start_email_html'])
                f.close()
                StartEmailForm().fields['start_email_html'].initial=cd['start_email_html']
                f = open('/users/hvz/uwhvz/app/templates/jinja2/email/game_start.txt','w')
                f.write(cd['start_email_txt'])
                f.close()
                StartEmailForm().fields['start_email_txt'].initial=cd['start_email_txt']
            except:
                messages.error(request, "There was an error updating the game start email.")
                return redirect('email_templates')            
            
            messages.success(request, "Succesfully updated game start email.")
            return self.render_email_templates(request, start_email_form=start_email_form)            