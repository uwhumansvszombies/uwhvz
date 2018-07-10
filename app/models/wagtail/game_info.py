from enumfields import EnumField, Enum
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page

from app.models import Player
from app.util import most_recent_game


class ViewableBy(Enum):
    ALL = 'A'
    HUMANS = 'H'
    ZOMBIES = 'Z'


class GameInfoPage(Page):
    template = 'wagtail/game_info.html'

    subpage_types = ['app.AnnouncementPage', 'app.MissionPage']
    parent_page_types = ['app.DashboardPage']

    def get_context(self, request, *args, **kwargs):
        context = super(GameInfoPage, self).get_context(request)
        game = most_recent_game()
        player = Player.objects.filter(user=request.user, game=game, active=True).first()
        context['is_mobile'] = request.user_agent.is_mobile
        context['player'] = player
        context['game'] = game
        context['announcements'] = \
            self.get_children().type(AnnouncementPage).live().order_by('-first_published_at')
        context['missions'] = \
            self.get_children().type(MissionPage).live().order_by('-first_published_at')
        return context


class AnnouncementPage(Page):
    template = 'wagtail/announcement.html'
    body = RichTextField(blank=True)

    viewable_by = EnumField(enum=ViewableBy, max_length=1)

    content_panels = Page.content_panels + [
        FieldPanel('viewable_by'),
        FieldPanel('body', classname="full"),
    ]

    parent_page_types = ['app.GameInfoPage']
    subpage_types = []

    def get_admin_display_title(self):
        return f'<{self.viewable_by}> {self.draft_title or self.title}'

    def get_context(self, request, *args, **kwargs):
        context = super(AnnouncementPage, self).get_context(request)
        game = most_recent_game()
        player = Player.objects.filter(user=request.user, game=game, active=True).first()
        context['player'] = player
        context['game'] = game
        return context

    def is_viewable_by(self, player):
        if self.viewable_by == ViewableBy.ALL:
            return True
        if self.viewable_by == ViewableBy.HUMANS and player.is_human:
            return True
        if self.viewable_by == ViewableBy.ZOMBIES and player.is_zombie:
            return True
        if player.is_spectator or player.user.is_superuser:
            return True
        return False


class MissionPage(Page):
    template = 'wagtail/mission.html'
    body = RichTextField(blank=True)

    viewable_by = EnumField(enum=ViewableBy, max_length=1)

    content_panels = Page.content_panels + [
        FieldPanel('viewable_by'),
        FieldPanel('body', classname="full")
    ]

    parent_page_types = ['app.GameInfoPage']
    subpage_types = []

    def get_admin_display_title(self):
        return f'<{self.viewable_by}> {self.draft_title or self.title}'

    def get_context(self, request, *args, **kwargs):
        context = super(MissionPage, self).get_context(request)
        game = most_recent_game()
        player = Player.objects.filter(user=request.user, game=game, active=True).first()
        context['player'] = player
        context['game'] = game
        return context

    def is_viewable_by(self, player):
        if self.viewable_by == ViewableBy.ALL:
            return True
        if self.viewable_by == ViewableBy.HUMANS and player.is_human:
            return True
        if self.viewable_by == ViewableBy.ZOMBIES and player.is_zombie:
            return True
        if player.is_spectator or player.user.is_superuser:
            return True
        return False
