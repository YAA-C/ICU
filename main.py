import time
import requests
from rcon.source import Client
from DataBase import DataBase


API_KEY: str = None
API_ENDPOINT: str = None
db: DataBase = DataBase()


def getLatestDemoFile() -> str:
    pass


def sendFile(filePath: str) -> None:
    with open(filePath, "rb") as fp:
        req = requests.post(API_ENDPOINT, files={"match.csv": fp}, data={"API_KEY": API_KEY})


def runLoop():
    try:
        with Client('127.0.0.1', 5000, passwd='123') as client:
            response = client.run('users')
    except Exception:
        print("Unable to connect to game server.")
        return
    
    if not response:
        return
    
    try:
        filePath: str = getLatestDemoFile()
    except Exception:
        print("No File Available to send...")
        return
    
    if db.exists(filePath):
        print("File already sent...")
        return

    print(f"Sending file: {filePath}")

    try:
        sendFile(filePath)
    except Exception:
        print(f"Failed to send file {filePath}")
        return
    
    db.insert(filePath)


def main():
    while True:
        runLoop(db)
        time.sleep(30)

if __name__ == "__main__":
    main()