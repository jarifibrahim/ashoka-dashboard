from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from datetime import datetime as dt
from .utility import Data
from django.shortcuts import reverse


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
        """
        Returns total number of teams in the Dashboard
        :returns: Total teams count
        """
        return len(self.teams.all())

    total_weeks = property(_get_total_weeks)

    @property
    def fellow_form_url(self):
        """
        Returns the encrypted form url for the Fellow Survey
        :return: Encrypted URL
        """
        hash_value = Data.encode_data(self.id)
        return reverse('fellow_survey', kwargs={'hash_value': hash_value})


class Team(models.Model):
    """
    Represents a Team. Each Team consists of Members.
    """
    dashboard = models.ForeignKey(
        Dashboard, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField("Team Name", max_length=200, unique=True)
    lrp_comment = models.TextField("LRP Comment", blank=True)
    STATUS_CHOICES = (
        ('RED', 'Major issues!!!'),
        ('YELLOW', 'Some minor issues!'),
        ('GREEN', 'All good!')
    )
    status = models.CharField(
        "Team Status", choices=STATUS_CHOICES, max_length=7, default='GREEN')

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

    @property
    def last_response(self):
        """
        Returns the last consultant form response belonging to the team
        :returns: Last consultant survey model belonging to the team or
                  empty string if no response exists
        """
        try:
            return ConsultantSurvey.objects.filter(team=self.id).latest(
                'call_date')
        except ConsultantSurvey.DoesNotExist:
            return None

    @property
    def working_document(self):
        """
        Returns last working document url
        :return: Working document url
        """

        entry = self.consultant_surveys.values('document_link').exclude(
            document_link__isnull=True).exclude(
            document_link__exact='').order_by('-call_date')
        if entry:
            return entry[0]['document_link']
        return ""

    @property
    def consultant_request(self):
        """
        Returns last consultant request
        :return: Last request
        """
        entry = self.consultant_surveys.values('help').exclude(
            help__isnull=True).exclude(help__exact="").order_by('-call_date')
        if entry:
            return entry[0]['help']
        return ""

    @property
    def fellow_request(self):
        """
        Returns last fellow request
        :return: Last fellow request
        """
        entry = self.fellow_surveys.values('comments').exclude(
            comments__isnull=True).exclude(comments__exact="").order_by(
            '-submit_date')
        if entry:
            return entry[0]['comments']
        return ""

    @property
    def consultant_form_url(self):
        """
        Returns encrypted form url for the Consultant Survey
        :return: Encrypted url
        """
        hash_value = Data.encode_data(self.id)
        return reverse('consultant_survey', kwargs={'hash_value': hash_value})


class Role(models.Model):
    """
    Represents possible roles a member can have.
    """
    short_name = models.CharField("Short Name", max_length=3)
    long_name = models.CharField("Role", max_length=18)

    def __str__(self):
        return self.long_name

    @classmethod
    def get_role_id(cls, role_name):
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


class SecondaryRole(models.Model):
    """
    Represents secondary roles such as Process Manager, Pulse Checker, etc
    """
    short_name = models.CharField("Short Name", max_length=100)
    role = models.CharField("Role", max_length=200)

    def __str__(self):
        return self.role


class Member(models.Model):
    """
    Represents Members of a Team.
    """
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="members")
    name = models.CharField("Name", max_length=200)
    email = models.CharField("Email", max_length=200)
    role = models.ForeignKey(Role, related_name="role")
    secondary_role = models.ManyToManyField(SecondaryRole,
                                            related_name="secondary_role")
    receives_survey_reminder_emails = models.BooleanField(
        "Receives reminder emails?")
    comment = models.TextField("comment", blank=True)

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
    help = models.TextField("Ashoka team should help with",
                            blank=True)
    phase_rating = models.IntegerField("How is the advisory phase going?",
                                       blank=True, null=True,
                                       validators=[MinValueValidator(1),
                                                   MaxValueValidator(10)]
                                       )
    other_comments = models.TextField("Any other comments?",
                                      blank=True)
    document_link = models.URLField("Link to current document", blank=True)

    def __str__(self):
        return "ID: {0}, Team: {1}, Date: {2}".format(
            self.id, self.team, dt.date(self.submit_date))

    @property
    def missing_member_names(self):
        """
        Returns str containing names of missing members
        :return: missing member string
        """
        missing_member_list = list(
            self.missing_member.all().values_list('name', flat=True))
        return ", ".join(missing_member_list)


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
    comments = models.TextField("Any other comments?",
                                blank=True)
    other_help = models.TextField("Any other Ashoka should help with?",
                                  blank=True)

    def __str__(self):
        return "ID: {0}, Team: {1}, Date: {2}".format(
            self.id, self.team, dt.date(self.submit_date))


class Email(models.Model):
    """
    Represents an email.
    """
    TYPE_CHOICES = (
        ('IM', 'Instruction Mail'),
        ('RM', 'Reminder Mail'),
    )
    type = models.CharField("Type of Email", choices=TYPE_CHOICES, max_length=5)
    subject = models.CharField("Subject of the Email", max_length=200)
    message = models.TextField("Body of the Email")

    def __str__(self):
        return self.subject


class TeamStatus(models.Model):
    """
    Represents various team settings
    """
    team = models.ForeignKey(Team, related_name='team_status')
    call_change_count = models.IntegerField("Add/Subtract Total Calls count",
                                            null=True)
    automatic_reminder = models.BooleanField("Send Automatic Reminders?",
                                             default=True)
    last_automatic_reminder = models.DateTimeField("Last automatic reminder "
                                                   "sent on", default=None,
                                                   null=True)
    KICK_OFF_CHOICES = (
        ('NS', 'Not Started'),
        ('IMS', 'IMS'),
        ('DA', 'Date Arranged'),
        ('CH', 'Call Happened')
    )
    kick_off = models.CharField(
        "Kick Off Status", choices=KICK_OFF_CHOICES, default='NS', max_length=5)
    kick_off_comment = models.TextField("Kick Off Comment", blank=True)
    mid_term = models.CharField(
        "Mid Term Status", choices=KICK_OFF_CHOICES, default='NS', max_length=5)
    mid_term_comment = models.TextField("Mid Term Comment", blank=True)

    def __str__(self):
        return str(self.team)