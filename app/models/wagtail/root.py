from django.shortcuts import redirect
from wagtail.core.models import Page


class RootPage(Page):
    subpage_types = ['app.DashboardPage']


class DashboardPage(Page):
    subpage_types = ['app.GameInfoPage', 'app.NewsPage']
    parent_page_types = ['app.RootPage']

    def serve(self, request, **kwargs):
        # Django routes to this for /dashboard/ but not /dashboard.
        # To save some server errors about DashboardPage not having
        # a template we will just redirect to dashboard.
        return redirect('dashboard')
