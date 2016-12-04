from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime as dt


class Dashboard(models.Model):
    """
    Represents a Dashboard. Dashboard contains
    Teams and Teams contain Members
    """
    name = models.CharField("Dashboard Name", max_length=200, unique=True)
    create_date = models.DateTimeField(
        "Dashboard Create Date", auto_now_add=True)
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
        """ Returns total number of teams in the Dashboard """
        return len(self.teams.all())

    total_weeks = property(_get_total_weeks)


class Team(models.Model):
    """
    Represents a Team. Each Team consists of Members.
    """
    dashboard = models.ForeignKey(
        Dashboard, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField("Team Name", max_length=200, unique=True)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return len(self.member_set.all())

    def get_members_with_role(self, role):
        """
        Returns names of team members belonging to a specific role.

        :param role: Members should be belonging to this role.
        """
        role_id = Role.get_role_id(role)
        role_members = self.members.filter(role=role_id)
        member_string = ', '.join([str(i) for i in role_members])
        return member_string


class Role(models.Model):
    """
    Represents possible roles a member can have.
    """
    short_name = models.CharField("Short Name", max_length=3)
    long_name = models.CharField("Role", max_length=18)

    def __str__(self):
        return self.long_name

    @classmethod
    def get_role_id(self, role_name):
        """
        Returns the ID of the role_name. Useful when trying to find members
        belonging to specific role.

        :param role_name:   Role name whose id is to be found.
        :raises ValueError: If no role represented by role_name is found.
        """
        try:
            return Role.objects.filter(long_name=role_name)[0].id
        except:
            values = [r.long_name for r in Role.objects.all()]
            raise ValueError(
                "Invalid role name. Possible Values are: " + str(values))


class Member(models.Model):
    """
    Represents Members of a Team.
    """
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="members")
    name = models.CharField("Name", max_length=200)
    email = models.CharField("Email", max_length=200)
    role = models.ForeignKey(Role, related_name="role")
    receives_survey_reminder_emails = models.BooleanField(
        "Receives reminder emails?")

    def __str__(self):
        return self.name


class AdvisoryPhase(models.Model):
    """
    Represents all the possible Advisory Phases.
    """
    phase = models.CharField("Phases", max_length=200)
    reached_in_week = models.IntegerField("Reached in Week")
    expected_calls = models.IntegerField("Expected calls")

    def __str__(self):
        return self.phase


class ConsultantSurvey(models.Model):
    """
    Represents Consultant Surveys(Forms) used to get Team status report.
    """
    team = models.ForeignKey(Team, related_name="consultant_surveys")
    submit_date = models.DateTimeField("Submit date", auto_now_add=True)
    call_date = models.DateField("Call date")
    missing_member = models.ManyToManyField(Member,
                                            related_name="surveys",
                                            blank=True)
    all_prepared = models.BooleanField("All participants prepared for call?")
    current_phase = models.ForeignKey(AdvisoryPhase, related_name="surveys")
    topic_discussed = models.CharField("Topic Discussed", max_length=200)
    help = models.CharField("Ashoka team should help with",
                            max_length=3000,
                            blank=True)
    phase_rating = models.IntegerField("How is the advisory phase going?",
                                       blank=True, null=True,
                                       validators=[MinValueValidator(1),
                                                   MaxValueValidator(10)]
                                       )
    other_comments = models.CharField("Any other comments?",
                                      max_length=3000,
                                      blank=True)
    document_link = models.URLField("Link to current document", blank=True)

    def __str__(self):
        return "ID: {0}, Team: {1}, Date: {2}".format(
            self.id, self.team, dt.date(self.submit_date))


class FellowSurvey(models.Model):
    """
    Represents Fellow Surveys
    """
    team = models.ForeignKey(Team, related_name='fellow_surveys')
    submit_date = models.DateTimeField("Submit date", auto_now_add=True)
    phase_rating = models.IntegerField("How is the advisory phase going?",
                                       blank=True, null=True,
                                       validators=[MinValueValidator(1),
                                                   MaxValueValidator(10)]
                                       )
    comments = models.CharField("Any other comments?",
                                max_length=3000,
                                blank=True)
    other_help = models.CharField("Any other Ashoka should help with?",
                                  max_length=3000,
                                  blank=True)

    def __str__(self):
        return "ID: {0}, Team: {1}, Date: {2}".format(
            self.id, self.team, dt.date(self.submit_date))
