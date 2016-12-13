from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Dashboard, Team, Data, AdvisoryPhase, TeamStatus, WeekWarning
from . import forms
from .utility import *


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
            request, 'No Teams found in this dashboard. Please create teams')

    all_teams = dashboard.teams.order_by('id').all()
    team_list, lrp_list, working_document = (list() for _ in range(3))
    consultant_requests, fellow_requests = (list() for _ in range(2))
    lrp_comment_and_teamid, status_and_teamid = (list() for _ in range(2))
    team_warnings = list()
    for team in all_teams:
        team_list.append({
            'teamid': team.id,
            'name': team.name
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
        'progress_percentage': progress_percentage
    }
    return render(request, "dashboard_display.html", context=context)


@login_required
def consultant_submit(request, hash_value):
    """ Consultant Survey from request and response """
    team_id = Data.decode_data(hash_value)
    team_object = get_object_or_404(Team, pk=team_id)
    if request.method == 'POST':
        form = forms.ConsultantSurveyForm(request.POST, team=team_id)
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
            messages.success(request, 'Your Response has been saved '
                                      'Successfully. Thank you!')
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
                from_email = "jarifibrahim@gmail.com"
                mail.send(to, from_email, subject=email['subject'],
                          message=email['message'])
                messages.success(request,
                                 "Email with your request will be sent to LRP.")
        return redirect(reverse(thanks))
    else:
        form = forms.ConsultantSurveyForm(team=team_id)
    return render(request, "survey_template.html",
                  context={'team': team_object.name,
                           'form': form})


@login_required
def thanks(request):
    """ Survey response acknowledgement page """
    return render(request, "thank_you.html")


@login_required
def fellow_submit(request, hash_value):
    """ Fellow Survey from request and response """
    dashboard_id = Data.decode_data(hash_value)
    get_object_or_404(Dashboard, pk=dashboard_id)
    if request.method == "POST":
        form = forms.FellowSurveyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your Response has been saved '
                                      'Successfully. Thank you!')

            # Send email to LRP if there is a request in the response
            if form.cleaned_data['other_help']:
                email = create_email("fellow", form.cleaned_data['other_help'])
                team_object = form.cleaned_data['team']
                all_emails = team_object.members.filter(
                    role__short_name="LRP").all().values('email')
                to = [e['email'] for e in all_emails]
                from_email = "jarifibrahim@gmail.com"
                mail.send(to, from_email, subject=email['subject'],
                          message=email['message'])
                messages.success(request,
                                 "Email with your request will be sent to LRP.")
        return redirect(reverse(thanks))
    else:
        form = forms.FellowSurveyForm()
    return render(request, "survey_template.html", context={'form': form})


@login_required
def show_urls(request):
    """ Show all form urls """
    dashboards = Dashboard.objects.all()
    fellow_survey_urls = list()
    for d in dashboards:
        fellow_survey_urls.append(dict(name=d.name, url=d.fellow_form_url))
    teams = Team.objects.all().order_by('id')
    consultant_survey_urls = list()
    for t in teams:
        consultant_survey_urls.append(
            dict(name=t.name, url=t.consultant_form_url))

    return render(request, "show_urls.html",
                  context={'f_urls': fellow_survey_urls,
                           'c_urls': consultant_survey_urls})


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
        'secondary_role_change': 'secondary_role_change',
        'role_comment': 'role_comment',
        'participates_in_call': 'participates_in_call'
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
    absolute_url = request.build_absolute_uri(team_object.consultant_form_url)
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
        'expected': int(expected_calls) + 1
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
        "jarifibrahim@gmail.com",
        subject=subject,
        message=body,
        priority='now',
    )

    return redirect(request.META.get('HTTP_REFERER', 'index'))


@login_required
def show_warnings(request):
    warnings = list(WeekWarning.objects.all())
    phases = list(AdvisoryPhase.objects.all())
    return render(request, 'show_warnings.html', context={
        'warnings': warnings, 'phases': phases})
