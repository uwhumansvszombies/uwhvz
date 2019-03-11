import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "uwhvz.settings.production")
application = get_wsgi_application()

try:
    import uwsgidecorators
    from django.core.management import call_command

    @uwsgidecorators.timer(15)
    def send_queued_mail(num):
        """Send queued mail every 15 seconds"""
        call_command('send_queued_mail', processes=1)
except ImportError:
    print("uwsgidecorators not found. Cron and timers are disabled")
