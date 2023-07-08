from core.mail_connector import GmailClient
import os
from core.GPTAccess import generate_mail_response
from rich.console import Console

# initialize console
console = Console()


console.log("Application Initialization... \nStep: Loading Inbox")

gmail_client = GmailClient("edmondmusiitwa", "credentials.json", "token.json") # Create an instance of the GmailClient class
gmail_client.authenticate() #Authenticate

# delate the inbox her

INBOX = gmail_client.get_cached_inbox()

while True:
    mail_no = input("Email index: ")
    print(f"""
          1. Read Email. \n
          2. Generate Response. \n
          3. Exit.
          """)
    option = int(input("\t Feedback: "))
    
    # read the email
    if option == 1:
        print(INBOX[int(mail_no)])
        
    # generate response for the sender 
    elif option == 2:
        msg = str(INBOX[int(mail_no)])
        print(generate_mail_response(msg))
    
    elif option == 3:
        input("press any key to Continue?")
        os.system('cls')
    
    input("press any key to Continue?")
    os.system('cls')