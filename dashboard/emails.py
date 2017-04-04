from post_office.models import EmailTemplate
from django.template import Context, Template
from post_office import mail
import datetime


def create_email(name, data=''):
    """
    Returns a dictionary with email subject and message
    :param name:    Name of the email template to use
    :param data:    Data to be added to the message
    :return:        Dictionary containing email subject and message
    """
    # Work around to convert EmailTemplate to string with required data
    intro_email_template = EmailTemplate.objects.get(name__icontains=name)
    template = Template(intro_email_template.content)
    context = Context({'data': data})
    message = template.render(context)

    return {
        'subject': intro_email_template.subject,
        'message': message
    }


def send_request_email(team_object, request, template_name):
    """
    Send request email to LRP
    :param team_object: Django team object
    :param request: Request to be sent to LRP
    :param template_name: Name of the template to use.
    """
    all_emails = team_object.members.filter(
        role__short_name="LRP").all().values('email')
    now = datetime.datetime.now()
    now_plus_5 = now + datetime.timedelta(minutes=5)
    mail.send(
        [e['email'] for e in all_emails],
        template=template_name,
        context={
            'team': team_object.name,
            'request': request,
        },
        scheduled_time=now_plus_5)
