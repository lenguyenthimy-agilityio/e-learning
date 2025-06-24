"""
Tasks for sending reminders about live classes.
"""

from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mass_mail
from django.utils.timezone import localtime

from classes.models import LiveClass
from config.celery import app
from courses.models import Enrollment

logger = get_task_logger(__name__)


@app.task(name="send_class_reminder_email")
def send_class_reminder_email(live_class_id):
    """
    Send reminder emails for a live class.
    """
    live_class = LiveClass.objects.select_related("course").filter(id=live_class_id).first()
    if not live_class:
        logger.error(f"The live class with ID {live_class_id} does not exist.")
        return

    subject = f"Reminder: {live_class.title} is starting soon"
    message = (
        f"Hi,\n\nYou have a live class coming up:\n\n"
        f"Course: {live_class.course.title}\n"
        f"Time: {localtime(live_class.date_time).strftime('%Y-%m-%d %H:%M')}\n"
        f"Link: {live_class.meeting_url}\n\n"
        f"Don't be late!"
    )

    enrollments = Enrollment.objects.select_related("student").filter(course=live_class.course)

    messages = []
    for enrollment in enrollments:
        email = enrollment.student.email
        logger.info(f"Sending reminder email to {email} for live class {live_class.title}")
        messages.append(
            (
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
        )

    send_mass_mail(messages)
    return f"Sent {len(messages)} reminders."
