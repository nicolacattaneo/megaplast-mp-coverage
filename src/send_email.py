import os
import requests
from auth import get_access_token, GRAPH_SCOPE
import base64 as b
from datetime import date
from dotenv import load_dotenv

from main import main

load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

def send_report_email(recipient_emails, filepath):
    token = get_access_token(GRAPH_SCOPE)
    to_recipients = [
        {"emailAddress": {"address": email.strip()}}
        for email in recipient_emails.split(",")
        if email.strip()
    ]

    with open(filepath, 'rb') as f:
        file_bytes = f.read()
        encoded_content = b.b64encode(file_bytes).decode('utf-8')

    url = f"https://graph.microsoft.com/v1.0/users/{SENDER_EMAIL}/sendMail"
    headers = {
        "Authorization" : f"Bearer {token}",
        "Content-Type" : "application/json"
    }

    today = date.today()

    email_body = {
        "message": {
            "subject": f'Reporte de Cobertura de Materia Prima - {today.strftime("%d/%m/%Y")}',
            "body": {
                "contentType": "Text",
                "content": "Buenos días, \n \n"
                            f"Adjunto el reporte de cobertura de materia prima correspondiente al {today.strftime("%d/%m/%Y")}.\n \n"
                            "Saludos, \n"
                            "Reporte automático — Megaplast"
            },
            "toRecipients": to_recipients,
            "attachments": [
                {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": f"cobertura_mp_{date.today().isoformat()}.xlsx",
                    "contentBytes": encoded_content
                }
            ]
        }
    }    

    response = requests.post(url, headers=headers, json=email_body)

    if response.status_code != 202:
        print(f"Failed to send email: {response.status_code}")
        print(response.text)
    else:
        print("Email sent successfully")
        os.remove(filepath)

if __name__ == "__main__":
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    send_report_email(recipient_email, main())

