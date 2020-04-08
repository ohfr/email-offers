from __future__ import print_function
import pickle
import json
import os.path
import re
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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
    results = service.users().messages().list(userId='me', labelIds="IMPORTANT", q="application developer interview proceed -decline", maxResults=20).execute()

    # print(results)
    if not results:
        print("No messages found")
    else:
        emails = []
        for email in results['messages']:
            emails.append(service.users().messages().get(userId='me', id=email['id']).execute())
        
            if not emails:
                print('No email found with id' + email['id'])
            else:
                emails.sort(key=lambda email: email['internalDate'])

                # create regex for finding offers or interviews

                print(emails[0]['snippet'])
                offers = re.findall(r'\b(\w*offer|invite|interview|congrat(s|ulations)|schedule|title|proceed\w*)\b', emails[0]['snippet'], re.MULTILINE)
                if offers:
                   print(offers)
                # for offer in emails[0]['snippet']:
                #     z = re.findall(r'\b(\w*offer|invite|interview|congrat(s|ulations)|schedule|title\w*)\b', offer)
                #     if z:
                #         print(z)
            
                # print(json.dumps(offers, indent=4))


if __name__ == '__main__':
    main()