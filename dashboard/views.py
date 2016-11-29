from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Dashboard
from .forms import CreateDashboardForm, SurveyForm
from django.contrib import messages


@login_required(login_url="login")
def home(request):
    """ The main home page"""
    all_dashboards = Dashboard.objects.all()
    context = {
        'all_dashboards': all_dashboards
    }
    return render(request, "home.html", context=context)


@login_required
def create_dashboard(request):
    """ New Dashboard Creation page"""
    if request.method == 'POST':
        form = CreateDashboardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New Dashboard Created Successfully')
    else:
        form = CreateDashboardForm()
    context = {
        'form': form
    }
    return render(request, "create_dashboard.html", context=context)


@login_required
def details(request, dashboards_id):
    """ Dashboard Display page"""
    dashboard = Dashboard.objects.get(id=dashboards_id)
    if not dashboard.teams.all():
        messages.success(request, 'No Teams found in this dashboard. Please create teams')
    context = {
        'nteams': range(dashboard.team_count)
    }
    return render(request, "dashboard_display.html", context=context)


@login_required
def fellow_submit(request):
    """ New Dashboard Creation page"""
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Response Saved Successfully')
    else:
        form = SurveyForm()
    context = {
        'form': form
    }
    return render(request, "fellow_survey.html", context=context)
