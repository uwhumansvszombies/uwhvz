from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from app.util import MobileSupportedView, most_recent_game


class IndexView(MobileSupportedView):
    desktop_template = "index.html"
    mobile_template = "mobile/index.html"

    def get(self, request):
        game = most_recent_game()
        return self.mobile_or_desktop(request, {'game': game})


@method_decorator(login_required, name='dispatch')
class DashboardView(MobileSupportedView):
    desktop_template = "dashboard/index.html"
    mobile_template = "mobile/dashboard/index.html"

    def get(self, request):
        game = most_recent_game()
        return self.mobile_or_desktop(request, {'game': game, 'participant': request.user.participant(game)})

class MissionsView(MobileSupportedView):
    desktop_template = "missions.html"
    mobile_template = "missions.html"

    def get(self, request):
        game = most_recent_game()
        return self.mobile_or_desktop(request, {'game': game})
