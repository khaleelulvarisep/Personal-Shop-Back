from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


def send_otp_email(email, otp, otp_validity_minutes):
    send_mail(
        subject="Your OTP for registration",
        message=f"Your OTP is {otp}. It is valid for {otp_validity_minutes} minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task(bind=True, ignore_result=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_otp_email_task(self, email, otp, otp_validity_minutes):
    send_otp_email(email, otp, otp_validity_minutes)
