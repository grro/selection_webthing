import logging
import yaml
from typing import List
from  pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



class Selection(FileSystemEventHandler):

    def __init__(self, file: str):
        self.__listener = lambda: None    # "empty" listener
        self.__options = dict()
        self.__selections = dict()
        self.__file = file
        logging.info("using config file " + self.__file)
        self.__parse()
        self.selected_name = self.selection_names[0]
        self.selected_value = self.__options.get(self.selected_name)
        observer = Observer()
        observer.schedule(self, Path(file).parent, recursive=False)
        observer.start()

    @property
    def selection_names(self) -> List:
        return sorted(list(self.__options.keys()))

    def select(self, name: str):
        self.selected_name = name
        self.selected_value = self.__options.get(name)
        logging.info(name + " selected (value: " + self.selected_value + ")")
        self.__notify_listener()

    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.__file:
            logging.info("file " + self.__file + " has been modified")
            self.__parse()
            self.__notify_listener()

    def __parse(self):
        with open(self.__file, 'r') as file:
            conf = yaml.safe_load(file)
            self.__options = dict(conf)
            logging.info(self.__file + " (re)loaded " + str(self.__options))

    def set_listener(self,listener):
        self.__listener = listener
        self.__notify_listener()

    def __notify_listener(self):
        self.__listener()




