from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from datetime import datetime as dt
from datetime import date
from django.shortcuts import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import math


class Data:
    @staticmethod
    def encode_data(data):
        """
        Encodes data to generate a hash.
        This hash is used to generate urls

        :param data: The data to be encoded.
        :returns: hash value
        """
        return "%08x" % (data * 387420489 % 4000000000)

    @staticmethod
    def decode_data(data):
        """
        Decodes the data encoded by 'encode_data' function.

        :param data: The hash value to be decoded.
        :returns: original data
        """
        return int(data, 16) * 3513180409 % 4000000000


class Dashboard(models.Model):
    """
    Represents a Dashboard. Dashboard contains Teams and Teams contain Members.
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

    total_weeks = property(_get_total_weeks)

    @property
    def fellow_form_url(self):
        """
        Returns the encrypted form url for the Fellow Survey
        :return: Encrypted URL
        """
        hash_value = Data.encode_data(self.id)
        return reverse('fellow_survey', kwargs={'hash_value': hash_value})

    @property
    def current_week(self):
        """
        Returns current week of advisory process
        :return: Week number of advisory process
        """
        start_date = self.advisory_start_date
        return math.ceil(int((date.today() - start_date).days) / 7.0)


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

    def get_members_with_role(self, role):
        """
        Returns names of team members belonging to a specific role.

        :param role:Members should be belonging to this role.
        :returns:   Comma separated string to member belonging to specified role
        """
        role = Role.objects.filter(long_name=role).values("id")
        if not role:
            values = [r.long_name for r in Role.objects.all()]
            raise ValueError(
                "Invalid role name. Possible Values are: " + str(values))
        role_members = self.members.filter(role=role[0]['id'])
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
        :return: Working document url if present, else empty string.
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
        :return: Last request if present, else empty string
        """
        entry = self.consultant_surveys.values('help').exclude(
            help__isnull=True).exclude(help__exact="")
        if entry:
            return entry.latest('call_date')['help']
        return ""

    @property
    def fellow_request(self):
        """
        Returns last fellow request
        :return: Last fellow request if present, else empty string
        """
        entry = self.fellow_surveys.values('comments').exclude(
            comments__isnull=True).exclude(comments__exact="")
        if entry:
            return entry.latest('submit_date')['comments']
        return ""

    @property
    def consultant_form_url(self):
        """
        Returns encrypted form url for the Consultant Survey
        :return: Encrypted url
        """
        hash_value = Data.encode_data(self.id)
        return reverse('consultant_survey', kwargs={'hash_value': hash_value})

    @property
    def last_consultant_rating(self):
        """
        Returns last phase rating provided by the consultant
        :return: None, if no consultant response with rating is found.
                 Else, Last phase rating by consultant.
        """

        entry = self.consultant_surveys.values('rating').exclude(
            rating__isnull=True)
        if entry:
            return entry.latest('call_date')['rating']
        return None

    @property
    def last_fellow_rating(self):
        """
        Returns last phase rating provided by the fellow
        :return: None, if there are no fellow responses.
                 Else, Last phase rating by fellow.
        """
        entry = self.fellow_surveys.values('rating').exclude(
            rating__isnull=True)
        if entry:
            return entry.latest('submit_date')['rating']
        return None

    @property
    def unprepared_calls_percentage(self):
        """
        Returns percentage of unprepared calls.
        :return: None, if there are no consultant responses.
                 Else, percentage of unprepared calls.
        """
        unprepared_calls = self.consultant_surveys.filter(all_prepared=False)
        total_calls = self.consultant_surveys.all().count()
        try:
            return math.floor((unprepared_calls.count() / total_calls) * 100)
        except ZeroDivisionError:
            return None


