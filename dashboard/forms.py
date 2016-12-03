from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import FellowSurvey, Member


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


'''
Removed!!
User can create new dashbaord via admin page

class CreateDashboardForm(forms.ModelForm):
    """ New Dashboard Creation Form """

    class Meta:
        model = Dashboard
        fields = ["name", "advisory_start_date", "advisory_end_date"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'Dashboard Name'}),
            'advisory_end_date': AdminDateWidget(attrs={
                'class': 'vDateField form-control'}),
            'advisory_start_date': AdminDateWidget(attrs={
                'class': 'vDateField form-control'}),
        }
        labels = {
            'name': _('Name of the Dashboard'),
            'advisory_end_date': _('End date of advisory process'),
            'advisory_start_date': _('Start date of advisory process'),
        }
        error_messages = {
            'name': {
                'unique': _('Dashboard with the provided name already \
                    exists.'),
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
                raise forms.ValidationError(_('Advisory start date cannot \
                    be after advisory end date.'), code='invalid')
            if form_start_date == form_end_date:
                raise forms.ValidationError(_('Advisory start date cannot \
                    be equal to advisory end date.'), code='invalid')

'''


class SurveyForm(forms.ModelForm):
    """ New survey Form """

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team')
        super(SurveyForm, self).__init__(*args, **kwargs)
        self.fields['call_date'].widget.attrs['class'] = 'datepicker'
        self.fields['missing_member'].widget = forms.CheckboxSelectMultiple()
        # Add only members that belong to 'team'
        self.fields['missing_member'].queryset = Member.objects.filter(
            team=team)

    class Meta:
        model = FellowSurvey
        required_css_class = 'required'
        fields = '__all__'
        exclude = ['team', 'submit_date']
        widgets = {
            'other_comments': forms.Textarea(attrs={'class': 'form-control'}),
            'document_link': forms.TextInput,
        }
        help_texts = {
            'call_date': 'When did the call take place?',
            'topic_discussed': 'What topics did you discuss?',
            'phase_rating': 'Enter number between 1-10',
            'other_comments': 'Is there any other thing you would \
                                like to tell us?',
            'all_prepared': 'Were all participants prepared for the call?',
            'missing_member': 'Who was missing?',
            'document_link': 'Link to current working document',
            'help': 'Is there anything Ashoka Team can help you with?',
        }
