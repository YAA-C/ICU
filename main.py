import time
import requests
from rcon.source import Client
from DataBase import DataBase
import os
from dotenv import load_dotenv
load_dotenv()

MY_ENV_VAR = os.getenv('MY_ENV_VAR')


API_KEY: str = os.getenv("API_KEY")
API_ENDPOINT: str = os.getenv("API_ENDPOINT")
RCON_ADDRESS: str = os.getenv("RCON_ADDRESS")
RCON_PASSWD: str = os.getenv("RCON_PASSWD")
GAME_SERVER_DIR: str = os.getenv("GAME_SERVER_DIR")
db: DataBase = DataBase()


def getLatestDemoFile() -> str:
    pass


def sendFile(filePath: str) -> None:
    with open(filePath, "rb") as fp:
        req = requests.post(API_ENDPOINT, files={"match.csv": fp}, data={"apikey": API_KEY})


def runLoop():
    try:
        with Client(RCON_ADDRESS, 5000, passwd=RCON_PASSWD) as client:
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