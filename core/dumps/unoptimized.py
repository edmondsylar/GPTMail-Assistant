from time import sleep
import os.path
import base64
import json 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os


from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailClient:
    def __init__(self, credentials):
        self.credentials = credentials
        self.creds = None

        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        # create the service object
        self.service = build('gmail', 'v1', credentials=self.creds)

    
    # function to get lables
    def get_labels(self):
        results = self.service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        return labels


    # get all unread messages
    def get_unread_messages(self):
        results = self.service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
        messages = results.get('messages', [])
        return messages
    
    # read a message
    def read_message(self, message_id):
        messsage = self.service.users().messages().get(userId='me', id=message_id).execute()
        paylood = messsage['payload']

        if paylood['body']['size'] != 0:

            # print(paylood['body']['data'])
            # input('Press any key to continue')

            body = paylood['body']['data']
            body_decode = base64.urlsafe_b64decode(body).decode('utf-8')
            return (body_decode)


    def send_email(self, to, subject, body):
        try:
            message = MIMEMultipart()
            text = MIMEText(body)
            message.attach(text)

            message['to'] = to
            message['subject'] = subject

            create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
            send_message = (self.service.users().messages().send(userId="me", body=create_message).execute())

            print(F'sent message to {to} Message Id: {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None

        return send_message
        
    

    # get message subject
    def get_subject(self, message_id):
        message = self.service.users().messages().get(userId='me', id=message_id).execute()
        paylood = message['payload']
    # Get the message subject
        payload = message['payload']
        headers = payload['headers']
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
                return subject

    # get basic details [From, date]
    def get_basic_details(self, message_id):
        message = self.service.users().messages().get(userId='me', id=message_id).execute()
        paylood = message['payload']
        headers = paylood['headers']
        for header in headers:
            if header['name'] == 'From':
                from_email = header['value']
            if header['name'] == 'Date':
                date = header['value']
        return (from_email, date)




ai = GmailClient('credentials.json')

print(ai)
    