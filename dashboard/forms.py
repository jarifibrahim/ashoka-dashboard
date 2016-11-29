from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from .models import Dashboard, FellowSurvey
from django.utils.translation import ugettext_lazy as _


class LoginForm(AuthenticationForm):
    """ Main Login Form """
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
    """ New Dashboard Creation Form """

    class Meta:
        model = Dashboard
        fields = ["name", "advisory_start_date", "advisory_end_date"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'Dashboard Name'}),
            'advisory_end_date': AdminDateWidget(attrs={'class': 'vDateField form-control'}),
            'advisory_start_date': AdminDateWidget(attrs={'class': 'vDateField form-control'}),
        }
        labels = {
            'name': _('Name of the Dashboard'),
            'advisory_end_date': _('End date of advisory process'),
            'advisory_start_date': _('Start date of advisory process'),
        }
        error_messages = {
            'name': {
                'unique': _('Dashboard with the provided name already exists.'),
            }
        }

    def clean(self):
        """ Check start and end advisory dates """
        super(CreateDashboardForm, self).clean()
        form_start_date = self.cleaned_data.get('advisory_start_date')
        form_end_date = self.cleaned_data.get('advisory_end_date')
        # Continue only if date is valid
        if form_end_date and form_start_date:
            # Start date should before end date
            if form_start_date > form_end_date:
                raise forms.ValidationError(_('Advisory start date cannot be after advisory end date.'),
                                            code='invalid')
            if form_start_date == form_end_date:
                raise forms.ValidationError(_('Advisory start date cannot be equal to advisory end date.'),
                                            code='invalid')


class SurveyForm(forms.ModelForm):
    """ New survey Form """
    class Meta:
        model = FellowSurvey
        fields = '__all__'
        exclude = ['submit_date']