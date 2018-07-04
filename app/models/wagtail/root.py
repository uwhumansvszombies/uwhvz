from wagtail.core.models import Page


class RootPage(Page):
    subpage_types = ['app.DashboardPage']


class DashboardPage(Page):
    subpage_types = ['app.GameInfoPage', 'app.NewsPage']
    parent_page_types = ['app.RootPage']
