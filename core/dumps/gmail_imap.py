# Import the imaplib module
import imaplib

# Define a function that takes an email address and a password as parameters
def get_unread_emails(email, password):
    # Connect to the Gmail IMAP server using SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # Login with the email address and password
    imap.login(email, password)
    # Select the inbox folder
    imap.select("INBOX")
    # Search for unread messages using the UNSEEN flag
    status, data = imap.search(None, "UNSEEN")
    # Check if the search was successful
    if status == "OK":
        # Get the list of message numbers
        msg_nums = data[0].split()
        # Loop through each message number
        for num in msg_nums:
            # Fetch the message header and body using the RFC822 protocol
            status, data = imap.fetch(num, "(RFC822)")
            # Check if the fetch was successful
            if status == "OK":
                # Get the message content as bytes
                msg_bytes = data[0][1]
                # Decode the message content as string
                msg_str = msg_bytes.decode()
                # Print the message content
                print(msg_str)
                print("-" * 80)
    # Logout from the IMAP server
    imap.logout()


# text the function

email = ""
password = ""

# get_unread_emails(email, password)