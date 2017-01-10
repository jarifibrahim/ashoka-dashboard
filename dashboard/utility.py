from django.contrib import messages
from . import models
from post_office.models import EmailTemplate
from django.template import Context, Template
from post_office import mail
from django.db.models import Q


class UpdateWarnings:
    """
    Contains functions used to update team status
    """
    status = {
        'green': 'G',
        'yellow': 'Y',
        'red': 'R'
    }

    def __init__(self, team):
        current_week = team.dashboard.current_week
        self.team = team
        self.week_warning = models.WeekWarning.objects.get(
            week_number=current_week)
        self.tw = team.warnings

    # Total calls check
    def total_calls_check(self):
        response_count = self.team.consultant_surveys.all().count()
        change_count = self.team.team_status.call_change_count
        total_call_count = response_count + change_count
        if total_call_count < self.week_warning.calls_r:
            msg = "Total Calls ({0}+{1})={2} < Expected Calls Red: {3}"
            msg = msg.format(response_count, change_count, total_call_count,
                             self.week_warning.calls_r)
            return self.status['red'], msg
        elif total_call_count < self.week_warning.calls_y:
            msg = "Total Calls ({0}+{1})={2} < Expected Calls Yellow: {3}"
            msg = msg.format(response_count, change_count, total_call_count,
                             self.week_warning.calls_y)
            return self.status['yellow'], msg
        else:
            msg = "Total Calls ({0}+{1})={2} >= Expected Calls: " \
                  "Yellow:{3} and Red:{4}"
            msg = msg.format(response_count, change_count, total_call_count,
                             self.week_warning.calls_y,
                             self.week_warning.calls_r)
            return self.status['green'], msg

    # Current Phase
    def phase_check(self):
        last_response = self.team.last_response
        # If there are no responses skip the following section
        if last_response:
            current_phase = last_response.current_phase
            yellow = self.week_warning.phase_y
            red = self.week_warning.phase_r
            green = self.week_warning.phase
            if red:
                if current_phase.phase_number <= red.phase_number:
                    msg = "Current Phase:{0} < Red warning Phase:{1}"
                    msg = msg.format(current_phase, red)
                    return self.status['red'], msg

            if yellow:
                if yellow.phase_number == current_phase.phase_number:
                    msg = "Current Phase:{1} is Yellow warning Phase:{0}"
                    msg = msg.format(yellow, current_phase)
                    return self.status['yellow'], msg
            if green:
                if green.phase_number == current_phase.phase_number:
                    msg = "Current Phase:{1} is Expected Phase:{0}"
                    msg = msg.format(green, current_phase)
                    return self.status['green'], msg
            msg = "No warnings found"
            return self.status['green'], msg
        msg = "No consultant responses found"
        return self.status['green'], msg

    # Kick Off
    def kick_off_check(self):
        if self.team.team_status.kick_off == "NS":
            yellow = self.week_warning.kick_off_y
            red = self.week_warning.kick_off_r
            msg = "Kick off not yet happened"
            if red:
                return self.status['red'], msg
            if yellow:
                return self.status['yellow'], msg
            else:
                return self.status['green'], "No kick off warnings found " \
                                             "for this week"
        msg = self.team.team_status.get_kick_off_display()
        return self.status['green'], msg

    # Mid Term
    def mid_term_check(self):
        if self.team.team_status.mid_term == "NS":
            yellow = self.week_warning.mid_term_y
            red = self.week_warning.mid_term_r
            msg = "Mid Term not yet happened"
            if red:
                return self.status['red'], msg
            if yellow:
                return self.status['yellow'], msg
            else:
                return self.status['green'], "No mid term warnings found " \
                                             "for this week"
        msg = self.team.team_status.get_mid_term_display()
        return self.status['green'], msg

    # Consultant Rating
    def consultant_rating_check(self):
        c_last_rating = self.team.last_consultant_rating
        if c_last_rating:
            if c_last_rating <= self.week_warning.consultant_rating_r:
                msg = "Last Consultant Rating: {0} <= Consultant Rating " \
                      "Red Warning: {1}".format(
                          c_last_rating, self.week_warning.consultant_rating_r)
                return self.status['red'], msg
            else:
                msg = "Last Consultant Rating: {0} > Consultant Rating " \
                      "Red Warning: {1}".format(
                          c_last_rating, self.week_warning.consultant_rating_r)
                return self.status['green'], msg
        # If there are no ratings
        else:
            return self.status['green'], "No Rating found (Either there are " \
                                         "no consultant responses or none of " \
                                         "the consultant responses have " \
                                         "rating value) "

    # Fellow Rating
    def fellow_rating_check(self):
        f_last_rating = self.team.last_fellow_rating
        if f_last_rating:
            if f_last_rating < self.week_warning.fellow_rating_r:
                msg = "Last Fellow Rating: {0} < Fellow Rating " \
                      "Red Warning: {1}".format(
                          f_last_rating, self.week_warning.fellow_rating_r)
                return self.status['red'], msg
            else:
                msg = "Fellow Rating: {0} > Fellow Rating " \
                      "Red Warning: {1}".format(
                          f_last_rating, self.week_warning.fellow_rating_r)
                return self.status['green'], msg
        # If there are no ratings
        else:
            return self.status['green'], "No Rating found (Either there are " \
                                         "no fellow responses or none of the " \
                                         "fellow responses have rating value) "

    # Unprepared calls
    def unprepared_calls_check(self):
        percentage = self.team.unprepared_calls_percentage
        if percentage:
            if percentage > self.week_warning.unprepared_calls_r:
                msg = "% Unprepared calls: {0} > % Unprepared Calls Red " \
                      "Threshold: {1}"
                msg = msg.format(percentage,
                                 self.week_warning.unprepared_calls_r)
                return self.status['red'], msg
            elif percentage > self.week_warning.unprepared_calls_y:
                msg = "% Unprepared calls: {0} > % Unprepared Calls Yellow " \
                      "Threshold: {1}"
                msg = msg.format(percentage,
                                 self.week_warning.unprepared_calls_y)
                return self.status['yellow'], msg
            else:
                msg = "% Unprepared calls: {0} < % Unprepared calls " \
                      "Threshold Yellow:{1} and Red:{2}"
                msg = msg.format(percentage,
                                 self.week_warning.unprepared_calls_y,
                                 self.week_warning.unprepared_calls_r)
                return self.status['green'], msg
        msg = ""
        if percentage is 0:
            msg = "% Unprepared calls: 0. Members were prepared for all " \
                  "the calls."
        if percentage is None:
            msg = "Could not calculate % Unprepared calls. " \
                  "No consultant responses found."

        return self.status['green'], msg

    def check_all_warnings(self):
        cc, cc_comment = self.total_calls_check()
        self.tw.call_count, self.tw.call_count_comment = cc, cc_comment
        self.tw.phase, self.tw.phase_comment = self.phase_check()
        self.tw.kick_off, self.tw.kick_off_comment = self.kick_off_check()
        self.tw.mid_term, self.tw.mid_term_comment = self.mid_term_check()
        cr, cr_comment = self.consultant_rating_check()
        self.tw.consultant_rating = cr
        self.tw.consultant_rating_comment = cr_comment
        fr, fr_comment = self.fellow_rating_check()
        self.tw.fellow_rating, self.tw.fellow_rating_comment = fr, fr_comment
        upc, upc_comment = self.unprepared_calls_check()
        self.tw.unprepared_call = upc
        self.tw.unprepared_call_comment = upc_comment
        self.tw.save()


