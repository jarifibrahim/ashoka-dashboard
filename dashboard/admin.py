from django.contrib import admin
from .models import *
from django import forms


# Inline models can be edited from other model's change page
# Team model can be modified from Dashboard model change page
class TeamInline(admin.TabularInline):
    model = Team
    extra = 1


class DashboardAdmin(admin.ModelAdmin):
    def get_team(self, obj):
        return [str(o) for o in obj.teams.all()]

    get_team.short_description = 'Teams'
    # Add team inline model so that it is available for editing
    inlines = [
        TeamInline,
    ]
    list_display = ['name', 'get_team']
    search_fields = ['name']
    list_filter = ['name']


class TeamAdmin(admin.ModelAdmin):
    def get_dashboard(self, obj):
        return obj.dashboard

    get_dashboard.short_description = 'Dashboard'
    # Columns displayed on the model view page
    list_display = ['name', 'get_dashboard', ]
    search_fields = ['name', 'dashboard__name']
    list_filter = ['name', 'dashboard']


class MemberAdmin(admin.ModelAdmin):
    def get_team(self, obj):
        return obj.team

    def get_dashboard(self, obj):
        return obj.team.dashboard

    def get_role(self, obj):
        return obj.role.long_name
    get_dashboard.short_description = "Dashboard"
    get_team.short_description = "Team"
    get_role.short_description = "Role"
    list_display = ['name', 'get_team', 'get_dashboard',
                    'get_role', 'receives_survey_reminder_emails']
    search_fields = ['name', 'team__name', 'role__long_name']
    list_filter = ['team__name', 'role__long_name',
                   'receives_survey_reminder_emails']
    filter_horizontal = ["secondary_role"]


class ConsultantSurveyForm(forms.ModelForm):
    # Filter the missing member list to display only those members that
    # belong to the team
    def __init__(self, *args, **kwargs):
        super(ConsultantSurveyForm, self).__init__(*args, **kwargs)

        teamid = self.instance.team.id
        members = Member.objects.filter(team=teamid)
        w = self.fields['missing_member'].widget
        choices = []
        for choice in members:
            choices.append((choice.id, choice.name))
        w.choices = choices


class ConsultantSurveyAdmin(admin.ModelAdmin):
    filter_horizontal = ["missing_member"]
    list_display = ['id', 'team', 'submit_date', 'call_date']
    form = ConsultantSurveyForm
    list_filter = ['team']

class AdvisoryPhaseAdmin(admin.ModelAdmin):
    list_display = ['phase_number', 'phase']
    ordering = ('phase_number',)


class EmailAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'subject', 'default_template']
    list_filter = ['type']


class WeekWarningAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'phase_y', 'phase_r']
    ordering = ('week_number',)

admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Role)
admin.site.register(AdvisoryPhase, AdvisoryPhaseAdmin)
admin.site.register(ConsultantSurvey, ConsultantSurveyAdmin)
admin.site.register(FellowSurvey)
admin.site.register(SecondaryRole)
admin.site.register(Email, EmailAdmin)
admin.site.register(TeamStatus)
admin.site.register(WeekWarning, WeekWarningAdmin)
admin.site.register(TeamWarning)
