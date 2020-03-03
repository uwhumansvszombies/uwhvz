from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import Group

from app.mail import send_signup_email, send_signup_reminder, send_start_email
from app.models import Player, SignupInvite, SignupLocation, SupplyCode, PlayerRole, Spectator, Moderator, Purchase, Game, User, Legacy, Tag, Faction, Modifier
from app.util import moderator_required, most_recent_game, running_game_required, get_game_participants, necromancer_required
from app.views.forms import *

from datetime import datetime
from pytz import utc, timezone
from random import sample

def get_text(file):
    x = open(file,'r')
    s = ''.join(x)
    x.close()
    return s


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

        volunteers = Group.objects.get(name='Volunteer').item_set.all()
        for volunteer in volunteers:
            if volunteer.email != 'volunteer@email.com':
                volunteer.groups.remove("Volunteer")

        legacy_users = Group.objects.get(name='LegacyUsers').item_set.all()
        for user in legacy_users:
            user.groups.remove("LegacyUsers")

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

        elif cd['recipients'] == "Volunteers and Legacy":
            recipients = list(User.objects \
                .filter(game=game, active=True, groups__name="Volunteer") \
                .values_list('user__email', flat=True))
            recipients.extend(list(User.objects \
                .filter(game=game, active=True, groups__name="LegacyUsers") \
                .values_list('user__email', flat=True)))
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
        max_value = Player.objects.filter(game=most_recent_game()).exclude(role=PlayerRole.ZOMBIE).distinct().count()
        return render(request, self.template_name, {
            'game': game,
            'total_players': max_value,
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

        to_make_ozs = sample(set(players),cd['amount'])

        for old_oz in Player.objects.filter(game=game, is_oz=True).exclude(role=PlayerRole.ZOMBIE).order_by('user__first_name'):
            old_oz.is_oz=False
            old_oz.save()

        for oz in to_make_ozs:
            oz.is_oz=True
            oz.save()

        messages.success(request, "Succesfully updated OZ list.")

        return redirect('manage_oz')

@method_decorator(moderator_required, name='dispatch')
class ManageSignupView(View):
    def get(self, request):
        return redirect('manage_players')

    def post(self, request):
        game = most_recent_game()

        locations = SignupLocation.objects.filter(game=game)
        for location in locations:
            if str(location.id)+'-remove' in request.POST:
                location.delete()
                messages.success(request, f"Deleted signup location {location}")
                return redirect('manage_players')

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

@method_decorator(moderator_required, name='dispatch')
class StunVerificationView(View):
    template_name = "dashboard/moderator/stun_verification.html"

    def render_stun_verification(self, request):
        game = most_recent_game()
        unverified_stuns = Tag.objects.filter(
            initiator__game=game,
            receiver__game=game,
            active=False)
        tz = timezone('Canada/Eastern')

        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'unverified_stuns': unverified_stuns,
            'tz':tz,
             })

    def get(self, request):
        return self.render_stun_verification(request)

    def post(self, request):
        game = most_recent_game()
        unverified_stuns = Tag.objects.filter(
            initiator__game=game,
            receiver__game=game,
            active=False)

        for tag in unverified_stuns:
            if str(tag.id)+'-activate' in request.POST:
                tag.active = True
                tag.save()
                messages.success(request, f"Succesfully approved tag {tag}")
                return redirect('stun_verification')
            if str(tag.id)+'-remove' in request.POST:
                messages.success(request, f"Deleted tag {tag}")
                tag.delete()
                return redirect('stun_verification')

        messages.error(request, "Tag ID not found")

        return redirect('stun_verification')


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
        token_transactions = Legacy.objects.all().order_by('user__first_name')

        for user in User.objects.all():
            if user.legacy_points():
                all_legacies.append(user)
                if sum(Legacy.objects.filter(user=user,value__gt=0).values_list('value', flat=True)) >= points_for_permanent:
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
            return self.render_manage_legacy(request, add_legacy_form=legacy_form)

        game = most_recent_game()
        cleaned_data = legacy_form.cleaned_data
        legacy_points, legacy_user, legacy_details = int(cleaned_data['legacy_points']),\
            User.objects.get(id=cleaned_data['legacy_user']), cleaned_data['legacy_details']


        if legacy_points < 0 and -1*(legacy_points) > legacy_user.legacy_points():
            messages.error(request, f"{legacy_user} does not have {legacy_points} points available to spend!")
            return self.render_manage_legacy(request, add_legacy_form=legacy_form)

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

        volunteer = User.objects.get(id=vol_id)
        vol_group = Group.objects.get(name='Volunteers')
        vol_group.user_set.add(volunteer)
        vol_group.save()

        messages.success(request, f"Added volunteer {volunteer.get_full_name()}")

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

    def render_email_templates(self, request):
        game = most_recent_game()

        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'signup_email_form': SignupEmailForm(initial={'signup_email_html': get_text('app/templates/jinja2/email/signup.html'),
                                                          'signup_email_txt': get_text('app/templates/jinja2/email/signup.txt') }),
            'reminder_email_form':ReminderEmailForm(initial={'reminder_email_html':get_text('app/templates/jinja2/email/signup_reminder.html'),
                                                             'reminder_email_txt':get_text('app/templates/jinja2/email/signup_reminder.txt')}),
            'start_email_form':StartEmailForm(initial={'start_email_html':get_text('app/templates/jinja2/email/game_start.html'),
                                                       'start_email_txt':get_text('app/templates/jinja2/email/game_start.txt')})
        })

    def get(self, request):
        return self.render_email_templates(request)


    def post(self, request):
        game = most_recent_game()

        if "change_signup" in request.POST:
            signup_email_form = SignupEmailForm(request.POST)

            if not signup_email_form.is_valid():
                return self.render_email_templates(request)
            cd = signup_email_form.cleaned_data

            try:
                f = open('app/templates/jinja2/email/signup.html','w')
                f.write(cd['signup_email_html'])
                f.close()
                SignupEmailForm().fields['signup_email_html'].initial = cd['signup_email_html']
                f = open('app/templates/jinja2/email/signup.txt','w')
                f.write(cd['signup_email_txt'])
                f.close()
                SignupEmailForm().fields['signup_email_txt'].initial=cd['signup_email_txt']
            except:
                messages.error(request, "There was an error updating the signup email.")
                return redirect('email_templates')

            messages.success(request, "Succesfully updated signup email.")
            return self.render_email_templates(request)

        if "change_reminder" in request.POST:
            reminder_email_form=ReminderEmailForm(request.POST)

            if not reminder_email_form.is_valid():
                return self.render_email_templates(request)
            cd = reminder_email_form.cleaned_data

            try:
                f = open('app/templates/jinja2/email/signup_reminder.html','w')
                f.write(cd['reminder_email_html'])
                f.close()
                ReminderEmailForm().fields['reminder_email_html'].initial=cd['reminder_email_html']
                f = open('app/templates/jinja2/email/signup_reminder.txt','w')
                f.write(cd['reminder_email_txt'])
                f.close()
                ReminderEmailForm().fields['reminder_email_txt'].initial=cd['reminder_email_txt']
            except:
                messages.error(request, "There was an error updating the reminder email.")
                return redirect('email_templates')

            messages.success(request, "Succesfully updated reminder email.")
            return self.render_email_templates(request)

        if "change_start" in request.POST:
            start_email_form=StartEmailForm(request.POST)

            if not start_email_form.is_valid():
                return self.render_email_templates(request)
            cd = start_email_form.cleaned_data

            try:
                f = open('app/templates/jinja2/email/game_start.html','w')
                f.write(cd['start_email_html'])
                f.close()
                StartEmailForm().fields['start_email_html'].initial=cd['start_email_html']
                f = open('app/templates/jinja2/email/game_start.txt','w')
                f.write(cd['start_email_txt'])
                f.close()
                StartEmailForm().fields['start_email_txt'].initial=cd['start_email_txt']
            except:
                messages.error(request, "There was an error updating the game start email.")
                return redirect('email_templates')

            messages.success(request, "Succesfully updated game start email.")
            return self.render_email_templates(request)

        if 'test_start' in request.POST:
            send_start_email(request, request.user.participant(game), game)
            messages.success(request, f"Game Start email sent to {request.user.email}.")
        if 'send_reminder' in request.POST:
            for invite in SignupInvite.objects.filter(game=game,used_at__isnull=True):
                send_signup_reminder(request, invite, game)
            messages.success(request, f"Reminder emails sent to {SignupInvite.objects.filter(game=game,used_at__isnull=True).count()} people.")
        if 'send_start' in request.POST:
            recipients = Player.objects.filter(game=game, active=True)
            for parti in recipients:
                send_start_email(request, parti, game)

            recipients = Moderator.objects.filter(game=game, active=True)
            for parti in recipients:
                send_start_email(request, parti, game)

            recipients = Spectator.objects.filter(game=game, active=True)
            for parti in recipients:
                send_start_email(request, parti, game)
            messages.success(request, f"Game start emails sent to {Player.objects.filter(game=game, active=True).count()} players,\
            {Moderator.objects.filter(game=game, active=True).count()} mods, and {Spectator.objects.filter(game=game, active=True).count()} spectators.")
        return self.render_email_templates(request)


