import smtplib
from email.message import EmailMessage
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.api_key import get_api_key
def send_email(recipients, subject, body, smtp_server='smtp.gmail.com', smtp_port=587):

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
  
    if isinstance(recipients, list):
        msg['To'] = ', '.join(recipients)
    else:
        msg['To'] = recipients

    try:
        sender = get_api_key('email')
        password = get_api_key('pass')
        print(sender)
        print(password)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()          
            server.login(sender, password)
            server.send_message(msg)

        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# usage:
if __name__ == "__main__":
    recipient_emails = ["krishnasubedi219@gmail.com"]
    subject = "Test Email"
    body = "This is a test email sent from Python!"

    send_email(recipient_emails, subject, body)