def update_team_value(request, field_name):
    """
    Updates the team value. This function is called only by update_value when
    a value related to the team is to be updated. The value is sent by a dialog
    form.
    :param request:     Request object that contains all the required values
    :param field_name:  Name of the form field that contains the new value
    :return:            True is successful else False
    """
    # Extract team id from the teamId string
    team_id = request.POST.get('teamId')
    try:
        team_object = models.Team.objects.get(pk=team_id)
    except models.Team.DoesNotExist:
        messages.error(request, "Failed to update value. Invalid team id")
        return False

    # Change Team status color
    if field_name == "newStatusColor":
        try:
            team_object.status_choice = request.POST[field_name]
            team_object.save()
            messages.success(request, "Team status updated successfully.")
            return True
        except Exception as e:
            messages.debug(request, "Failed to update value. " + str(e))
            return False

    # Change Team comment
    elif field_name == "LRPComment":
        try:
            team_object.lrp_comment = request.POST[field_name]
            team_object.save()
            messages.success(request, "Team LRP comment updated successfully")
            return True
        except Exception as e:
            messages.debug(request, "Failed to update value. " + str(e))
            return False

    messages.debug(request, "Unknown action " + field_name)
    return False


def update_team_status_value(request, field_name):
    """
    :param request:     Request object that contains all the required values
    :param field_name:  Name of the form field that contains the new value
    :return:            True is successful else False
    """

    team_id = request.POST.get('teamId')

    try:
        team_object = models.Team.objects.get(pk=team_id)
    except models.Team.DoesNotExist:
        messages.error(request, "Failed to update value. Invalid Team id")
        messages.error(request, request.POST)
        return False

    # Change team call count
    if field_name == "change_calls_count":
        try:
            status_object = models.TeamStatus.objects.get(team=team_object)
            status_object.call_change_count = int(request.POST.get(field_name))
            status_object.save()
            messages.success(request, "Successfully changed call count value.")
            update = UpdateWarnings(team_object)
            cc, cc_comment = update.total_calls_check()
            tw = team_object.warnings
            tw.call_count, tw.call_count_comment = cc, cc_comment
            tw.save()
            return True
        except Exception as e:
            messages.error(request, "Failed to change call count value.")
            messages.debug(request, str(e))
            return False

    # Change automatic reminder status
    elif field_name == "automatic_reminder_status":
        try:
            status_object = models.TeamStatus.objects.get(team=team_object)
            status_object.automatic_reminder = (
                request.POST[field_name] == 'true')
            status_object.save()
            messages.success(request, "Successfully changed automatic "
                                      "reminder status value.")
            return True
        except Exception as e:
            messages.error(request, "Failed to change automatic reminder "
                                    "status value")
            messages.debug(request, str(e))
            return False

    # Change advisory onboarding status
    elif field_name == "advisor_onboarding_status":
        try:
            status_object = models.TeamStatus.objects.get(team=team_object)
            status_object.advisor_onboarding = request.POST[field_name]
            status_object.save()
            messages.success(request, "Successfully changed Advisor "
                                      "Onboarding status value.")
            return True
        except Exception as e:
            messages.error(request, "Failed to change Advisory Onboarding "
                                    "status value.")
            messages.debug(request, str(e))
            return False

    elif field_name == "advisor_onboarding_comment":
        try:
            status_object = models.TeamStatus.objects.get(team=team_object)
            status_object.advisor_onboarding_comment = request.POST[field_name]
            status_object.save()
            messages.success(request, "Successfully changed Advisor "
                                      "Onboarding Comment value.")
            return True
        except Exception as e:
            messages.error(request, "Failed to change Advisor Onboarding "
                                    "Comment value")
            messages.debug(request, str(e))
            return False

    elif field_name == "kick_off_status":
        try:
            status_object = models.TeamStatus.objects.get(team=team_object)
            status_object.kick_off = request.POST[field_name]
            status_object.save()
            update = UpdateWarnings(team_object)
            tw = team_object.warnings
            tw.kick_off, tw.kick_off_comment = update.kick_off_check()
            tw.save()
            messages.success(request, "Successfully changed Kick off status "
                                      "value.")
            return True
        except Exception as e:
            messages.error(request, "Failed to change Kick off "
                                    "status value")
            messages.debug(request, str(e))
            return False

    elif field_name == "kick_off_comment":
        try:
            status_object = models.TeamStatus.objects.get(team=team_object)
            status_object.kick_off_comment = request.POST[field_name]
            status_object.save()
            messages.success(request, "Successfully changed Kick Off Comment "
                                      "value.")
            return True
        except Exception as e:
            messages.error(request, "Failed to change Kick Off Comment "
                                    "value")
            messages.debug(request, str(e))
            return False

    elif field_name == "systemic_vision_status":
        try:
            status_object = models.TeamStatus.objects.get(team=team_object)
            status_object.systemic_vision = request.POST[field_name]
            status_object.save()
            messages.success(request, "Successfully changed Systemic Vision "
                                      "status value.")
            return True
        except Exception as e:
            messages.error(request, "Failed to change Systemic Vision "
                                    "status value")
            messages.debug(request, str(e))
            return False

    elif field_name == "systemic_vision_comment":
        try:
            status_object = models.TeamStatus.objects.get(team=team_object)
            status_object.systemic_vision_comment = request.POST[field_name]
            status_object.save()
            messages.success(request, "Successfully changed Systemic Vision "
                                      "Comment value.")
            return True
        except Exception as e:
            messages.error(request, "Failed to change Systemic Vision Comment "
                                    "value")
            messages.debug(request, str(e))
            return False

    elif field_name == "mid_term_status":
        try:
            status_object = models.TeamStatus.objects.get(team=team_object)
            status_object.mid_term = request.POST[field_name]
            status_object.save()
            update = UpdateWarnings(team_object)
            tw = team_object.warnings
            tw.mid_term, tw.mid_term_comment = update.mid_term_check()
            tw.save()
            messages.success(request, "Successfully changed Mid Term status "
                                      "value.")
            return True
        except Exception as e:
            messages.error(request, "Failed to change Mid Term "
                                    "status value")
            messages.debug(request, str(e))
            return False

    elif field_name == "mid_term_comment":
        try:
            status_object = models.TeamStatus.objects.get(team=team_object)
            status_object.mid_term_comment = request.POST[field_name]
            status_object.save()
            messages.success(request, "Successfully changed Mid Term Comment "
                                      "value.")
            return True
        except Exception as e:
            messages.error(request, "Failed to change Mid Term "
                                    "Comment value")
            messages.debug(request, str(e))
            return False

    messages.debug(request, "Unknown action " + field_name)
    return False


