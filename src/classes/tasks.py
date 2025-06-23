"""
Tasks for sending reminders about live classes.
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mass_mail
from django.utils.timezone import localtime

from classes.models import LiveClass
from courses.models import Enrollment

logger = get_task_logger(__name__)


@shared_task
def send_class_reminder_email(live_class_id):
    """
    Send reminder emails for a live class.
    """
    live_class = LiveClass.objects.select_related("course").filter(id=live_class_id).first()
    if not live_class:
        logger.error(f"The live class with ID {live_class_id} does not exist.")
        return

    if live_class.is_canceled:
        return "ClassCanceled"

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
        messages.append(
            (
                subject,
                message,
                "no-reply@yourdomain.com",
                [enrollment.student.email],
            )
        )

    send_mass_mail(messages)
    return f"Sent {len(messages)} reminders."
