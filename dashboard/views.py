from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Dashboards
from .forms import CreateDashboardForm
from django.contrib import messages


@login_required(login_url="login")
def home(request):
    """ The main home page"""
    all_dashboards = Dashboards.objects.all()
    return render(request, "home.html", {'all_dashboards': all_dashboards})


def create_dashboard(request):
    """ New Dashboard Creation page"""
    if request.method == 'POST':
        form = CreateDashboardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New Dashboard Created Successfully')
    else:
        form = CreateDashboardForm()
    return render(request, "create.html", {'form': form})


def details(request, dashboards_id):
    """ Dashboard Display page"""
    return HttpResponse("You're looking at dashboard %s" % dashboards_id)
