from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Dashboard, Team
from .forms import SurveyForm
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect


@login_required(login_url="login")
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


def fellow_submit(request, hash_value):
    """ Survey from request and response """
    team_id = Team.decode_form_url(hash_value)
    team_object = get_object_or_404(Team, id=team_id)
    if request.method == 'POST':
        form = SurveyForm(request.POST, team=team_id)
        if form.is_valid():
            # It is necessary to save the object without commit
            # and then add the team id
            entry = form.save(commit=False)
            # Form does not contain team id. So add it.
            entry.team = team_object
            entry.save()
            messages.success(request, 'Response Saved Successfully')
            return HttpResponseRedirect(reverse(thanks))
    else:
        form = SurveyForm(team=team_id)
        return render(request, "fellow_survey.html",
                      context={'team': team_object.name,
                               'form': form})


def thanks(request):
    """ Fellow survey form acknowledgement page """
    return render(request, "thank_you.html")
