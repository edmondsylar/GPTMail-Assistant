import json
from rich.console import Console

con = Console()

class JsonWriter:
    def __init__(self, data, filename):
        self.data = data
        self.filename = filename

    def write(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)
            
        # close the file
        f.close()
        con.log("Inbox account file Created Successfully")
