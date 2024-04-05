import time
import requests
import subprocess
import shutil
import os
from pprint import pprint
from rcon.source import Client
from DataBase import DataBase
from dotenv import load_dotenv
load_dotenv()


API_KEY: str = os.getenv("API_KEY")
API_ENDPOINT: str = os.getenv("API_ENDPOINT")
RCON_ADDRESS: str = os.getenv("RCON_ADDRESS")
RCON_PORT: int = int(os.getenv("RCON_PORT"))
RCON_PASSWD: str = os.getenv("RCON_PASSWD")
GAME_SERVER_DIR: str = os.getenv("GAME_SERVER_DIR")
db: DataBase = DataBase()


def getLatestDemoFile() -> str:
    targetDir: str = os.path.join(GAME_SERVER_DIR, "csgo")
    files: str = [file for file in os.listdir(targetDir) if file.endswith(".dem")]
    fileData: list = []

    for file in files:
        filePath = os.path.join(targetDir, file)
        modificationTime = os.path.getmtime(filePath)
        fileData.append((file, modificationTime))
    
    fileData = sorted(fileData, key= lambda x: x[1])

    if len(fileData) == 0:
        raise Exception()
    return fileData[-1][0]


def sendFile(fileName: str) -> None:
    filePath: str = os.path.join(os.path.dirname(__file__), "parser", "DemoFiles", "csv", fileName)
    with open(filePath, "rb") as fp:
        req = requests.post(API_ENDPOINT, files={"csvFile": fp}, data={"apikey": API_KEY})
        data = req.json()
        if data["success"]:
            print("Uploaded file for analysis successfully!")
        else:
            print("Failed uploading data")
            print(f"Reason {data["message"]}")


def copyFileToParserBucket(fileName: str) -> None:
    srcPath: str = os.path.join(GAME_SERVER_DIR, "csgo", fileName)
    destPath: str = os.path.join(os.path.dirname(__file__), "parser", "DemoFiles", "Demos")
    shutil.copy2(srcPath, destPath)


def deleteAllFilesInFolder(folderPath: str) -> None:
    for file in os.listdir(folderPath):
        if not (file.endswith(".dem") ^ file.endswith(".csv")):
            continue

        filePath = os.path.join(folderPath, file)
        try:
            os.remove(filePath)
            print(f"Deleted: {filePath}")
        except Exception as e:
            print(f"Failed to delete {filePath}.\n Exception: {e}")


def deleteParserBucketFiles() -> None:
    targetDir1: str = os.path.join(os.path.dirname(__file__), "parser", "DemoFiles", "Demos")
    targetDir2: str = os.path.join(os.path.dirname(__file__), "parser", "DemoFiles", "csv")
    deleteAllFilesInFolder(targetDir1)
    deleteAllFilesInFolder(targetDir2)


def parseFile() -> str:
    baseDir: str = os.path.dirname(__file__)
    parserDir: str = os.path.join(baseDir, "parser")
    os.chdir(parserDir)
    args = ["py", "main.py"]
    subprocess.run(args)
    os.chdir(baseDir)
    allFiles: list[str] = os.listdir(os.path.join(parserDir, "DemoFiles", "csv"))
    targetFile: str = [file for file in allFiles if file.endswith(".csv")][0]
    return targetFile


def runLoop():
    try:
        with Client(RCON_ADDRESS, RCON_PORT, passwd=RCON_PASSWD) as client:
            response: str = client.run('users')
    except Exception as e:
        print("Unable to connect to game server.")
        return
    
    userCount: int = int(response[-8:-6])

    if userCount > 0:
        print("Match is in progress...")
        return
    
    try:
        fileName: str = getLatestDemoFile()
    except Exception:
        print("No File Available to send...")
        return

    if db.exists(fileName):
        print("File already sent...")
        return
    
    print(f"Target Acquired: {fileName}")
    print("Copying file to parser bucket...")    
    copyFileToParserBucket(fileName)

    print("Parsing File...")
    parsedFile: str = parseFile()

    print(f"Sending file: {parsedFile}...")
    try:
        sendFile(parsedFile)
    except Exception as e:
        print(f"Failed to send file {parsedFile}")
        print(e)
        return
    
    print("File Sent Successfully.")
    print("Performing cleanup...")
    deleteParserBucketFiles()
    db.insert(fileName)
    print("Cleanup Done.")


def main():
    while True:
        runLoop()
        time.sleep(10)


if __name__ == "__main__":
    main()