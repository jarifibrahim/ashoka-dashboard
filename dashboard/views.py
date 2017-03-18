from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Dashboard, Team, Data, AdvisoryPhase, TeamStatus, \
    WeekWarning, TeamWarning
from . import forms
from .utility import *
from django.http import HttpResponse, Http404, JsonResponse
import datetime


@login_required
def home(request):
    """ The main home page """
    all_dashboards = Dashboard.objects.all().order_by('id')
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
            request, 'No Teams found in this dashboard. '
                     'Please create some teams.')
        return render(request, "dashboard_display.html")
    all_teams = dashboard.teams.order_by('id').all()
    team_list, lrp_list, working_document = (list() for _ in range(3))
    consultant_requests, fellow_requests = (list() for _ in range(2))
    lrp_comment_and_teamid, status_and_teamid = (list() for _ in range(2))
    team_warnings = list()
    for team in all_teams:
        # Create new team status if it does not exits
        try:
            ad_onboard = team.team_status.get_advisor_on_display()
        except TeamStatus.DoesNotExist:
            ts = TeamStatus(team=team)
            ts.save()
            ad_onboard = team.team_status.get_advisor_on_display()
        team_list.append({
            'teamid': team.id,
            'name': team.name,
            'advisor_on': ad_onboard,
            'kick_off': team.team_status.get_kick_off_display(),
            'sys_vision': team.team_status.get_sys_vision_display(),
            'mid_term': team.team_status.get_mid_term_display(),
        })

        role_members = team.members.filter(role__short_name="LRP")
        lrp_list.append(', '.join([str(i) for i in role_members]))
        working_document.append(team.working_document)
        consultant_requests.append(team.consultant_request)
        fellow_requests.append(team.fellow_request)
        status_and_teamid.append({
            'teamid': team.id,
            'status_color': team.status_color,
            'status_choice': team.status_choice,
        })
        lrp_comment_and_teamid.append({
            'teamid': team.id,
            'comment': team.lrp_comment
        })
        # Create new team warnings if it does not exits
        try:
            team_warnings.append(team.warnings)
        except TeamWarning.DoesNotExist:
            tw = TeamWarning(team=team)
            tw.save()
            team_warnings.append(team.warnings)
    dates = {
        'start_date': dashboard.advisory_start_date,
        'end_date': dashboard.advisory_end_date,
        'total_weeks': dashboard.total_weeks,
        'current_week': dashboard.current_week,
    }
    progress_percentage = int(
        (dates['current_week'] / dates['total_weeks']) * 100)
    context = {
        'teams': team_list,
        'LRPs': lrp_list,
        'working_document': working_document,
        'consultant_request': consultant_requests,
        'fellow_requests': fellow_requests,
        'status': status_and_teamid,
        'lrp_comment': lrp_comment_and_teamid,
        'dates': dates,
        'team_warnings': team_warnings,
        'progress_percentage': progress_percentage,
        'dashboard': dashboard
    }
    return render(request, "dashboard_display.html", context=context)


def consultant_submit(request, hash_value):
    """ Consultant Survey from request and response """
    dashboard = Data.decode_data(hash_value)
    get_object_or_404(Dashboard, pk=int(dashboard))
    if request.method == 'POST':
        form = forms.ConsultantSurveyForm(request.POST)
        if form.is_valid():
            team_object = form.cleaned_data['team']
            # It is necessary to save the object without commit
            # and then add the team id
            entry = form.save(commit=False)
            # Form does not contain team id. So add it.
            entry.team = team_object
            # Save new instance
            entry.save()
            # Save many to many data from the Form
            form.save_m2m()
            # Increase missing call count for each missing member
            for m in form.cleaned_data['missing_member']:
                m.missed_calls += 1
                m.save()
            # Send email to LRP if there is a request in the response
            if form.cleaned_data['help']:
                email = create_email("consultant", form.cleaned_data['help'])
                all_emails = team_object.members.filter(
                    role__short_name="LRP").all().values('email')
                to = [e['email'] for e in all_emails]
                now = datetime.datetime.now()
                now_plus_15 = now + datetime.timedelta(minutes=15)
                mail.send(to, subject=email['subject'],
                          message=email['message'], scheduled_time=now_plus_15)
        return redirect(reverse(thanks))
    else:
        form = forms.ConsultantSurveyForm()
    return render(request, "survey_template.html",
                  context={'cs': True,
                           'form': form})


def thanks(request):
    """ Survey response acknowledgement page """
    return render(request, "thank_you.html")


def fellow_submit(request, hash_value):
    """ Fellow Survey from request and response """
    dashboard_id = Data.decode_data(hash_value)
    get_object_or_404(Dashboard, pk=dashboard_id)
    if request.method == "POST":
        form = forms.FellowSurveyForm(request.POST)
        if form.is_valid():
            form.save()
            # Send email to LRP if there is a request in the response
            if form.cleaned_data['other_help']:
                email = create_email("fellow", form.cleaned_data['other_help'])
                team_object = form.cleaned_data['team']
                all_emails = team_object.members.filter(
                    role__short_name="LRP").all().values('email')
                to = [e['email'] for e in all_emails]
                now = datetime.datetime.now()
                now_plus_15 = now + datetime.timedelta(minutes=15)
                mail.send(to, subject=email['subject'],
                          message=email['message'], scheduled_time=now_plus_15)
        return redirect(reverse(thanks))
    else:
        form = forms.FellowSurveyForm()
    return render(request, "survey_template.html", context={'form': form})


