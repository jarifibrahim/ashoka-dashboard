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


class ConsultantSurveyForm(forms.ModelForm):
    """ New survey Form """

    # To get the Yes-No field in the form
    all_prepared = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=((False, 'No'), (True, 'Yes')))

    def __init__(self, dashboard, *args, **kwargs):
        super(ConsultantSurveyForm, self).__init__(*args, **kwargs)
        team_choices = [(t.id, t.name) for t in dashboard.teams.all()]
        self.fields['team'].choices = [(None, '------')] + team_choices
        self.fields['call_date'].widget.attrs['class'] = 'datepicker'
        self.fields['missing_member'].widget = forms.CheckboxSelectMultiple()

    class Meta:
        model = ConsultantSurvey
        required_css_class = 'required'
        fields = '__all__'
        exclude = ['submit_date']
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
            'missing_member': 'Who was missing? (Please select a Team first)',
            'document_link': 'Link to current working document.',
            'help': 'Is there anything Ashoka Globalizer Team can help you'
                    ' with? (If you fill out this field, an email will be '
                    'sent to the Ashoka Globalizer team with a notification '
                    'about your request. If you do not have any specific '
                    'request, please leave this field empty.)'
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