def update_member_value(request, field_name):
    """
    Updates the member object value. This function is called only by
    update_value when a value related to a member is to be updated. The value
    is sent by a dialog box which contains the form.
    :param request:     Request object that contains all the required values
    :param field_name:  Name of the form field that contains the new value
    :return:            True is successful else False
    """

    # Extract member id from the memeberId string
    member_id = request.POST.get('memberId')

    try:
        member_object = models.Member.objects.get(pk=member_id)
    except models.Member.DoesNotExist:
        messages.error(request, "Failed to update value. Invalid Member id")
        messages.error(request, request.POST)
        return False

    # Change Member comment
    if field_name == "member_comment":
        try:
            member_object.comment = request.POST.get(field_name, "")
            member_object.save()
            flash_message = "Comment for member {} updated "\
                            "successfully".format(member_object.name)
            messages.success(request, flash_message)
            return True
        except Exception as e:
            messages.debug(request, "Failed to update value. " + str(e))
            return False

    elif field_name == 'secondary_role_change':
        try:
            short_name = request.POST.get('secondary_role_change')
            sr_object = models.SecondaryRole.objects.get(short_name=short_name)
            # If member already has role remove it
            if member_object.secondary_role.filter(
                    short_name=short_name).exists():
                member_object.secondary_role.remove(sr_object)
                messages.success(request, "Removed role {} from {}".format(
                    sr_object.role, member_object.name))
            else:
                member_object.secondary_role.add(sr_object)
                messages.success(request, "Added role {} to {}".format(
                    sr_object.role, member_object.name
                ))
            member_object.save()
            return True
        except Exception as e:
            messages.debug(request, "Failed to update value. " + str(e))

    # Change Member role comment
    elif field_name == "role_comment":
        try:
            member_object.role_comment = request.POST.get(field_name, "")
            member_object.save()
            flash_message = "Role Comment for member {} updated " \
                            "successfully".format(member_object.name)
            messages.success(request, flash_message)
            return True
        except Exception as e:
            messages.debug(request, "Failed to update value. " + str(e))
            return False

    # Participates in call status
    elif field_name == "participates_in_call":
        try:
            member_object.participates_in_call = (
                request.POST[field_name] == 'true')
            member_object.save()
            flash_message = "Participates in call status for {} updated "\
                            "successfully".format(member_object.name)
            messages.success(request, flash_message)
            return True
        except Exception as e:
            messages.debug(request, "Failed to update value. " + str(e))
            return False
    messages.debug(request, request.POST)
    return False


def create_email(name, data=''):
    """
    Returns a dictionary with email subject and message
    :param name:    Name of the email template to use
    :param data:    Data to be added to the message
    :return:        Dictionary containing email subject and message
    """
    # Work around to convert EmailTemplate to string with required data
    intro_email_template = EmailTemplate.objects.get(name__icontains=name)
    template = Template(intro_email_template.content)
    context = Context({'data': data})
    message = template.render(context)

    return {
        'subject': intro_email_template.subject,
        'message': message
    }


def send_reminder_email(team, next_date):
    """
    Schedule reminder email on the next_date
    :param team:        Team that should be reminded
    :param next_date:   Next date on which email should be sent
    """
    # Add automatic reminder only if automatic_reminder is true
    if not team.team_status.automatic_reminder:
        return
    url = 'http:/' + team.dashboard.consultant_form_url
    email = create_email('reminder', url)
    # Get all Pulse Checkers and LRPs
    recipients = team.members.filter(Q(secondary_role__short_name="PC") or
                                     Q(role__short_name="LRP")).distinct()
    to = []
    if recipients:
        to = [r['email'] for r in recipients.values('email').all()]
    mail.send(to, subject=email['subject'],
              message=email['message'], scheduled_time=next_date)
