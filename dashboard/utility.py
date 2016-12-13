from django.contrib import messages
from .models import Team, Member, TeamStatus, SecondaryRole, WeekWarning
from post_office.models import EmailTemplate
from django.template import Context, Template


def check_warnings(team):
    status = {
        'green': 'G',
        'yellow': 'Y',
        'red': 'R'
    }

    current_week = team.dashboard.current_week
    try:
        week_warning = WeekWarning.objects.get(week_number=current_week)
        tw = team.warnings
    except WeekWarning.DoesNotExist:
        raise
    except team.RelatedObjectDoesNotExist:
        raise

    # Total calls check
    def _total_calls_check():
        response_count = team.consultant_surveys.all().count()
        change_count = team.team_status.call_change_count
        total_call_count = response_count + change_count
        if total_call_count < week_warning.calls_r:
            msg = "Total Calls ({0}+{1})={2} < Expected Calls Red: {3}"
            msg = msg.format(response_count, change_count, total_call_count,
                             week_warning.calls_r)
            return status['red'], msg
        elif total_call_count < week_warning.calls_y:
            msg = "Total Calls ({0}+{1})={2} < Expected Calls Yellow: {3}"
            msg = msg.format(response_count, change_count, total_call_count,
                             week_warning.calls_y)
            return status['yellow'], msg
        else:
            msg = "Total Calls ({0}+{1})={2} >= Expected Calls: " \
                  "Yellow:{3} and Red:{4}"
            msg = msg.format(response_count, change_count, total_call_count,
                             week_warning.calls_y, week_warning.calls_r)
            return status['green'], msg

    # Current Phase
    def _phase_check():
        last_response = team.last_response
        # If there are no responses skip the following section
        if last_response:
            current_phase = last_response.current_phase
            yellow = week_warning.phase_y
            red = week_warning.phase_r
            green = week_warning.phase
            if red:
                if current_phase.phase_number <= red.phase_number:
                    msg = "Current Phase:{0} < Red warning Phase:{1}"
                    msg = msg.format(current_phase, red)
                    return status['red'], msg

            if yellow:
                if yellow.phase_number == current_phase.phase_number:
                    msg = "Current Phase:{1} is Yellow warning Phase:{0}"
                    msg = msg.format(yellow, current_phase)
                    return status['yellow'], msg
            if green:
                if green.phase_number == current_phase.phase_number:
                    msg = "Current Phase:{1} is Expected Phase:{0}"
                    msg = msg.format(green, current_phase)
                    return status['green'], msg
        msg = "No consultant responses found!"
        return status['green'], msg

    # Kick Off
    def _kick_off_check():
        if team.team_status.kick_off == "NS":
            yellow = week_warning.kick_off_y
            red = week_warning.kick_off_r
            msg = "Kick off not yet happened"
            if red:
                return status['red'], msg
            if yellow:
                return status['yellow'], msg
            else:
                return status['green'], "No kick off warnings found for this " \
                                        "week. "
        return status['green'], "Kick off Done."

    # Mid Term
    def _mid_term_check():
        if team.team_status.mid_term == "NS":
            yellow = week_warning.mid_term_y
            red = week_warning.mid_term_r
            msg = "Mid Term not yet happened"
            if red:
                return status['red'], msg
            if yellow:
                return status['yellow'], msg
            else:
                return status['green'], "No mid term warnings found for this " \
                                        "week. "
        return status['green'], "Mid Term Done"

    # Consultant Rating
    def _consultant_rating_check():
        c_last_rating = team.last_consultant_rating
        if c_last_rating:
            if c_last_rating <= week_warning.consultant_rating_r:
                msg = "Last Consultant Rating: {0} <= Consultant Rating " \
                      "Red Warning: {1}".format(c_last_rating,
                                                week_warning.consultant_rating_r)
                return status['red'], msg
            else:
                msg = "Last Consultant Rating: {0} > Consultant Rating " \
                      "Red Warning: {1}".format(c_last_rating,
                                                week_warning.consultant_rating_r)
                return status['green'], msg
        # If there are no ratings
        else:
            return status['green'], "No Rating found (Either there are no " \
                                    "consultant responses or none of the " \
                                    "consultant responses have rating value) "

    # Fellow Rating
    def _fellow_rating_check():
        f_last_rating = team.last_fellow_rating
        if f_last_rating:
            if f_last_rating < week_warning.fellow_rating_r:
                msg = "Last Fellow Rating: {0} < Fellow Rating " \
                      "Red Warning: {1}".format(f_last_rating,
                                                week_warning.fellow_rating_r)
                return status['red'], msg
            else:
                msg = "Fellow Rating: {0} > Fellow Rating " \
                      "Red Warning: {1}".format(f_last_rating,
                                                week_warning.fellow_rating_r)
                return status['green'], msg
        # If there are no ratings
        else:
            return status['green'], "No Rating found (Either there are no " \
                                    "fellow responses or none of the " \
                                    "fellow responses have rating value) "

    # Unprepared calls
    def _unprepared_calls_check():
        percentage = team.unprepared_calls_percentage
        if percentage:
            if percentage > week_warning.unprepared_calls_r:
                msg = "% Unprepared calls: {0} > % Unprepared Calls Red " \
                      "Threshold: {1}"
                msg = msg.format(percentage, week_warning.unprepared_calls_r)
                return status['red'], msg
            elif percentage > week_warning.unprepared_calls_y:
                msg = "% Unprepared calls: {0} > % Unprepared Calls Yellow " \
                      "Threshold: {1}"
                msg = msg.format(percentage, week_warning.unprepared_calls_y)
                return status['yellow'], msg
            else:
                msg = "% Unprepared calls: {0} < % Unprepared calls " \
                      "Threshold Yellow:{1} and Red:{2}"
                msg = msg.format(percentage, week_warning.unprepared_calls_y,
                                 week_warning.unprepared_calls_r)
                return status['green'], msg
        msg = ""
        if percentage is 0:
            msg = "% Unprepared calls: 0. Members were prepared for all " \
                  "the calls."
        if percentage is None:
            msg = "Could not calculate % Unprepared calls. " \
                  "No consultant responses found."

        return status['green'], msg

    tw.call_count, tw.call_count_comment = _total_calls_check()
    tw.phase, tw.phase_comment = _phase_check()
    tw.kick_off, tw.kick_off_comment = _kick_off_check()
    tw.mid_term, tw.mid_term_comment = _mid_term_check()
    tw.consultant_rating, tw.consultant_rating_comment = _consultant_rating_check()
    tw.fellow_rating, tw.fellow_rating_comment = _fellow_rating_check()
    tw.unprepared_call, tw.unprepared_call_comment = _unprepared_calls_check()
    tw.save()


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
        team_object = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
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
        team_object = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        messages.error(request, "Failed to update value. Invalid Team id")
        messages.error(request, request.POST)
        return False

    # Change team call count
    if field_name == "change_calls_count":
        try:
            status_object = TeamStatus.objects.get(team=team_object)
            status_object.call_change_count = int(request.POST.get(field_name))
            status_object.save()
            messages.success(request, "Successfully changed call count value.")
            return True
        except Exception as e:
            messages.error(request, "Failed to change call count value.")
            messages.debug(request, str(e))
            return False

    # Change automatic reminder status
    elif field_name == "automatic_reminder_status":
        try:
            status_object = TeamStatus.objects.get(team=team_object)
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

    elif field_name == "kick_off_status":
        try:
            status_object = TeamStatus.objects.get(team=team_object)
            status_object.kick_off = request.POST[field_name]
            status_object.save()
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
            status_object = TeamStatus.objects.get(team=team_object)
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

    elif field_name == "mid_term_status":
        try:
            status_object = TeamStatus.objects.get(team=team_object)
            status_object.mid_term = request.POST[field_name]
            status_object.save()
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
            status_object = TeamStatus.objects.get(team=team_object)
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
        member_object = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        messages.error(request, "Failed to update value. Invalid Member id")
        messages.error(request, request.POST)
        return False

    # Change Member comment
    if field_name == "member_comment":
        try:
            member_object.comment = request.POST.get(field_name, "")
            member_object.save()
            flash_message = "Comment for member {} updated successfully".format(
                member_object.name)
            messages.success(request, flash_message)
            return True
        except Exception as e:
            messages.debug(request, "Failed to update value. " + str(e))
            return False

    elif field_name == "receives_reminder_emails":
        try:
            member_object.receives_survey_reminder_emails = (
                request.POST[field_name].lower() == 'true')
            member_object.save()
            flash_message = "{}'s Reminder Email setting updated " \
                            "successfully".format(member_object.name)
            messages.success(request, flash_message)
            return True
        except Exception as e:
            messages.debug(request, "Failed to update value. " + str(e))

    elif field_name == 'secondary_role_change':
        try:
            short_name = request.POST.get('secondary_role_change')
            sr_object = SecondaryRole.objects.get(short_name=short_name)
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
    messages.debug(request, request.POST)
    return False


def get_email(name, data=''):
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
