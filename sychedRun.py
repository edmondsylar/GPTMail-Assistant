import asyncio
from halo import Halo


async def fetch_inbox_with_spinner(gmail_client):
    # Create a spinner
    spinner = Halo(text="Fetching inbox", spinner="dots")
    # Start the spinner
    spinner.start()
    # Run the fetch_inbox function
    await loop.run_in_executor(None, gmail_client.fetch_inbox)
    # Stop the spinner
    spinner.stop()

# Create an instance of the GmailClient class
gmail_client = GmailClient("credentials.json", "token.json")
# Authenticate with Gmail
gmail_client.authenticate()

# Create an asyncio event loop
loop = asyncio.get_event_loop()
# Run the fetch_inbox_with_spinner function
loop.run_until_complete(fetch_inbox_with_spinner(gmail_client))
# Close the event loop
loop.close()
