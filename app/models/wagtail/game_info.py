from enumfields import EnumField, Enum
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page

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
        player = request.user.player(game)
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
        player = request.user.player(game)
        context['player'] = player
        context['game'] = game
        return context

    @property
    def viewable_by_humans(self):
        return self.viewable_by == ViewableBy.HUMANS or self.viewable_by == ViewableBy.ALL

    @property
    def viewable_by_zombies(self):
        return self.viewable_by == ViewableBy.ZOMBIES or self.viewable_by == ViewableBy.ALL


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
        player = request.user.player(game)
        context['player'] = player
        context['game'] = game
        return context

    @property
    def viewable_by_humans(self):
        return self.viewable_by == ViewableBy.HUMANS or self.viewable_by == ViewableBy.ALL

    @property
    def viewable_by_zombies(self):
        return self.viewable_by == ViewableBy.ZOMBIES or self.viewable_by == ViewableBy.ALL
