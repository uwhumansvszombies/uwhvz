from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.utils import json

from app.mail import send_tag_email, send_stun_email
from app.models import Player, PlayerRole, Tag, SupplyCode, Modifier, ModifierType, Spectator, Moderator, TagType, Email, RecipientGroup
from app.util import most_recent_game, running_game_required, player_required, get_game_participants, game_required, \
    participant_required
from app.views.forms import ReportTagForm, ClaimSupplyCodeForm, MessagePlayersForm, ChangeCodeForm
from string import ascii_letters, digits
from re import search

from pytz import timezone, utc
import pytz
from datetime import datetime

import io
from django.http import FileResponse
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from pdfrw import PdfReader, PdfWriter, PageMerge

pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))


def render_player_info(request, change_code_form = ChangeCodeForm(), report_tag_form=ReportTagForm(), claim_supply_code_form=ClaimSupplyCodeForm()):
    template_name = "mobile/dashboard/player.html" if request.user_agent.is_mobile else "dashboard/player.html"

    game = most_recent_game()
    participant = request.user.participant(game)
    team_score = sum([p.score() for p in Player.objects.filter(game=game, role=participant.role)])
   
    emails = Email.objects.filter(game=game)#.exclude(group=RecipientGroup.HUMAN)
    if participant and participant.is_player:
        if participant.is_human:
            emails = emails.exclude(group=RecipientGroup.ZOMBIE)
        elif participant.is_zombie:
            emails = emails.exclude(group=RecipientGroup.HUMAN)
        elif participant:
            emails = Email.objects.filter(game=game)
        else:
            emails = None
    if emails:
        emails.order_by("-created_at")
        if not request.user.groups.filter(name='LegacyUsers').exists() and not request.user.groups.filter(name='Volunteers').exists():
            emails = emails.exclude(group=RecipientGroup.VOLUNTEER)
    return render(request, template_name, {
        'game': game,
        'emails': emails,
        'pytz': pytz,
        'participant': participant,
        'team_score': team_score,
        'change_code_form': change_code_form,
        'report_tag_form': report_tag_form,
        'claim_supply_code_form': claim_supply_code_form,
    })

