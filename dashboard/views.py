from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Dashboard, Team, Member, SecondaryRole, TeamStatus, Email, \
        Data
from .forms import ConsultantSurveyForm, FellowSurveyForm
from .utility import check_warnings
from django.core.mail import send_mail


@login_required
def home(request):
    """ The main home page """
    all_dashboards = Dashboard.objects.all()
    context = {
        'all_dashboards': all_dashboards
    }
    return render(request, "home.html", context=context)


@login_required
def dashboard_overview(request, dashboard_id):
    """ Dashboard Display page"""
    dashboard = get_object_or_404(Dashboard, id=dashboard_id)
    if not dashboard.teams.all():
        messages.error(
            request, 'No Teams found in this dashboard. Please create teams')

    all_teams = dashboard.teams.all()
    team_list, lrp_list, working_document = (list() for _ in range(3))
    consultant_requests, fellow_requests = (list() for _ in range(2))
    lrp_comment_and_teamid, status_and_teamid = (list() for _ in range(2))

    for team in all_teams:
        team_list.append({
            'teamid': team.id,
            'name': team.name
        })
        lrp_list.append(team.get_members_with_role("LRP"))
        working_document.append(team.working_document)
        consultant_requests.append(team.consultant_request)
        fellow_requests.append(team.fellow_request)
        status_and_teamid.append({
            'teamid': team.id,
            'status': team.status
        })
        lrp_comment_and_teamid.append({
            'teamid': team.id,
            'comment': team.lrp_comment
        })

    dates = {
        'start_date': dashboard.advisory_start_date,
        'end_date': dashboard.advisory_end_date,
        'total_weeks': dashboard.total_weeks,
        'current_week': dashboard.current_week

    }
    context = {
        'teams': team_list,
        'LRPs': lrp_list,
        'working_document': working_document,
        'consultant_request': consultant_requests,
        'fellow_requests': fellow_requests,
        'status': status_and_teamid,
        'lrp_comment': lrp_comment_and_teamid,
        'dates': dates
    }
    return render(request, "dashboard_display.html", context=context)


@login_required
def consultant_submit(request, hash_value):
    """ Consultant Survey from request and response """
    team_id = Data.decode_data(hash_value)
    team_object = get_object_or_404(Team, pk=team_id)
    if request.method == 'POST':
        form = ConsultantSurveyForm(request.POST, team=team_id)
        if form.is_valid():
            # It is necessary to save the object without commit
            # and then add the team id
            entry = form.save(commit=False)
            # Form does not contain team id. So add it.
            entry.team = team_object
            # Save new instance
            entry.save()
            # Save many to many data from the Form
            form.save_m2m()
            messages.success(
                request, 'Your Response has been saved Successfully. \
                          Thank you!')
            return redirect(reverse(thanks))
    else:
        form = ConsultantSurveyForm(team=team_id)
    return render(request, "survey_template.html",
                  context={'team': team_object.name,
                           'form': form})


def thanks(request):
    """ Survey response acknowledgement page """
    return render(request, "thank_you.html")


def fellow_submit(request, hash_value):
    """ Fellow Survey from request and response """
    dashboard_id = Data.decode_data(hash_value)
    get_object_or_404(Dashboard, pk=dashboard_id)
    if request.method == "POST":
        form = FellowSurveyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your Response has been saved Successfully. \
                          Thank you!')
            return redirect(reverse(thanks))
    else:
        form = FellowSurveyForm()
    return render(request, "survey_template.html", context={'form': form})


@login_required
def show_urls(request):
    """ Show all form urls """
    dashboards = Dashboard.objects.all()
    fellow_survey_urls = list()
    for d in dashboards:
        fellow_survey_urls.append(dict(name=d.name, url=d.fellow_form_url))
    teams = Team.objects.all()
    consultant_survey_urls = list()
    for t in teams:
        consultant_survey_urls.append(
            dict(name=t.name, url=t.consultant_form_url))

    return render(request, "show_urls.html",
                  context={'f_urls': fellow_survey_urls,
                           'c_urls': consultant_survey_urls})


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
            team_object.status = request.POST[field_name]
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

    messages.debug(request, request.POST)
    return False


@login_required
def update_value(request):
    """
    Update dashboard values. Request is sent via dialog boxes on the
    dashboard page.
    """
    if request.method == "GET":
        return redirect('index')

    # Contains possible fields that can be changed
    # Format:
    #    field to be changed: form field id
    response_url = request.META.get('HTTP_REFERER', 'index')
    possible_team_change = {
        'Team Status Color': 'newStatusColor',
        'LRP Comment': 'LRPComment'
    }
    possible_member_change = {
        'Member_comment': 'member_comment',
        'receives_reminder_email': 'receives_reminder_emails',
        'secondary_role_change': 'secondary_role_change',
    }
    possible_status_change = {
        'kick_off_status': 'kick_off_status',
        'mid_term_status': 'mid_term_status',
        'kick_off_comment': 'kick_off_comment',
        'mid_term_comment': 'mid_term_comment',
        'change_calls_count': 'change_calls_count',
        'Automatic Reminder Status': 'automatic_reminder_status',
    }

    for change, name in possible_team_change.items():
        if name in request.POST:
            status = update_team_value(request, name)
            if not status:
                messages.error(request, "Failed to update {} value.".format(
                    change))
            return redirect(response_url)

    for change, name in possible_member_change.items():
        if name in request.POST:
            status = update_member_value(request, name)
            if not status:
                messages.error(request, "Failed to update {} value.".format(
                    change))
            return redirect(response_url)

    for change, name in possible_status_change.items():
        if name in request.POST:
            status = update_team_status_value(request, name)
            if not status:
                messages.error(request, "Failed to update {} value.".format(
                    change))
            return redirect(response_url)

    messages.debug(request, request.POST)
    messages.error(request, "Error: Unknown action.")
    return redirect(response_url)


@login_required
def team_detail(request, team_id):
    """
    Display details about the team
    :param team_id: Id of the team
    """
    team_object = get_object_or_404(Team, pk=team_id)

    # Get team status object.
    # Create new object if none found.
    try:
        team_status = team_object.team_status
    except Team.team_status.RelatedObjectDoesNotExist:
        team_status = TeamStatus.objects.create(team=team_object)
        team_status.save()

    check_warnings(team_object)

    intro_email_object = Email.objects.get(type="IM", default_template=True)
    reminder_email_object = Email.objects.get(type="RM", default_template=True)
    context = {
        'team': team_object,
        'team_members': team_object.members.all(),
        'team_status': team_status,
        'consultant_responses': team_object.consultant_surveys.all(),
        'fellow_responses': team_object.fellow_surveys.all(),
        'intro_email': intro_email_object,
        'reminder_email': reminder_email_object,
        'team_warnings': team_object.warnings
    }
    return render(request, "team_display.html", context=context)


def send_email(request):
    """
    Sends email to a list of recipients. All required data is received
    from a Form.
    """
    if request.method == "GET":
        return redirect(reverse(home))
    messages.success(request, request.POST)
    subject = request.POST.get('email_subject', '')
    body = request.POST.get('email_body', '')
    to = request.POST.getlist('send_to')
    if not to:
        messages.error(request, "Please select at least one recipient")
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    elif not subject:
        messages.error(request, "Cannot send email without Subject")
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    elif not body:
        messages.error(request, "Cannot send email without Email Body")
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    send_mail(subject, body, "admin@ashoka.org", to, fail_silently=False)
    return redirect(request.META.get('HTTP_REFERER', 'index'))
