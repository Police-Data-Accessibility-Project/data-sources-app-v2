import json
import os

import requests

from middleware.util import get_env_variable


def post_to_webhook(msg: str):
    vite_vue_app_base_url = get_env_variable("VITE_VUE_APP_BASE_URL")
    webhook_url = get_env_variable("WEBHOOK_URL")

    requests.post(
        url=webhook_url,
        data=f"({vite_vue_app_base_url}) {msg}",
        headers={"Content-Type": "application/json"},
        timeout=5,
    )


def send_password_reset_link(email, token):
    body = (
        f"To reset your password, click the following link: "
        f"{get_env_variable('VITE_VUE_APP_BASE_URL')}/reset-password/{token}"
    )
    r = requests.post(
        "https://api.mailgun.net/v3/mail.pdap.io/messages",
        auth=("api", get_env_variable("MAILGUN_KEY")),
        data={
            "from": "mail@pdap.io",
            "to": [email],
            "subject": "PDAP Data Sources Reset Password",
            "text": body,
        },
        timeout=5,
    )
