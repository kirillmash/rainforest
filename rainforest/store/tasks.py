import csv
import os
from datetime import datetime

from django.conf import settings
from celery import shared_task
from django.core.mail import EmailMessage

from .services import get_data_for_report


@shared_task
def create_task_report(date_start: str, date_end: str, email: str) -> None:
    """Task for generate report in csv format and send on email"""
    today = datetime.now().strftime('%d-%m-%Y %H-%M-%S')
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    data, column_names = get_data_for_report(date_start, date_end)

    file_name = f"{today}_report.csv"
    full_path = os.path.join(settings.MEDIA_ROOT, file_name)

    with open(full_path, 'w') as f:
        report_file = csv.writer(f, delimiter=';')
        report_file.writerow(column_names)
        report_file.writerows(data)
    email_message = EmailMessage(
        'Hello, this is report for you',
        today,
        settings.EMAIL_HOST_USER,
        [email],
    )

    with open(full_path, 'r') as f:
        email_message.attach(filename=file_name, content=f.read(), mimetype='text/csv')
        email_message.send()

    os.remove(full_path)
