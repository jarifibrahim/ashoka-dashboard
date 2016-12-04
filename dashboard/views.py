from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Dashboard, Team
from .forms import ConsultantSurveyForm, FellowSurveyForm
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect


@login_required
def home(request):
    """ The main home page """
    all_dashboards = Dashboard.objects.all()
    context = {
        'all_dashboards': all_dashboards
    }
    return render(request, "home.html", context=context)


@login_required
def details(request, dashboard_id):
    """ Dashboard Display page"""
    dashboard = get_object_or_404(Dashboard, id=dashboard_id)
    if not dashboard.teams.all():
        messages.error(
            request, 'No Teams found in this dashboard. Please create teams')
    allTeams = dashboard.teams.all()
    context = {
        'teams': [str(t.id) + ": " + str(t.name) for t in allTeams],
        'LRPs': [t.get_members_with_role("LRP") for t in allTeams]
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
    """ Survey from request and response """
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
            entry.save()
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
    dashboard_list = list(
        Dashboard.objects.values_list('id', 'name'))
    fellow_survey_urls = [{
        'url': encode_data(id),
        'name': name
    }for id, name in dashboard_list]

    team_list = list(
        Team.objects.values_list('id', 'name'))
    consultant_survey_urls = [{
        'url': encode_data(id),
        'name': name
    }for id, name in team_list]

    return render(request, "show_urls.html",
                  context={'f_urls': fellow_survey_urls,
                           'c_urls': consultant_survey_urls})