@method_decorator(game_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class PlayerCodeView(View):
    def get(self, request):
        watermark = "app/static/files/cardunderlay.pdf"
        player = request.user.participant(most_recent_game())
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()
    
        # Create the PDF object, using the buffer as its "file."
        p = SimpleDocTemplate(buffer, topMargin=70,bottomMargin=0)
        width, height = letter # Save these for later
    
        elements = []
        data=[(player.code,)*2]*7
        table = Table(data, colWidths=270, rowHeights=105)
        table.setStyle(TableStyle([('FACE',(0,0),(7,7),'VeraBd'),
                                   ('SIZE',(0,0),(7,7),45),
                                   ('TOPPADDING',(0,0),(7,7),15),
                                   ('BOTTOMPADDING',(0,0),(7,7),15),
                                   ('ALIGN',(0,0),(7,7),'CENTER'),
                                   ('VALIGN',(0,0),(7,7),'MIDDLE')]))
        
        elements.append(table)
        p.build(elements)            
        
        wmark = PageMerge().add(PdfReader(watermark).pages[0])[0]
        buffer.seek(0)
        trailer = PdfReader(buffer)
        buffer.close()
        for page in trailer.pages:
            PageMerge(page).add(wmark, prepend=True).render()
        
        buffer = io.BytesIO()
        PdfWriter(buffer, trailer=trailer).write()
        buffer.seek(0)
        # Close the PDF object cleanly, and we're done.
        #If this was on a client instead of server, we wouldn't use a buffer.
        #p.showPage()
        #p.save()
    
        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        return FileResponse(buffer, filename=f'{request.user.first_name}_code.pdf')


@method_decorator(game_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class PlayerInfoView(View):
    def get(self, request):
        # While it would be nice to use running_game_required and player_required
        # due to the fact that we redirect here from login for all users we must
        # account for spectators/moderators and when the game isn't running as well.
        game = most_recent_game()
        if not game.is_running or not request.user.participant(game) or not request.user.participant(game).is_player:
            return redirect('dashboard')
        return render_player_info(request)

    def post(self, request):
        is_score_public = request.POST.get('is_score_public', 'off') == 'on'
        player = request.user.participant(most_recent_game())
        player.is_score_public = is_score_public
        player.save()
        messages.success(request, f"Your score is now {'public' if is_score_public else 'private'}.")
        return render_player_info(request)


@method_decorator(game_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ChangeCodeView(View):
    def get(self, request):
        return redirect('dashboard')
    
    def post(self, request):
        change_code_form = ChangeCodeForm(request.POST)
        if not change_code_form.is_valid():
            messages.error(request, "Codes must be between 2 and 9 characters.")
            return redirect('dashboard') 
        cleaned_data = change_code_form.cleaned_data
        game = most_recent_game()
        if Player.objects.filter(game=game,code=cleaned_data['code']).exists():
            messages.error(request, "That code is already in use.")
            return redirect('dashboard')
        if search("[^a-zA-Z0-9]",cleaned_data['code']):
            messages.error(request, "Your code must be alphanumeric.")
            return redirect('dashboard')
        player = request.user.participant(game)
        player.code = cleaned_data['code']
        player.save()
        messages.success(request,f"You have successfully changed your code to {cleaned_data['code']}")
        return redirect('dashboard')


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
        
        if cleaned_data['datetime'].replace(tzinfo=timezone('Canada/Eastern')) > datetime.utcnow().replace(tzinfo=timezone('Canada/Eastern')):
            report_tag_form.add_error('datetime', "You can't tag someone in the future!")
            return render_player_info(request, report_tag_form=report_tag_form)            

        try:
            receiving_player = Player.objects.get(code=receiver_code, game=game, active=True)
        except ObjectDoesNotExist:
            report_tag_form.add_error('player_code', "No player with that code exists.")
            return render_player_info(request, report_tag_form=report_tag_form)

        tag_modifier_amount = 0
        try:
            if initiating_player.is_human:
                tag_modifier = Modifier.objects.get(faction=initiating_player.faction, modifier_type=ModifierType.TAG)
                tag_modifier_amount = tag_modifier.modifier_amount
        except ObjectDoesNotExist:
            pass

        if Tag.objects.filter(initiator=initiating_player, receiver=receiving_player,
                              tagged_at=cleaned_data['datetime'].replace(tzinfo=timezone('Canada/Eastern')), location=cleaned_data['location'],
                              description=cleaned_data['description']).exists():
            return redirect('player_info')

        try:
            tag = Tag.objects.create_tag(initiating_player, receiving_player, cleaned_data['datetime'].replace(tzinfo=timezone('Canada/Eastern')),
                                         cleaned_data['location'], cleaned_data['description'], tag_modifier_amount)
            tag.active = False
            tag.save()
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


@method_decorator(running_game_required, name='dispatch')
@method_decorator(participant_required, name='dispatch')
class PlayerListView(View):
    template_name = 'dashboard/player_list.html'

    def get(self, request):
        game = most_recent_game()
        participant = request.user.participant(game)
        participants = get_game_participants(game).order_by('user__first_name')
        moderators = Moderator.objects.filter(game=game, active=True)

        return render(request, self.template_name, {
            'game': game,
            'participant': participant,
            'participants': participants,
            'moderators': moderators,
        })

@method_decorator(running_game_required, name='dispatch')
@method_decorator(participant_required, name='dispatch')
class PlayerTagView(View):
    template_name = 'dashboard/view_tags.html'

    def get(self, request):
        game = most_recent_game()
        participant = request.user.participant(game)
        tz = timezone('Canada/Eastern')

        unverified_tags = Tag.objects.filter(
            initiator=participant,
            initiator__game=game,
            receiver__game=game,
            active=False)

        verified_tags = Tag.objects.filter(
            initiator=participant,
            initiator__game=game,
            receiver__game=game,
            active=True)

        received_tags = Tag.objects.filter(
            receiver=participant,
            initiator__game=game,
            receiver__game=game,
            type=TagType.STUN,
            #initiator__role=PlayerRole.HUMAN,
            #receiver__role=PlayerRole.ZOMBIE
            )


        type = "Stun" if participant.is_human else "Tag"

        return render(request, self.template_name, {
            'game': game,
            'participant': participant,
            'type': type,
            'unverified_tags': unverified_tags,
            'verified_tags': verified_tags,
            'received_tags': received_tags,
            'tz':tz,
        })


@method_decorator(running_game_required, name='dispatch')
@method_decorator(player_required, name='dispatch')
class MessagePlayersView(View):
    template_name = 'dashboard/message_players.html'

    def get(self, request, **kwargs):
        game = most_recent_game()
        participant = request.user.participant(game)
        message_players_form = kwargs.get('message_players_form', MessagePlayersForm(player=participant))

        return render(request, self.template_name, {
            'game': game,
            'participant': participant,
            'message_players_form': message_players_form,
        })

    def post(self, request):
        game = most_recent_game()
        participant = request.user.participant(game)
        message_players_form = MessagePlayersForm(request.POST, player=participant)
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
            if not participant.is_zombie:
                messages.error(request, "Only zombies can email only zombies.")
                return redirect('message_players')
            subject_set = '[hvz-zombies]'
            recipients = list(Player.objects \
                .filter(game=game, active=True, role=PlayerRole.ZOMBIE) \
                .values_list('user__email', flat=True))

        recipients.extend(list(Moderator.objects \
                .filter(game=game, active=True) \
                .values_list('user__email', flat=True)))

        recipients.extend(list(Spectator.objects \
                .filter(game=game, active=True) \
                .values_list('user__email', flat=True)))

        # Gmail has a limit of 100 recipients at a time.
        # Hence we send multiple emails, in batches of 100.
        for i in range(0, len(recipients), 100):
            msg = EmailMultiAlternatives(
                subject=f"{subject_set} Message from {request.user.get_full_name()}",
                body=cd['message'],
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[],
                bcc=recipients[i:i + 100]
            )

            print(msg)
            try:
                msg.send()
            except SMTPException as e:
                messages.error('There was an error sending an email: ', e)

        #EmailMultiAlternatives(
        #    subject=f"{subject_set} Message from {request.user.get_full_name()}",
        #    body=cd['message'],
        #    from_email=settings.DEFAULT_FROM_EMAIL,
        #    to=[],
        #    bcc=recipients
        #).send()

        if cd['recipients'] == "All":
            email = Email.objects.create_email(f"{subject_set} Message from {request.user.get_full_name()}",cd['message'],RecipientGroup.ALL,game,player_made=True)
            messages.success(request, "You've sent an email to all players.")
        elif cd['recipients'] == "Zombies":
            email = Email.objects.create_email(f"{subject_set} Message from {request.user.get_full_name()}",cd['message'],RecipientGroup.ZOMBIE,game,player_made=True)
            messages.success(request, "You've sent an email to all zombies.")
        return redirect('message_players')


# Zombie Tree Re-Written by Tristan Ohlson :)
@method_decorator(login_required, name='dispatch')
@method_decorator(game_required, name='dispatch')
class ZombieTreeView(View):
    template_name = 'dashboard/zombie_tree.html'

    def get(self, request):
        game = most_recent_game()

        try:
            player = request.user.participant(game)
        except ObjectDoesNotExist:
            return redirect('dashboard')

        if game.is_running and not player.is_spectator and not player.is_moderator and player.is_human:
            raise PermissionDenied

        player_codes = {}
        nodes = {}
        edges = []
        tag_descs = {}
        # Since we don't want repeated instances of OZs, we use a set instead of a list.
        ozs = set()

        tags = Tag.objects.filter(
            initiator__game=game,
            receiver__game=game,
            type=TagType.KILL,
            active=True)

        for tag in tags:
            if tag.location:
                desc = tag.location
                if tag.description:
                    desc = desc + ': ' + tag.description
            else:
                desc = tag.description
            edges.append({'from': tag.initiator.code, 'to': tag.receiver.code,}) # 'title': desc}) #This is from when edges used to hold descriptions
            tag_descs[tag.receiver.code] = desc
            
            player_codes[tag.initiator.code] = tag.initiator.user.get_full_name()
            player_codes[tag.receiver.code] = tag.receiver.user.get_full_name()

            #if not Player.objects.filter(game=game,code=tag.initiator.code, role=PlayerRole.HUMAN).exists():
            #    ozs.add(tag.initiator)

        nodes['NECROMANCER'] = {'label': "Necromancer",'title':"The original OZ"}
        for oz in Player.objects.filter(game=game,is_oz=True):
            if oz not in ozs:
                ozs.add(oz)
        
        oz_codes = []
        for oz in ozs:
            edges.append({'from': 'NECROMANCER', 'to': oz.code})
            player_codes[oz.code] = oz.user.get_full_name()
            oz_codes.append(oz.code)
        
        for code, name in player_codes.items():
            nodes[code] = {'label': name}
            if code in oz_codes:
                nodes[code]['title'] = 'OZ'
            if code in tag_descs:
                desc = tag_descs[code]
                if desc.strip():
                    desc = desc.split()
                    desc.reverse()
                    to_write = ['']
                    while desc:
                        curr_len = len(to_write[-1])
                        next_word = desc.pop()
                        if curr_len + len(next_word) <= 100:
                            to_write[-1] += ' ' + next_word
                        else:
                            to_write[-1] += "</br>"
                            to_write.append(next_word)
                    nodes[code]['title'] = ''.join(to_write)
                else:
                    nodes[code]['title'] = ':/'

        # BFS on the edge list so that we can put each node into a group based on
        # its level in the tree.
        queue = ['NECROMANCER']
        level = 0
        while queue:
            popped = []
            while queue:
                node_id = queue.pop(0)
                popped.append(node_id)
                nodes[node_id]['group'] = level

            children = []
            while popped:
                node_id = popped.pop(0)
                children.extend([n['to'] for n in edges if n['from'] == node_id])

            queue.extend(children)
            level += 1

        node_list = []
        for key, value in nodes.items():
            node_list.append({'id': key, **value})

        return render(request, self.template_name, {
            'game': game,
            'player': player,
            'participant': request.user.participant(game),
            'nodes': json.dumps(node_list),
            'edges': json.dumps(edges),
        })
