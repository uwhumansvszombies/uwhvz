from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from django.views import View
from rest_framework.utils import json
from django.contrib.auth.models import Group
from django.contrib import messages
from time import mktime
from datetime import datetime
import pytz

from app.util import MobileSupportedView, most_recent_game
from app.models import Game, Tag, Player, PlayerRole, SignupLocation, Legacy, SupplyCode, User, TagType, Email, RecipientGroup
from app.views.forms import ChangeCodeForm

class IndexView(MobileSupportedView):
    desktop_template = "index.html"
    mobile_template = "mobile/index.html"

    def get(self, request):
        game = most_recent_game()
        signups = SignupLocation.objects.filter(game=game).exclude(name='Online')
        if game.started_on:
            for_js = int(mktime(game.started_on.timetuple())) * 1000
        else:
            for_js = int(mktime(datetime.utcnow().timetuple())) * 1000
        return self.mobile_or_desktop(request, {'game': game, 'signups':signups, 'for_js':for_js})


@method_decorator(login_required, name='dispatch')
class DashboardView(MobileSupportedView):
    desktop_template = "dashboard/index.html"
    mobile_template = "mobile/dashboard/index.html"

    def get(self, request, change_code_form=ChangeCodeForm()):
        game = most_recent_game()
        participant = request.user.participant(game)
        stuns = Tag.objects.filter(initiator__user=request.user,type=TagType.STUN,active=True).count()
        kills = Tag.objects.filter(initiator__user=request.user,type=TagType.KILL,active=True).count()
        codes = SupplyCode.objects.filter(claimed_by__user=request.user,active=True).count()

        emails = Email.objects.filter(game=game,visible=True)
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

        points_accu = sum(Legacy.objects.filter(user=request.user,value__gt=0).values_list('value', flat=True))
        # Only spot this variable exists/is used
        points_for_permanent = 6
        if game.is_running and (request.user.is_superuser or (request.user.participant(game) and request.user.participant(game).is_moderator)):
            unverified = Tag.objects.filter(initiator__game=game,
                receiver__game=game,active=False).count()
            if unverified:
                messages.error(request, f"There are {unverified} tags that require verification")
        return self.mobile_or_desktop(request, {'game': game, 'participant': participant, 'change_code_form': change_code_form,
                                                'stuns':stuns, 'kills':kills, 'codes':codes, 'emails':emails.order_by("-created_at") if emails else None, 'pytz':pytz,
                                                'points_accu':points_accu, 'points_for_permanent':points_for_permanent})

    def post(self, request):
        game = most_recent_game()

        if "pts" in request.POST:
            player = request.user.participant(game)
            player.point_modifier = 15
            player.save()
            Legacy.objects.create_legacy(user=request.user,value=-1,details=f'Started {game} game with 15 points.')
            messages.success(request, "You will now start the game with 15 points.")

        elif "oz" in request.POST:
            player = request.user.participant(game)
            player.is_oz = True
            player.save()
            Legacy.objects.create_legacy(user=request.user,value=-1,details=f'Started {game} game as OZ.')
            messages.success(request, "You will now start the game as OZ.")

        legacy_users = Group.objects.get(name='LegacyUsers')
        if request.user.id not in list(User.objects.filter(groups__name="LegacyUsers").values_list('id', flat=True)):
            legacy_users.user_set.add(request.user)

        return redirect('dashboard')



class MissionsView(MobileSupportedView):
    desktop_template = "missions.html"
    mobile_template = "missions.html"    

    def get(self, request):
        game = most_recent_game()
        return self.mobile_or_desktop(request, {'game': game})

class MinecraftView(MobileSupportedView):
    desktop_template = "minecraft.html"
    mobile_template = "minecraft.html"

    def get(self, request):
        game = most_recent_game()
        return self.mobile_or_desktop(request, {'game': game})
    
class NewPlayerGuideView(MobileSupportedView):
    desktop_template = "new_player_guide.html"
    mobile_template = "new_player_guide.html"    

    def get(self, request):
        game = most_recent_game()
        return self.mobile_or_desktop(request, {'game': game})

class PrevGamesView(View):
    template_name = "previous_games.html"

    def render_zombie_tree(self, request, prev_games, game):

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
            edges.append({'from': tag.initiator.code, 'to': tag.receiver.code})
            tag_descs[tag.receiver.code] = desc

            player_codes[tag.initiator.code] = tag.initiator.user.get_full_name()
            player_codes[tag.receiver.code] = tag.receiver.user.get_full_name()

        nodes['NECROMANCER'] = {'label': "Necromancer",'title':"Necromancer"}
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
                    #nodes[code]['title'] = '<span style="display: -webkit-box;word-wrap:break-word;word-break: break-all;overflow-x: auto;">' + ''.join(to_write) + '</span>'
                else:
                    nodes[code]['title'] = ':/'

        # BFS on the edge list so that we can put each node into a group based on
        # its level in the tree.
        # This is perhaps the only time you will see a practical use of BFS
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
            'game_rendering': game,
            'prev_games':prev_games,
            'nodes': json.dumps(node_list),
            'edges': json.dumps(edges),
        })

    def get(self, request):
        prev_games = Game.objects.filter(include_summary=True)

        return self.render_zombie_tree(request,prev_games,prev_games.order_by('-created_at').first())

    def post(self, request):
        prev_games = Game.objects.filter(include_summary=True)
        game_selection = prev_games.order_by('-created_at').first()
        for game in prev_games:
            if game.name in request.POST:
                game_selection = game

        return self.render_zombie_tree(request,prev_games,game_selection)
