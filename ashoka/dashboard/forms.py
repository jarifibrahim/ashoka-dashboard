from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Dashboards
from django.utils.translation import ugettext_lazy as _


class LoginForm(AuthenticationForm):
    """ Main Login Form"""
    username = forms.CharField(label="Username", max_length=30,
                               widget=forms.TextInput(attrs={
                                   "class": "form-control",
                                   "name": "username",
                                   "placeholder": "Password"}))
    password = forms.CharField(label="Password", max_length=30,
                               widget=forms.PasswordInput(attrs={
                                   "class": "form-control",
                                   "name": "password",
                                   "placeholder": "Password"}))


class CreateDashboardForm(forms.ModelForm):
    """ New Dashboard Creation Form"""
    class Meta:
        model = Dashboards
        fields = ["dashboard_name", "number_of_teams", "advisory_start_date", "advisory_end_date"]
        widgets = {
            'dashboard_name': forms.TextInput(attrs={'class': 'form-control',
                                                     'placeholder': 'Dashboard Name'}),
            'number_of_teams': forms.TextInput(attrs={'class': 'form-control',
                                                      'type': 'number',
                                                      'placeholder': 'Total Number of Teams'}),
            'advisory_end_date': forms.SelectDateWidget,
            'advisory_start_date': forms.SelectDateWidget,
        }
        labels = {
            'dashboard_name': _('Name of the Dashboard'),
            'number_of_teams': _('Total Number of Teams'),
            'advisory_end_date': _('End date of advisory process'),
            'advisory_start_date': _('Start date of advisory process'),
        }
        error_messages = {
            'dashboard_name': {
                'unique': _('Dashboard with the provided name already exists.'),
            }
        }

    def clean(self):
        """ Check start and end advisory dates """
        form_start_date = self.cleaned_data.get('advisory_start_date')
        form_end_date = self.cleaned_data.get('advisory_end_date')
        if form_start_date > form_end_date:
            raise forms.ValidationError(_('Advisory start date cannot be after advisory end date.'),
                                        code='invalid')
        if form_start_date == form_end_date:
            raise forms.ValidationError(_('Advisory start date cannot be equal to advisory end date.'),
                                        code='invalid')

        super(CreateDashboardForm, self).clean()