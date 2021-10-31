import smtplib
from email.message import EmailMessage


def send_mail(recipient, subject, message, sender="kingstack08@gmail.com"):
    password = "Tester2008*"

    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    # Send the message via our own SMTP server.
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender, password)
    server.send_message(msg)
    server.quit()
