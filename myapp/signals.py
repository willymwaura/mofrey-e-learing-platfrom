

from .models import MofrexUsers
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from dict import settings
import logging



@receiver(post_save, sender=MofrexUsers)
def thankyou(sender, instance, **kwargs):
    
    try:
        user_email = instance.email
        subject = 'Thank you'
        message = 'Thank you for signing up , Welcome to Mofrey Markets.'   
        from_email = settings.EMAIL_HOST_USER   
        recipient_list = [user_email]
        #print("sending email")
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        logging.error(f"Failed to send email. Error message: {str(e)}")