from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator

from app.models import Participant
from app.util import MobileSupportedView, game_exists, most_recent_game


class IndexView(MobileSupportedView):
    desktop_template = "index.html"
    mobile_template = "mobile/index.html"


@method_decorator(login_required, name='dispatch')
class DashboardView(MobileSupportedView):
    desktop_template = "dashboard/index.html"
    mobile_template = "mobile/dashboard/index.html"

    def get(self, request):
        if game_exists():
            game = most_recent_game()
            if game.is_active:
                if not Participant.objects.filter(game=game, user=request.user).exists():
                    game_signup_url = reverse('game_signup')
                    messages.warning(
                        request,
                        f"You haven't finished signing up for the {game} game. "
                        f"If you still wish to join, "
                        f"<a href=\"{game_signup_url}\">you can finish signing up here</a>."
                    )

            return self.mobile_or_desktop(request, {'game': game})
        return self.mobile_or_desktop(request)


@method_decorator(login_required, name='dispatch')
class SettingsView(MobileSupportedView):
    desktop_template = "dashboard/settings.html"
    mobile_template = "mobile/dashboard/settings.html"

    def get(self, request):
        return self.mobile_or_desktop(request)
