from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from base64 import urlsafe_b64decode
import os
from httpx import HTTPError
from bs4 import BeautifulSoup
import re
from rich.console import Console
from rich.prompt import Prompt
from .build_context import JsonWriter
import json


console = Console()

class GmailClient:
    def __init__(self, account_holder, credentials_file, token_file):
        self.account_holder = account_holder
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.credentials = None
        self.service = None
        self.cached_inbox = []
        

    def authenticate(self):
        # Load credentials from token file if it exists
        if os.path.exists(self.token_file):
            self.credentials = Credentials.from_authorized_user_file(self.token_file)
        # If there are no valid credentials, let the user log in
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, ["https://www.googleapis.com/auth/gmail.readonly"])
                self.credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_file, "w") as token:
                token.write(self.credentials.to_json())
        # Build the Gmail service
        self.service = build("gmail", "v1", credentials=self.credentials)
        
        # load the inbox
        if os.path.exists(f"{self.account_holder}.json"):
            console.log("Account Already Authenitcated, Would you like to continue")
            opt = Prompt.ask("y|n _:")
            
            if opt == str('y'):
                with open(f"{self.account_holder}.json", "r") as f:
                    self.cached_inbox = json.load(f)
            else:
                console.log("You selected No. \nSelect another option to continue")
                opt = Prompt.ask("""
                                 1. Fetch Inbox \n
                                 2.Exit
                                 """)
                if opt == '1':
                    console.log("Please be patient as we load your inbox")
                    self.fetch_inbox()
                
            
        else:
            self.fetch_inbox()
            try:
                json_writer = JsonWriter(self.cached_inbox, f"{self.account_holder}.json")
                json_writer.write()
            except Exception as ex:
                console.log(ex)
        
    def create_email_body(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            text = re.sub('\s+', ' ', text).strip()

            return (text)
        except TypeError as Tp:
            console.log("This has been skipped becuase of the typeError Below\n", Tp)
            
            # using the os function clears the screen
            os.system('cls')
            console.log('Retriving Inbox inprogress')
    

    def fetch_inbox(self, unread_only=False):
        # Check if the service is authenticated
        if not self.service:
            print("Error: Not authenticated")
            return
        # Get the messages from the inbox
        query = "is:unread" if unread_only else None
        results = self.service.users().messages().list(userId="me", labelIds=["INBOX"], q=query).execute()
        messages = results.get("messages", [])
        # Loop through each message
        for message in messages:
            # Get the message details
            msg = self.service.users().messages().get(userId="me", id=message["id"]).execute()
            # Print the message subject
            
            msg_body = self.create_email_body(self.get_message(msg["id"]))
            sender = self.get_sender(msg["id"])
            snippet = msg["snippet"]
            thread_id = msg["threadId"]
            replies = self.get_replies(thread_id)
            
            _temp_dict = {
                "sender": sender,
                "snippet": snippet,
                "Body": msg_body,
                "Replies": replies
            }
            
            # append the Message to the cached_inbox
            self.cached_inbox.append(_temp_dict)
            
        console.log("Caching Inbox: Completed \nBuilding Emails: Completed \nTotal Emails: ", len(self.cached_inbox))
            
    def get_sender(self, msg_id):
        try:
            message = self.service.users().messages().get(userId="me", id=msg_id).execute()
            payload = message['payload']
            headers = payload['headers']
            # Get the sender from the headers
            for header in headers:
                if header['name'] == 'From':
                    return header['value']
        except HttpError as error: #type: ignore
            print(f'An error occurred: {error}')


    def get_message(self, msg_id):
        try:
            message = self.service.users().messages().get(userId="me", id=msg_id).execute()
            payload = message['payload']
            headers = payload['headers']
            parts = payload.get('parts')
            if parts:
                # If the email has parts, then it is multipart
                # Iterate over the parts and get the part with mimeType 'text/plain'
                for part in parts:
                    filename = part.get('filename')
                    mimeType = part.get('mimeType')
                    file_data = part.get('body').get('data')
                    file_size = part.get('body').get('size')
                    if file_data:
                        text = urlsafe_b64decode(file_data).decode()
                        return text
            else:
                # If the email doesn't have parts, then it is not multipart
                text = urlsafe_b64decode(payload['body']['data']).decode()
                return text
        except HTTPError as error:
            print(f'An error occurred: {error}')
            
    def get_replies(self, thread_id):
        try:
            thread = self.service.users().threads().get(userId='me', id=thread_id).execute()
            messages = thread['messages']
            replies = []
            for message in messages[1:]:
                msg_id = message['id']
                msg = self.service.users().messages().get(userId='me', id=msg_id).execute()
                payload = msg['payload']
                headers = payload['headers']
                subject = [i['value'] for i in headers if i['name'] == 'Subject'][0]
                sender = [i['value'] for i in headers if i['name'] == 'From'][0]
                date = [i['value'] for i in headers if i['name'] == 'Date'][0]
                parts = payload.get('parts')
                if parts:
                    for part in parts:
                        filename = part.get('filename')
                        mimeType = part.get('mimeType')
                        file_data = part.get('body').get('data')
                        file_size = part.get('body').get('size')
                        if file_data:
                            text = urlsafe_b64decode(file_data).decode()
                            reply = {'subject': subject, 'sender': sender, 'date': date, 'text': text}
                            replies.append(reply)
                else:
                    text = urlsafe_b64decode(payload['body']['data']).decode()
                    reply = {'subject': subject, 'sender': sender, 'date': date, 'text': text}
                    replies.append(reply)
            return replies
        except HttpError as error: #type: ignore
            print(f'An error occurred: {error}')

    
    def get_cached_inbox(self):
        return self.cached_inbox


