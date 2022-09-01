
from typing import Dict, Any

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from django.core.mail import EmailMessage


def send_mail_func(email_body: Dict[str, Any]):
    """
    Send mail function to the specified email
    """
    print(email_body)
    try:
        html = render_to_string('accounts/mail_body.html', {
            'message': email_body['messages']
        })
        subject = email_body['subject']
        message = email_body['messages']
        email_from = settings.EMAIL_HOST_USER
        recipient_list = email_body['recipients']

        # mail = send_mail(subject, message, email_from,
        #                  recipient_list, html_message=html)
        print('got here')
        mail = EmailMessage(
            subject, email_body['messages'], to=[recipient_list])
        mail.send()
        print(1, mail)
        return True

    except Exception as e:
        print(e)
        return False