class Role(models.Model):
    """
    Represents possible roles a member can have.
    """
    short_name = models.CharField("Short Name", max_length=3)
    long_name = models.CharField("Role", max_length=18)

    def __str__(self):
        return self.long_name


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
    Represents a Member of a Team.
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
    phase = models.CharField("Phase", max_length=200)
    phase_number = models.PositiveIntegerField(
        "Phase number", help_text="Phase are sorted according to this number. "
                                  "If phase 'A' should happen before phase "
                                  "'B' then 'A' should have lower phase number "
                                  "value than 'B'.", unique=True)

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
    rating = models.IntegerField("How is the advisory phase going?",
                                 blank=True, null=True,
                                 validators=[MinValueValidator(1),
                                             MaxValueValidator(10)]
                                 )
    other_comments = models.TextField("Any other comments?",
                                      blank=True)
    document_link = models.URLField("Link to current document", blank=True)

    def __str__(self):
        return "ID: {0}, Team: {1}, Submit Date: {2}, Call Date: {3}".format(
            self.id, self.team, dt.date(self.submit_date), self.call_date)

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
    rating = models.IntegerField("How is the advisory phase going?",
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
    help_text = "Template name to uniquely identify it."
    name = models.CharField("Name", max_length=200,
                            unique=True, help_text=help_text)
    help_text = "Type of the template. Currently Instruction Email template " \
                "and Reminder Email template are supported."
    type = models.CharField(
        "Type", choices=TYPE_CHOICES, max_length=5,
        help_text=help_text)
    help_text = "If this field is set to ON all the emails of the specified " \
                "type will use this template. Each type of email can have " \
                "only one default"
    default_template = models.BooleanField("Default",
                                           default=False,
                                           help_text=help_text)
    subject = models.CharField("Subject", max_length=200)
    help_text = "If you wish to include the url to consultant form in the " \
                "email, please add 'FORM_URL' (without quotes) placeholder. " \
                "It will be replaced by the actual consultant url in the email."
    message = models.TextField("Body of the Email", help_text=help_text)

    # Overwrite save method to change default template
    def save(self, *args, **kwargs):
        if self.default_template:
            # Get current default object
            try:
                email_object = Email.objects.get(type=self.type,
                                                 default_template=True)
                # Set default value to false
                email_object.default_template = False
                email_object.save()
            except Email.DoesNotExist:
                pass
        super(Email, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class TeamStatus(models.Model):
    """
    Represents team's current status
    """
    team = models.OneToOneField(Team, related_name='team_status')
    help_text = "This value will be added to total calls count."
    call_change_count = models.IntegerField("Add/Subtract Total Calls count",
                                            default=0, help_text=help_text)
    help_text = "Should periodic Automatic Reminders Emails be sent?"
    automatic_reminder = models.BooleanField("Send Automatic Reminders?",
                                             default=True, help_text=help_text)
    help_text = "Last automatic reminder email was sent on this date"
    last_automatic_reminder = models.DateTimeField("Last automatic reminder "
                                                   "sent on", blank=True,
                                                   null=True, editable=False)
    KICK_OFF_CHOICES = (
        ('NS', 'Not Started'),
        ('IMS', 'Intro Mail Sent'),
        ('DA', 'Date Arranged'),
        ('CH', 'Call Happened')
    )
    kick_off = models.CharField("Kick Off Status", choices=KICK_OFF_CHOICES,
                                default='NS', max_length=5)
    kick_off_comment = models.TextField("Kick Off Comment", blank=True)
    mid_term = models.CharField("Mid Term Status", choices=KICK_OFF_CHOICES,
                                default='NS', max_length=5)
    mid_term_comment = models.TextField("Mid Term Comment", blank=True)

    def __str__(self):
        return str(self.team)


class WeekWarning(models.Model):
    """
    Represents warnings for a week. Each week has different warning criterion.
    """
    week_number = models.PositiveIntegerField("Week Number", unique=True)

    # Call count warnings
    help_text = "Number of calls less than this value leads to Yellow warning."
    calls_y = models.PositiveIntegerField(
        "Call count - Yellow warning", help_text=help_text)
    help_text = "Number of calls less than this value leads to Red warning (" \
                "Should be less than yellow warning call count) "
    calls_r = models.PositiveIntegerField(
        "Call count - Red warning", help_text=help_text)

    # Unprepared calls warning
    help_text = "If percentage of unprepared calls is less than this " \
                "threshold, Yellow warning will be raised. "
    unprepared_calls_y = models.IntegerField(
        "% unprepared call threshold", help_text=help_text)
    help_text = "If percentage of unprepared calls is less than this " \
                "threshold, Red warning will be raised. "
    unprepared_calls_r = models.IntegerField(
        "% unprepared call threshold", help_text=help_text)

    # Member missing call warnings
    help_text = "Person missing calls: > leads to Yellow warning"
    member_call_y = models.PositiveIntegerField(
        "Member missing call count - Yellow warning", help_text=help_text)
    help_text = "Person missing calls: > leads to Red warning (Should be " \
                "greater than yellow warning member call count) "
    member_call_r = models.PositiveIntegerField(
        "Member missing call count - Red warning", help_text=help_text)

    # Kick off warnings
    help_text = "Kick-off not happened in this week leads to Yellow warning."
    kick_off_y = models.BooleanField(
        "Kick Off - Yellow warning", help_text=help_text)
    help_text = "Kick-off not happened in this week leads to Red warning."
    kick_off_r = models.BooleanField(
        "Kick Off - Red warning", help_text=help_text)

    # Mid term warnings
    help_text = "Mid-term not happened in this week leads to Yellow warning"
    mid_term_y = models.BooleanField(
        "Mid Term - Yellow warning", help_text=help_text)
    help_text = "Mid-term not happened in this week leads to Red warning"
    mid_term_r = models.BooleanField(
        "Mid Term - Red warning", help_text=help_text)

    # Phase related warnings
    help_text = "Phases: Progress expected"
    phase = models.ForeignKey(
        AdvisoryPhase, help_text=help_text, related_name="expected_phase")
    help_text = "Yellow warning if in this Phase"
    phase_y = models.ForeignKey(AdvisoryPhase,
                                help_text=help_text,
                                null=True,
                                blank=True,
                                related_name="yellow_warning_phase")
    help_text = "Red warning if in less than this Phase"
    phase_r = models.ForeignKey(AdvisoryPhase,
                                help_text=help_text,
                                null=True,
                                blank=True,
                                related_name="red_warning_phase")
    # Rating related warnings
    help_text = "Red warning if last rating by consultant is less than this " \
                "value "
    consultant_rating_r = models.PositiveIntegerField(
        "Consultant Rating Red Warning", default=7, help_text=help_text)
    help_text = "Red warning if last rating by fellow is less than this " \
                "value "
    fellow_rating_r = models.PositiveIntegerField(
        "Fellow Phase Rating Red Warning", default=7, help_text=help_text)

    def clean(self):
        if self.calls_r > self.calls_y:
            raise ValidationError(_('Call count for Red warning should be '
                                    'less than or equal to Call count for '
                                    'Yellow warning'))
        if self.member_call_r < self.member_call_y:
            raise ValidationError(_('Member missing call count for Red '
                                    'warning should be greater than Member '
                                    'missing call count for Yellow warning'))

    # Overwrite parent save method
    def save(self, *args, **kwargs):
        orig = WeekWarning.objects.get(pk=self.id)

        # Execute following code only if the value has changed
        if self.kick_off_y is not orig.kick_off_y:
            """
            If a week has kick off yellow warning then all the weeks following
            it should have the kick off yellow warning.
            """
            weeks = WeekWarning.objects.filter(week_number__gt=self.week_number)
            weeks.update(kick_off_y=self.kick_off_y)

        if self.kick_off_r is not orig.kick_off_r:
            """
            If a week has kick off red warning then all the weeks following
            it should have the kick off red warning.
            """
            weeks = WeekWarning.objects.filter(week_number__gt=self.week_number)
            weeks.update(kick_off_r=self.kick_off_r)

        if self.mid_term_y is not orig.mid_term_y:
            """
            If a week has mid term yellow warning then all the weeks following
            it should have the mid term yellow warning.
            """
            weeks = WeekWarning.objects.filter(week_number__gt=self.week_number)
            weeks.update(mid_term_y=self.mid_term_y)

        if self.mid_term_r is not orig.mid_term_r:
            """
            If a week has mid term red warning then all the weeks following
            it should have the mid term red warning.
            """
            weeks = WeekWarning.objects.filter(week_number__gt=self.week_number)
            weeks.update(mid_term_r=self.mid_term_r)

        super(WeekWarning, self).save(*args, **kwargs)

    def __str__(self):
        return "Week {}".format(self.week_number)


class TeamWarning(models.Model):
    """
    Represents the set of warnings related to a team
    """
    WARNING_TYPES = (
        ('G', 'Green'),
        ('Y', 'Yellow'),
        ('R', 'Red')
    )
    team = models.OneToOneField(Team, related_name="warnings")
    call_count = models.CharField("Warning - Call Count",
                                  choices=WARNING_TYPES,
                                  default="G", max_length=3)
    call_count_comment = models.CharField("Comment - Call Count",
                                          max_length=300, blank=True)
    phase = models.CharField("Warning - Phase", choices=WARNING_TYPES,
                             default="G", max_length=3)
    phase_comment = models.CharField("Comment - Phase", max_length=300,
                                     blank=True)
    kick_off = models.CharField("Warning - Kick Off", choices=WARNING_TYPES,
                                default="G", max_length=3)
    kick_off_comment = models.CharField("Comment - Kick Off", max_length=300,
                                        blank=True)
    mid_term = models.CharField("Warning - Mid Term", choices=WARNING_TYPES,
                                default="G", max_length=3)
    mid_term_comment = models.CharField("Comment - Mid Term", max_length=300,
                                        blank=True)
    unprepared_call = models.CharField("Warning - Unprepared Calls",
                                       choices=WARNING_TYPES, default="G",
                                       max_length=3)
    unprepared_call_comment = models.CharField("Comment - Unprepared Calls",
                                               max_length=300, blank=True)
    consultant_rating = models.CharField("Warning - Consultant Rating",
                                         choices=WARNING_TYPES, default="G",
                                         max_length=3)
    consultant_rating_comment = models.CharField("Comment - Consultant Rating",
                                                 max_length=300, blank=True)
    fellow_rating = models.CharField("Warning - Fellow Rating",
                                     choices=WARNING_TYPES, default="G",
                                     max_length=3)
    fellow_rating_comment = models.CharField("Comment - Fellow Rating",
                                             max_length=300, blank=True)

    def __str__(self):
        return str(self.team) + " Warnings"
