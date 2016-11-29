from django.db import models


class Dashboard(models.Model):
    name = models.CharField("Dashboard Name", max_length=200, unique=True)
    create_date = models.DateTimeField("Dashboard Create Date", auto_now_add=True)
    advisory_start_date = models.DateField("Start date of Advisory Process")
    advisory_end_date = models.DateField("End date of Advisory Process")

    class Meta:
        verbose_name_plural = "Dashboards"
        verbose_name = "Dashboard"

    def __str__(self):
        return self.name

    def _get_total_weeks(self):
        delta = self.advisory_end_date - self.advisory_start_date
        return delta.days // 7

    @property
    def team_count(self):
        return len(self.teams.all())

    total_weeks = property(_get_total_weeks)


class Team(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField("Team Name", max_length=200, unique=True)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return len(self.member_set.all())


class Role(models.Model):
    short_name = models.CharField("Short Name", max_length=3)
    long_name = models.CharField("Role", max_length=18)

    def __str__(self):
        return self.long_name


class Member(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    name = models.CharField("Name", max_length=200)
    email = models.CharField("Email", max_length=200)
    role = models.ForeignKey(Role, related_name="role")

    def __str__(self):
        return self.name


class AdvisoryPhase(models.Model):
    phase = models.CharField("Phases", max_length=200)
    reached_in_week = models.IntegerField("Reached in Week")
    expected_calls = models.IntegerField("Expected calls")

    def __str__(self):
        return self.phase


class FellowSurvey(models.Model):
    team = models.ForeignKey(Team, related_name="surveys")
    submit_date = models.DateTimeField("Submit date", auto_now_add=True)
    call_date = models.DateField("Call date")
    missing_member = models.CharField("Missing members", max_length=300, blank=True)
    all_prepared = models.BooleanField("All participants prepared for call?")
    current_phase = models.ForeignKey(AdvisoryPhase, related_name="surveys")
    topic_discussed = models.CharField("Topic Discussed", max_length=200)
    help = models.CharField("Ashoka team should help with", max_length=3000, blank=True)
    phase_rating = models.IntegerField("How is the phase going?", blank=True, null=True)
    other_comments = models.CharField("Any other comments?", max_length=3000, blank=True)
    document_link = models.URLField("Link to current document", blank=True)

    def __str__(self):
        return "ID: {0}, team: {1}, date: {2}".format(self.id, self.team, self.submit_date)
