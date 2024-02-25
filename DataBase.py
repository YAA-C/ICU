import os

class DataBase:
    def __init__(self) -> None:
        self.dbName: str = "db.db"
        self.dbFilePath: str = f"{os.getcwd()}/{self.dbName}"
        self.data: set = set()
        self.loadDB()


    def loadDB(self) -> None:
        if not os.path.isfile(self.dbFilePath):
            return
        
        doneFiles: list = []
        with open(self.dbFilePath, "r") as fp:
            doneFiles.extend([line[:-1] for line in fp.readlines()])
        self.data = set(doneFiles)

    
    def insert(self, fileName: str) -> None:
        self.data.add(fileName)
        with open(self.dbFilePath, "a") as fp:
            fp.write(f"{fileName}\n")


    def exists(self, fileName: str) -> bool:
        return fileName in self.data