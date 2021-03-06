from __future__ import print_function
import pickle
import json
import os.path
import re
import email
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

load_dotenv()

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TO_PHONE_NUMBER = os.getenv("TO_PHONE_NUMBER")
FROM_PHONE_NUMBER = os.getenv("FROM_PHONE_NUMBER")
client = Client(TWILIO_SID, TWILIO_AUTH)


def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    # Call the Gmail API
    results = service.users().messages().list(userId='me', labelIds=['INBOX', 'IMPORTANT', 'SPAM'],
                                              q="application developer interview proceed -decline is:unread", maxResults=20).execute()

    if not results or results['resultSizeEstimate'] == 0:
        print("No new offers found")
    else:
        emails = []
        for email in results['messages']:
            emails.append(service.users().messages().get(
                userId='me', id=email['id'], format="raw").execute())

            if not emails:
                print('No email found with id' + email['id'])
            else:
                emails.sort(key=lambda email: email['internalDate'])

                offers = re.findall(
                    r'\b(\w*offer|invite|interview|congrat(s|ulations)|schedule|title|proceed\w*)\b', emails[0]['snippet'], re.MULTILINE)
                if offers:
                    print(offers)

                    message = client.messages.create(body="You have " + str(
                        len(offers)) + " new offers in your email!", from_=FROM_PHONE_NUMBER, to=TO_PHONE_NUMBER)

                    print(message.sid)


if __name__ == '__main__':
    main()
