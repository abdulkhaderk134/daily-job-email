import os
import base64
import requests
import datetime
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build

# === CONFIG ===
SEARCH_URL = "https://wellfound.com/jobs?description=entry+level+software+engineer&sort=recent"
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SERVICE_ACCOUNT_FILE = 'service-account.json'
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = 'abdulkhaderk134@gmail.com'

def fetch_jobs():
    jobs = []
    try:
        resp = requests.get(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"})
        text = resp.text
        for line in text.splitlines():
            if "/job/" in line and "title=" in line:
                start = line.find('href="') + 6
                end = line.find('"', start)
                url = line[start:end]
                title = line[line.find("title=")+7:].split('"')[0]
                jobs.append({
                    "title": title,
                    "company": "Wellfound Startup",
                    "location": "Remote / India",
                    "link": "https://wellfound.com" + url
                })
        return jobs[:10]
    except Exception as e:
        return [{"title": "Error fetching jobs", "company": str(e), "location": "", "link": ""}]

def create_message(body, subject):
    msg = MIMEText(body)
    msg['to'] = RECIPIENT_EMAIL
    msg['from'] = SENDER_EMAIL
    msg['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}

def send_email(service, message):
    service.users().messages().send(userId="me", body=message).execute()

def main():
    jobs = fetch_jobs()
    now = datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")
    subject = f"🔍 Entry-Level SWE Jobs on Wellfound — {now}"
    body = "\n\n".join(
        f"{j['title']} @ {j['company']} ({j['location']})\n{j['link']}" for j in jobs
    )

    service_account_info = os.getenv("SERVICE_ACCOUNT_JSON").replace("\\n", "\n")
    with open("service-account.json", "w") as f:
        f.write(service_account_info)

    creds = service_account.Credentials.from_service_account_file(
        "service-account.json", scopes=SCOPES)
    delegated = creds.with_subject(SENDER_EMAIL)
    service = build('gmail', 'v1', credentials=delegated)

    send_email(service, create_message(body, subject))

if __name__ == "__main__":
    main()
