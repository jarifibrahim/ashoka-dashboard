from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import ConsultantSurvey, Member, FellowSurvey


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


class ConsultantSurveyForm(forms.ModelForm):
    """ New survey Form """

    # To get the Yes-No field in the form
    all_prepared = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')))

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team')
        super(ConsultantSurveyForm, self).__init__(*args, **kwargs)
        self.fields['call_date'].widget.attrs['class'] = 'datepicker'
        self.fields['missing_member'].widget = forms.CheckboxSelectMultiple()
        # Add only members that belong to 'team'
        self.fields['missing_member'].queryset = Member.objects.filter(
            team=team)

    class Meta:
        model = ConsultantSurvey
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
            'rating': 'Enter number between 1-10 where 1 represents \
                            "Not Working at all" and 10 represents \
                            "Working Great".',
            'other_comments': 'Is there any other thing you would \
                                like to tell us?',
            'all_prepared': 'Were all participants prepared for the call?',
            'missing_member': 'Who was missing?',
            'document_link': 'Link to current working document.',
            'help': 'Is there anything Ashoka Team can help you with?',
        }


class FellowSurveyForm(forms.ModelForm):
    class Meta:
        model = FellowSurvey
        fields = '__all__'
        exclude = ['submit_date']
        widgets = {
            'comments': forms.Textarea(attrs={'class': 'form-control'}),
            'other_help': forms.Textarea(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'rating': 'Enter number between 1-10 where 1 represents \
                            "Not Working at all" and 10 represents \
                            "Working Great".',
            'comments': "What works? What doesn't work? Did you adapt the \
                        standard advisory process in any way? Are there any \
                        problems with the team?",
            'other_help': "Do you want us to join a call at some point? Any \
                           questions that we could help you answer? Want \
                           Feedback on your ideas? (If you fill out this \
                           field, an email will be sent to the Ashoka \
                           Globalizer team with a notification about your \
                           request. If you do not have any specific request, \
                           please leave this field empty.)"
        }
