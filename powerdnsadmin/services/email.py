from flask import current_app, render_template, url_for
from flask_mail import Message

from ..models.setting import Setting
from .token import generate_confirmation_token


def send_account_verification(user_email):
    """
    Send welcome message for the new registration
    """
    try:
        token = generate_confirmation_token(user_email)
        verification_link = url_for("index.confirm_email", token=token, _external=True)

        subject = "Welcome to {}".format(Setting().get("site_name"))
        msg = Message(subject=subject)
        msg.recipients = [user_email]
        msg.body = "Please access the following link verify your email address. {}".format(verification_link)
        msg.html = render_template("emails/account_verification.html", verification_link=verification_link)
        current_app.mail.send(msg)
    except Exception:
        current_app.logger.exception("Cannot send account verification email")
