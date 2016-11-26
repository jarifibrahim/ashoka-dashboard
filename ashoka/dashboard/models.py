from django.db import models


class Dashboards(models.Model):
    dashboard_name = models.CharField("Dashboard Name", max_length=200, unique=True)
    create_date = models.DateTimeField("Dashboard Create Date", auto_now=True)
    number_of_teams = models.IntegerField("Number of teams")
    advisory_start_date = models.DateField("Start date of Advisory Process")
    advisory_end_date = models.DateField("End date of Advisory Process")

    def __str__(self):
        return self.dashboard_name

    def _get_total_weeks(self):
        delta = self.advisory_end_date - self.advisory_start_date
        return delta.days//7

    total_weeks = property(_get_total_weeks)
