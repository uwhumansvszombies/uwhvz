from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, render
from django.views import View
from rest_framework.utils import json
from django.contrib.auth.models import Group
from django.contrib import messages

from app.util import MobileSupportedView, most_recent_game
from app.models import Game, Tag, Player, PlayerRole, SignupLocation, Legacy, SupplyCode


class IndexView(MobileSupportedView):
    desktop_template = "index.html"
    mobile_template = "mobile/index.html"

    def get(self, request):
        game = most_recent_game()
        signups = SignupLocation.objects.filter(game=game).exclude(name='Online')
        return self.mobile_or_desktop(request, {'game': game, 'signups':signups})


@method_decorator(login_required, name='dispatch')
class DashboardView(MobileSupportedView):
    desktop_template = "dashboard/index.html"
    mobile_template = "mobile/dashboard/index.html"   

    def get(self, request):
        game = most_recent_game()
        stuns = Tag.objects.filter(initiator__user=request.user,initiator__role=PlayerRole.HUMAN,
            receiver__role=PlayerRole.ZOMBIE,active=True).count()
        kills = Tag.objects.filter(initiator__user=request.user,initiator__role=PlayerRole.ZOMBIE,
            receiver__role=PlayerRole.HUMAN,active=True).count()
        codes = SupplyCode.objects.filter(claimed_by__user=request.user,active=True).count()
        
        points_accu = sum(Legacy.objects.filter(user=request.user,value__gt=0).values_list('value', flat=True))
        points_for_permanent = 8       
        if game.is_running and (request.user.is_superuser or request.user.participant(game).is_moderator):
            unverified = Tag.objects.filter(initiator__game=game,
                receiver__game=game,active=False).count()
            if unverified:
                messages.error(request, f"There are {unverified} tags that require verification")
        return self.mobile_or_desktop(request, {'game': game, 'participant': request.user.participant(game),
                                                'stuns':stuns, 'kills':kills, 'codes':codes,
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
            legacy_users.add(request.user)
            
        return redirect('dashboard')
    
    

class MissionsView(MobileSupportedView):
    desktop_template = "missions.html"
    mobile_template = "missions.html"

    def get(self, request):
        game = most_recent_game()
        return self.mobile_or_desktop(request, {'game': game})

class PrevGamesView(View):
    template_name = "previous_games.html"
    
    def render_zombie_tree(self, request, prev_games, game):

        player_codes = {}
        nodes = {}
        edges = []
        # Since we don't want repeated instances of OZs, we use a set instead of a list.
        ozs = set()

        tags = Tag.objects.filter(
            initiator__game=game,
            receiver__game=game,
            initiator__role=PlayerRole.ZOMBIE,
            receiver__role=PlayerRole.HUMAN,
            active=True)

        for tag in tags:
            edges.append({'from': tag.initiator.code, 'to': tag.receiver.code})

            player_codes[tag.initiator.code] = tag.initiator.user.get_full_name()
            player_codes[tag.receiver.code] = tag.receiver.user.get_full_name()

            if not Player.objects.filter(game=game,code=tag.initiator.code, role=PlayerRole.HUMAN).exists():
                ozs.add(tag.initiator)

        nodes['NECROMANCER'] = {'label': "Necromancer"}
        for oz in Player.objects.filter(game=game,in_oz_pool=True):
            if oz not in ozs:
                ozs.add(oz)
        for oz in ozs:
            edges.append({'from': 'NECROMANCER', 'to': oz.code})
            player_codes[oz.code] = oz.user.get_full_name()

        for code, name in player_codes.items():
            nodes[code] = {'label': name}
            
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
        
        return self.render_zombie_tree(request,prev_games,(game_selection)[1])
