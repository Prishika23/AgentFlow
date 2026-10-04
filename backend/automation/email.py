import time
import webbrowser
from urllib.parse import quote


def prepare_email(to, subject, body):
    to = str(to).strip(); subject = str(subject).strip(); body = str(body).strip()
    if not to:
        raise ValueError("Email recipient is required.")
    mailto_url = "mailto:" + quote(to) + "?subject=" + quote(subject) + "&body=" + quote(body)
    webbrowser.open(mailto_url)
    time.sleep(3)
    return f"Opened the email composer for {to}. Review it and send it from your email application."


def send_email(to, subject, body):
    return prepare_email(to, subject, body)