@method_decorator(moderator_required, name='dispatch')
class DeleteFactionsView(View):
    def get(self, request):
        return redirect('manage_factions')

    def post(self, request):
        game = most_recent_game()
        modifiers = Modifier.objects.all()

        for modifier in modifiers:
            if str(modifier.id) + "-remove" in request.POST:
                modifier_count = modifier.faction.modifier_set.count()

                if modifier_count > 1:
                    modifier.delete()
                    messages.success(request, f"Successfully deleted modifier {modifier}.")
                    break

                if modifier.faction.player_set.count() == 0:
                    modifier.delete()
                    modifier.faction.delete()
                    messages.success(request, f"Successfully deleted faction {modifier.faction}.")
                else:
                    messages.error(request, f"Failed to delete modifier and faction {modifier.faction} since players are still a part of it.")

        return redirect('manage_factions')

@method_decorator(moderator_required, name='dispatch')
class ManageFactionsView(View):
    template_name = "dashboard/moderator/manage_factions.html"

    def render_manage_factions(self, request, mod_add_player_to_faction_form=AddPlayerToFactionForm(),
                               mod_add_faction_form=AddFactionForm(), mod_add_modifier_form=AddModifierForm()):
        game = most_recent_game()
        human_players = Player.objects.filter(game=game, role=PlayerRole.HUMAN, active=True).order_by('user__first_name')
        factions = Faction.objects.filter(game=game)
        modifiers = map(lambda f: f.modifier_set.all(), factions)
        return render(request, self.template_name, {
            'game': game,
            'participant': request.user.participant(game),
            'humans': human_players,
            'factions': zip(factions, modifiers),
            'mod_add_player_to_faction_form': mod_add_player_to_faction_form,
            'mod_add_faction_form': mod_add_faction_form,
            'mod_add_modifier_form': mod_add_modifier_form
        })

    def get(self, request):
        return self.render_manage_factions(request)

    def post(self, request, **kwargs):
        game = most_recent_game()
        if 'add-faction' in request.POST:
            mod_add_faction_form = AddFactionForm(request.POST)
            if not mod_add_faction_form.is_valid():
                return self.render_manage_factions(request, mod_add_faction_form=mod_add_faction_form)

            cleaned_data = mod_add_faction_form.cleaned_data
            name, description, modifier_type, amount = cleaned_data['name'], cleaned_data['description'], cleaned_data['modifier_type'], cleaned_data['amount']
            # update if possible
            try:
                faction = Faction.objects.get(game=game, name=name)
                faction.description = description
                faction.save()

                messages.success(request, f"Updated faction successfully.")
                return redirect ('manage_factions')
            # the .get() function throws an error if faction/modifier not found, so we catch it here
            except (Faction.DoesNotExist, Modifier.DoesNotExist):
                pass

            # else create
            try: 
                faction = Faction.objects.create_faction(game, name, description)
                if modifier_type and amount:
                    Modifier.objects.create_modifier(faction, modifier_type, amount)
                messages.success(request, f"Created faction successfully.")
            except:
                messages.error(request, f"There was an error in creating the faction.")
        elif 'add-player-to-faction' in request.POST:
            mod_add_player_to_faction_form = AddPlayerToFactionForm(request.POST)
            if not mod_add_player_to_faction_form.is_valid():
                return self.render_manage_factions(request, mod_add_player_to_faction_form=mod_add_player_to_faction_form)

            cleaned_data = mod_add_player_to_faction_form.cleaned_data
            player, faction = cleaned_data['player'], cleaned_data['faction']


            try:
                player_object = Player.objects.get(id=player, game=game)
                # for clearing a player's faction
                if (faction == ''):
                    player_object.faction = None
                    player_object.save()
                    messages.success(request, f"Updated player faction successfully.")
                else:
                    faction_object = Faction.objects.get(id=faction, game=game)
                    player_object.faction = faction_object
                    player_object.save()
                    messages.success(request, f"Updated player faction successfully.")
            except:
                messages.error(request, f"There was an error in setting the players faction.")
        elif 'add-modifier' in request.POST:
            mod_add_modifier_form = AddModifierForm(request.POST)
            if not mod_add_modifier_form.is_valid():
                return self.render_manage_factions(request, mod_add_modifier_form=mod_add_modifier_form)

            cleaned_data = mod_add_modifier_form.cleaned_data
            faction, modifier_type, amount = cleaned_data['faction'], cleaned_data['modifier_type'], cleaned_data['amount']
            try: 
                faction_object = Faction.objects.get(id=faction, game=game)
                Modifier.objects.create_modifier(faction_object, modifier_type, amount)
                messages.success(request, f"Created modifier successfully.")
            except Exception as e:
                print(e)
                messages.error(request, f"Failed to create modifier.")

        return redirect('manage_factions')

