import googleapiclient.discovery
import googleapiclient.errors
from pathlib import Path

class apiAsker:
    def __init__(self):
        self.youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=Path('youtubeapikey.txt').read_text())
    def listId(self, id: str):
        return self.youtube.channels().list(part="snippet", id=id).execute()

if __name__ == "__main__":
    theThing = apiAsker()
    print(theThing.listId('UCRUULstZRWS1lDvJBzHnkXA'))