from django.contrib import admin
from .models import Dashboard, Team, Member, Role, AdvisoryPhase


# Inline models can be edited from other model's change page
# Team model can be modified from Dashboard model change page
class TeamInline(admin.TabularInline):
    model = Team


class MemberInline(admin.TabularInline):
    model = Member


class DashboardAdmin(admin.ModelAdmin):
    def get_team(self, obj):
        return [str(o) for o in obj.team_set.all()]

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
    inlines = [
        MemberInline
    ]
    # Columns displayed on the model view page
    list_display = ['name', 'get_dashboard', ]
    search_fields = ['name','dashboard__name']
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
    list_display = ['name', 'get_team', 'get_dashboard', 'get_role']
    search_fields = ['name', 'team__name', 'role__long_name']
    list_filter = ['name', 'team__name', 'role__long_name']

# Register your models here.
admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Role)
admin.site.register(AdvisoryPhase)