@login_required
def show_urls(request):
    """ Show all form urls """
    dashboards = Dashboard.objects.all()
    survey_urls = list()
    for d in dashboards:
        survey_urls.append(
            dict(name=d.name, f_url=d.fellow_form_url, c_url=d.consultant_form_url))
    return render(request, "show_urls.html",
                  context={'survey_urls': survey_urls})


@login_required
def update_status(request):
    """
    Update dashboard values. Request is sent via dialog boxes on the
    dashboard page.
    """
    if request.method == "GET":
        return redirect('index')
    # Contains possible fields that can be changed
    # Format:
    #    field to be changed: form field id
    possible_status_change = {
        'advisor_onboarding_status': 'advisor_onboarding_status',
        'kick_off_status': 'kick_off_status',
        'sys_vision_status': 'sys_vision_status',
        'mid_term_status': 'mid_term_status',
        'advisor_onboarding_comment': 'advisor_onboarding_comment',
        'kick_off_comment': 'kick_off_comment',
        'sys_vision_comment': 'sys_vision_comment',
        'mid_term_comment': 'mid_term_comment',
        'change_calls_count': 'change_calls_count',
        'Automatic Reminder Status': 'automatic_reminder_status',
    }

    for change, name in possible_status_change.items():
        if name in request.POST:
            return JsonResponse(update_team_status_value(request, name))
    return JsonResponse(
        {"message": "Error: Unknown action.", 'status': 'error'})


@login_required
def update_team(request):
    if request.method == "GET":
        return redirect('index')

    # Contains possible fields that can be changed
    # Format:
    #    field to be changed: form field id
    possible_team_change = {
        'Team Status Color': 'newStatusColor',
        'LRP Comment': 'LRPComment'
    }
    for change, name in possible_team_change.items():
        if name in request.POST:
            status = update_team_value(request, name)
            return JsonResponse(status)
    return JsonResponse(
        {"message": "Error: Unknown action.", 'status': 'error'})


@login_required
def update_member(request):
    if request.method == "GET":
        return redirect('index')

    possible_member_change = {
        'Member_comment': 'member_comment',
        'secondary_role_change': 'secondary_role_change',
        'role_comment': 'role_comment',
        'participates_in_call': 'participates_in_call'
    }
    for change, name in possible_member_change.items():
        if name in request.POST:
            return JsonResponse(update_member_value(request, name))
    return {
        "message": "Error: Unknown action.",
        "status": "error"
    }


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
    absolute_url = request.build_absolute_uri(
        team_object.dashboard.consultant_form_url)
    r_email = create_email("reminder", absolute_url)
    w_email = create_email("welcome", absolute_url)
    lr = team_object.last_response
    total_calls = team_object.consultant_surveys.all().count()
    current_week = WeekWarning.objects.filter(
        week_number=team_object.dashboard.current_week).values('calls_r')
    expected_calls = current_week[0].get('calls_r',
                                         '') if current_week else None
    calls = {
        'total': total_calls,
        'expected': int(expected_calls) + 1 if expected_calls else 0
    }
    context = {
        'team': team_object,
        'team_members': team_object.members.all().order_by('role_id'),
        'team_status': team_status,
        'c_responses': team_object.consultant_surveys.all().order_by('id'),
        'f_responses': team_object.fellow_surveys.all().order_by('id'),
        'welcome_email': w_email,
        'reminder_email': r_email,
        'team_warnings': team_object.warnings,
        'last_response': lr.submit_date if lr else '',
        'calls': calls
    }
    return render(request, "team_display.html", context=context)


@login_required
def send_email(request):
    """
    Sends email to a list of recipients. All required data is received
    from a Form.
    """
    if request.method == "GET":
        return redirect(reverse(home))
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
    mail.send(
        to,
        subject=subject,
        message=body,
        priority='now',
    )

    return redirect(request.META.get('HTTP_REFERER', 'index'))


@login_required
def show_warnings(request):
    warnings = list(WeekWarning.objects.all().order_by('week_number'))
    phases = list(AdvisoryPhase.objects.all().order_by('phase_number'))
    return render(request, 'show_warnings.html', context={
        'warnings': warnings, 'phases': phases})


def get_members(request):
    """
    Handles the AJAX request sent by the Consultant survey form.
    :returns: list of members
    """
    if request.is_ajax():
        try:
            team_id = request.POST.get('team_id')
            try:
                team_id = int(team_id)
            except ValueError:
                return HttpResponse("Invalid Team ID: ", team_id)
            team = get_object_or_404(Team, pk=team_id)
            member_list = list(team.members.filter(
                participates_in_call=True).values('name', 'id'))
            if not member_list:
                return HttpResponse("No Team members found")
            return HttpResponse(str(member_list))
        except Exception as e:
            return HttpResponse(e)  # incorrect post
    else:
        raise Http404


@login_required
def refresh_team_warnings(request):
    """
    Handles the AJAX request sent from the dashboard page to refresh team
    warnings.
    """
    if request.is_ajax():
        try:
            dashboard_id = request.POST.get('dashboard_id')
            try:
                dashboard_id = int(dashboard_id)
            except ValueError:
                return HttpResponse("Invalid Dashboard ID: ", dashboard_id)
            dashboard = get_object_or_404(Dashboard, pk=dashboard_id)
            for team in dashboard.teams.all():
                update_warnings_object = UpdateWarnings(team)
                update_warnings_object.check_all_warnings()
            return HttpResponse(
                "Warnings related to all teams refreshed successfully")
        except Exception as e:
            return HttpResponse(e)  # incorrect post
    else:
        raise Http404
