import time
import requests
import subprocess
import shutil
import os
from rcon.source import Client
from DataBase import DataBase
from dotenv import load_dotenv
load_dotenv()

MY_ENV_VAR = os.getenv('MY_ENV_VAR')


API_KEY: str = os.getenv("API_KEY")
API_ENDPOINT: str = os.getenv("API_ENDPOINT")
RCON_ADDRESS: str = os.getenv("RCON_ADDRESS")
RCON_PORT: str = os.getenv("RCON_PORT")
RCON_PASSWD: str = os.getenv("RCON_PASSWD")
GAME_SERVER_DIR: str = os.getenv("GAME_SERVER_DIR")
db: DataBase = DataBase()


def getLatestDemoFile() -> str:
    pass


def sendFile(filePath: str) -> None:
    with open(filePath, "rb") as fp:
        req = requests.post(API_ENDPOINT, files={"match.csv": fp}, data={"apikey": API_KEY})


def copyFileToParserBucket(fileName: str) -> None:
    srcPath: str = os.path.join(GAME_SERVER_DIR, "csgo", fileName)
    destPath: str = os.path.join(os.path.dirname(__file__), "parser", "DemoFiles", "Demos")
    shutil.copy2(srcPath, destPath)


def deleteParserBucketFiles() -> None:
    pass


def parseFile() -> None:
    baseDir: str = os.path.dirname(__file__)
    parserDir: str = os.path.join(baseDir, "parser")
    os.chdir(parserDir)
    args = ["py", "main.py"]
    subprocess.run(args)
    print("DONE")
    os.chdir(baseDir)


def runLoop():
    try:
        with Client(RCON_ADDRESS, RCON_PORT, passwd=RCON_PASSWD) as client:
            response = client.run('users')
    except Exception:
        print("Unable to connect to game server.")
        return
    
    if not response:  # game is not stopped
        return
    
    try:
        fileName: str = getLatestDemoFile()
    except Exception:
        print("No File Available to send...")
        return
    
    if db.exists(fileName):
        print("File already sent...")
        return

    copyFileToParserBucket(fileName)


    print("Parsing File...")
    parseFile(fileName)

    print(f"Sending file: {fileName}")

    try:
        sendFile(fileName)
    except Exception:
        print(f"Failed to send file {fileName}")
        return
    
    db.insert(fileName)


def main():
    while True:
        runLoop(db)
        time.sleep(30)

if __name__ == "__main__":
    # main()
    parseFile()