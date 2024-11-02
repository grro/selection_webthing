import yaml
from typing import List
from  pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Options(FileSystemEventHandler):

    def __init__(self, file: str):
        self.__selections = dict()
        self.__file = file
        self.__parse()
        observer = Observer()
        observer.schedule(self, Path(file).parent, recursive=False)
        observer.start()


    def names(self) -> List[str]:
        return list(self.__selections.keys())

    def value(self, name: str) -> str:
        return self.__selections.get(name)

    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.__file:
            print("file " + self.__file + " has been modified")
            self.__parse()

    def __parse(self):
        with open(self.__file, 'r') as file:
            conf = yaml.safe_load(file)
            self.__selections = dict(conf)
            print(self.__file + " (re)loaded " + str(self.__selections))
