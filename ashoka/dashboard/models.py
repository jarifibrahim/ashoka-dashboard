from django.db import models


# Create your models here.
class Dashboards(models.Model):
    dashboard_name = models.CharField(max_length=200)
    create_date = models.DateTimeField('Dashboard Creation Date.')
    in_use = models.BooleanField()

    def __str__(self):
        return self.dashboard_name
