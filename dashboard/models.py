from django.db import models


class Dashboard(models.Model):
    name = models.CharField("Dashboard Name", max_length=200, unique=True)
    create_date = models.DateTimeField("Dashboard Create Date", auto_now_add=True)
    total_teams = models.IntegerField("Total number of teams")
    advisory_start_date = models.DateField("Start date of Advisory Process")
    advisory_end_date = models.DateField("End date of Advisory Process")

    class Meta:
        verbose_name_plural = "Dashboards"
        verbose_name = "Dashboard"

    def __str__(self):
        return self.name

    def _get_total_weeks(self):
        delta = self.advisory_end_date - self.advisory_start_date
        return delta.days // 7

    total_weeks = property(_get_total_weeks)


class Team(models.Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    name = models.CharField("Team Name", max_length=200, unique=True)
    total_members = models.IntegerField("Total Number of members in Team")


class Member(models.Model):
    ROLE1 = ("LRP", "LRP")
    ROLE2 = ("SA", "Senior Advisor")
    ROLE3 = ("SC", "Senior Consultant")
    ROLE4 = ("JC", "Junior Consultant")
    ROLE5 = ("C", "Consultant")
    ROLE6 = ("F", "Fellow")
    ROLE7 = ("FC", "Fellow Colleague")
    name = models.CharField("Name", max_length=200)
    email = models.CharField("Email", max_length=200)
    ROLE_CHOICES = (ROLE1, ROLE2, ROLE3, ROLE4, ROLE5, ROLE6, ROLE7)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
