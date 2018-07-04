from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page


class NewsPage(Page):
    template = 'wagtail/news.html'

    subpage_types = ['app.Article']
    parent_page_types = ['app.DashboardPage']


class Article(Page):
    template = 'wagtail/article.html'
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]

    parent_page_types = ['app.NewsPage']
    subpage_types = []
