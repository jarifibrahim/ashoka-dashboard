import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q
from post_office import mail

from ...models import Dashboard


class Command(BaseCommand):
    help = "Send reminder emails"

    def handle(self, *args, **options):
        """
        Bulk send reminder emails.
        """
        today = datetime.date.today().weekday()
        all_dashboard = Dashboard.objects.all()
        all_emails = []
        for d in all_dashboard:
            # Advisory period completed. So skip it
            if d.advisory_end_date < datetime.date.today():
                continue
            url = 'http://ashoka-dashboard.herokuapp.com' \
                + d.consultant_form_url
            all_teams = d.teams.filter(
                reminder_emails_day=today).select_related()
            for team in all_teams:
                # Add automatic reminder only if automatic_reminder is true
                if not team.team_status.automatic_reminder:
                    continue
                # Get all Pulse Checkers and LRPs
                recipients = team.members.filter(
                    Q(secondary_role__short_name="PC") or
                    Q(role__short_name="LRP")
                ).distinct()
                if recipients:
                    to = [r['email'] for r in recipients.values('email').all()]
                    all_emails.append({
                        'recipients': to,
                        'template': 'reminder_email',
                        'context': {'data': url},
                    })
        # Queue all reminder emails at once
        mail.send_many(all_emails)
        # Send all queued emails
        mail.send_queued()
