import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from shared.notificator.notificator import Notificator

class EmailNotificator(Notificator):
    def __init__(self, receiver, subject = os.getenv('SUBJECT_MESSAGE')):
        super().__init__()

        self.receiver = receiver
        self.subject = subject

    def notify(self, text):
        smtp_host = os.getenv('SMTP_PROVIDER')
        smtp_port = os.getenv('SMTP_PORT')
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')

        message = MIMEMultipart()

        message['From'] = smtp_username
        message['To'] = self.receiver
        message['Subject'] = self.subject

        message.attach(MIMEText(text, 'html'))

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as provider:
                provider.starttls()
                provider.login(smtp_username, smtp_password)
                
                provider.sendmail(smtp_username, self.receiver, message.as_string())

        except smtplib.SMTPException as error:
            print(f'[PARROT ERROR] Unable to send the email to the address {self.receiver}: {error}')