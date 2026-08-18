import os
import sys
import traceback
import requests
from auth import get_access_token, GRAPH_SCOPE
import base64 as b
from datetime import date
from dotenv import load_dotenv

from main import main

load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

def _send_email(recipient_emails, subject, body_text, attachment_path=None):
    token = get_access_token(GRAPH_SCOPE)
    to_recipients = [
        {"emailAddress": {"address": email.strip()}}
        for email in recipient_emails.split(",")
        if email.strip()
    ]

    message = {
        "subject": subject,
        "body": {
            "contentType": "Text",
            "content": body_text
        },
        "toRecipients": to_recipients,
    }

    if attachment_path:
        with open(attachment_path, 'rb') as f:
            encoded_content = b.b64encode(f.read()).decode('utf-8')
        message["attachments"] = [
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": os.path.basename(attachment_path),
                "contentBytes": encoded_content
            }
        ]

    url = f"https://graph.microsoft.com/v1.0/users/{SENDER_EMAIL}/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    return requests.post(url, headers=headers, json={"message": message})


def send_report_email(recipient_emails, filepath):
    today = date.today()
    body = (
        "Buenos días, \n \n"
        f"Adjunto el reporte de cobertura de materia prima correspondiente al {today.strftime('%d/%m/%Y')}.\n \n"
        "Saludos, \n"
        "Reporte automático — Megaplast"
    )

    response = _send_email(
        recipient_emails,
        f'Reporte de Cobertura de Materia Prima - {today.strftime("%d/%m/%Y")}',
        body,
        attachment_path=filepath,
    )

    if response.status_code != 202:
        raise RuntimeError(f"Failed to send report email: {response.status_code} - {response.text}")

    print("Email sent successfully")
    os.remove(filepath)


def send_failure_alert(recipient_emails, error_message):
    today = date.today()
    body = (
        "El reporte automático de cobertura de materia prima no se pudo generar hoy "
        f"({today.strftime('%d/%m/%Y')}).\n \n"
        "Detalle del error:\n"
        f"{error_message}\n \n"
        "Reporte automático — Megaplast"
    )

    response = _send_email(
        recipient_emails,
        f'⚠️ Error al generar el Reporte de Cobertura - {today.strftime("%d/%m/%Y")}',
        body,
    )

    if response.status_code != 202:
        raise RuntimeError(f"Failed to send failure alert: {response.status_code} - {response.text}")

    print("Failure alert sent")


if __name__ == "__main__":
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    try:
        filepath = main()
        send_report_email(recipient_email, filepath)
    except Exception:
        error_message = traceback.format_exc()
        print(error_message)
        try:
            send_failure_alert(recipient_email, error_message)
        except Exception as alert_error:
            print(f"Also failed to send failure alert: {alert_error}")
        sys.exit(1)
