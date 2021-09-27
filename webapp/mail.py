import smtplib
import constant
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Mail:
    def send_mail(self, recipients, subject, body):
        msg = MIMEMultipart()
        sender = constant.MAIL_SENDER

        msg['From'] = sender
        msg['To'] = recipients
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        msg.add_header('reply-to', constant.NO_REPLY)
        text = msg.as_string()

        s = smtplib.SMTP(constant.SMTP_SERVER)
        s.sendmail(sender, recipients, text)
        s.quit()
