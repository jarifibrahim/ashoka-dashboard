from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Dashboard, Team, Member
from .forms import ConsultantSurveyForm, FellowSurveyForm


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
        team_list.append({'teamid': team.id, 'name': team.name})
        lrp_list.append(team.get_members_with_role("LRP"))
        working_document.append(team.working_document)
        consultant_requests.append(team.consultant_request)
        fellow_requests.append(team.fellow_request)
        status_and_teamid.append({'teamid': team.id, 'status': team.status})
        lrp_comment_and_teamid.append(
            {'teamid': team.id, 'comment': team.lrp_comment})

    context = {
        'teams': team_list,
        'LRPs': lrp_list,
        'working_document': working_document,
        'consultant_request': consultant_requests,
        'fellow_requests': fellow_requests,
        'status': status_and_teamid,
        'lrp_comment': lrp_comment_and_teamid,
    }
    return render(request, "dashboard_display.html", context=context)


def encode_data(data):
    """
    Encodes data to generate a hash.
    This hash is used to generate urls

    :param data: The data to be encoded.
    :returns: hash value
    """
    return "%08x" % (data * 387420489 % 4000000000)


def decode_data(data):
    """
    Decodes the data encoded by 'encode_data' function.

    :param data: The hash value to be decoded.
    :returns: original data
    """
    return int(data, 16) * 3513180409 % 4000000000


def consultant_submit(request, hash_value):
    """ Consultant Survey from request and response """
    team_id = decode_data(hash_value)
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
            return HttpResponseRedirect(reverse(thanks))
    else:
        form = ConsultantSurveyForm(team=team_id)
    return render(request, "consultant_survey.html",
                  context={'team': team_object.name,
                           'form': form})


def thanks(request):
    """ Survey response acknowledgement page """
    return render(request, "thank_you.html")


def fellow_submit(request, hash_value):
    """ Fellow Survey from request and response """
    dashboard_id = decode_data(hash_value)
    get_object_or_404(Dashboard, pk=dashboard_id)
    if request.method == "POST":
        form = FellowSurveyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your Response has been saved Successfully. \
                          Thank you!')
            return HttpResponseRedirect(reverse(thanks))
    else:
        form = FellowSurveyForm()
    return render(request, "consultant_survey.html", context={'form': form})


@login_required
def show_urls(request):
    """ Show all form urls """
    dashboard_list = list(
        Dashboard.objects.values_list('id', 'name'))
    fellow_survey_urls = [{
                              'url': encode_data(d_id),
                              'name': name
                          } for d_id, name in dashboard_list]

    team_list = list(
        Team.objects.values_list('id', 'name'))
    consultant_survey_urls = [{
                                  'url': encode_data(t_id),
                                  'name': name
                              } for t_id, name in team_list]

    return render(request, "show_urls.html",
                  context={'f_urls': fellow_survey_urls,
                           'c_urls': consultant_survey_urls})


def update_team_value(request, change_name, change_field_id):
    """
    Updates the team value. This function is called only by update_value when
    a value related to the team is to be updated. The value is sent by a dialog
    form.
    :param request:         Request object that contains all the required values
    :param change_name:     Type of change to be done.
                            Possible values are "status" and "comment"
    :param change_field_id: Id of the form field that contains the new value
    :return:                True is successful else False
    """
    # Extract team id from the teamId string
    team_id = request.POST.get('teamId')
    try:
        team_object = Team.objects.get(pk=team_id)
    except Team.DoesNotExist:
        messages.error(request, "Failed to update value. Invalid team id")
        return False

    # Change Team status color
    if change_name.lower() == "status":
        try:
            team_object.status = request.POST[change_field_id]
            team_object.save()
            messages.success(request, "Team status updated successfully.")
        except Exception as e:
            messages.debug(request, "Failed to update value. " + str(e))
            return False

    # Change Team comment
    elif change_name.lower() == "comment":
        try:
            team_object.lrp_comment = request.POST[change_field_id]
            team_object.save()
            messages.success(request, "Team LRP comment updated successfully")
        except Exception as e:
            messages.debug(request, "Failed to update value. " + str(e))
            return False
    else:
        messages.debug(request, "Unknown action " + change_name)
        return False
    return True


def update_member_value(request, change_name, change_field_id):
    """
    Updates the member object value. This function is called only by
    update_value when a value related to a member is to be updated. The value
    is sent by a dialog box which contains the form.
    :param request:         Request object that contains all the required values
    :param change_name:     Type of change to be done.
                            Possible value is "comment"
    :param change_field_id: Id of the form field that contains the new value
    :return:                True is successful else False
    """

    # Extract member id from the memebrId string
    member_id = request.POST.get('memberId')

    try:
        member_object = Member.objects.get(pk=member_id)
    except Team.DoesNotExist:
        messages.error(request, "Failed to update value. Invalid team id")
        return False

    # Change Team comment
    if change_name.lower() == "comment":
        try:
            member_object.comment = request.POST[change_field_id]
            member_object.save()
            messages.success(request, "Member comment updated successfully")
        except Exception as e:
            messages.debug(request, "Failed to update value. " + str(e))
            return False
        return True
    return False


@login_required
def update_value(request):
    """
    Update dashboard values. Request is sent via dialogue boxes on the
    dashboard page.
    """

    if request.method != "POST":
        HttpResponseRedirect(reverse("index"))

    # Contains possible fields that can be changed
    # Format:
    #    change name: form field id
    possible_field_change = {
        'status': 'newStatusColor',
        'LRP_comment': 'LRPComment',
        'Member_comment': 'memberComment',
    }
    response_url = request.META.get('HTTP_REFERER', 'index')
    messages.debug(request, request.POST)

    # Change team status color
    if possible_field_change['status'] in request.POST:
        status = update_team_value(
            request, 'status', possible_field_change['status'])
        if not status:
            messages.error(request, "Failed to update status value.")

    # Change LRP Comment
    elif possible_field_change['LRP_comment'] in request.POST:
        status = update_team_value(
            request, 'comment', possible_field_change['LRP_comment'])
        if not status:
            messages.error(request, "Failed to update LRP Comment value.")

    # Change Member comment
    elif possible_field_change['Member_comment'] in request.POST:
        status = update_member_value(
            request, 'comment', possible_field_change['Member_comment'])
        if not status:
            messages.error(request, "Failed to update Member Comment value.")

    else:
        messages.error(request, "Error: Unknown action.")
    return HttpResponseRedirect(response_url)


def team_detail(request, team_id):
    team_object = get_object_or_404(Team, pk=team_id)

    context = {
        'teamid': team_object.id,
        'team_name': team_object.name,
        'team_members': team_object.members.all(),
        'consultant_responses': team_object.consultant_surveys.all(),
    }
    return render(request, "team_display.html", context=context)