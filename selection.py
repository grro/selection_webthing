import logging
import yaml
from typing import List
from  pathlib import Path
from datetime import datetime
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
        self.selected_name = None
        self.select(self.selection_names[0])
        self.selected_value = self.__options.get(self.selected_name)
        self.selection_time = datetime.now()
        observer = Observer()
        observer.schedule(self, Path(file).parent, recursive=False)
        observer.start()
        logging.info("selections loaded:\n" + self.info)

    @property
    def info(self) -> str:
        text = ""
        for name in self.selection_names:
            text += ("*" if name == self.selected_name else "") + name + ": " + str(self.__options.get(name)) + "\n"
        return text

    @property
    def selection_names(self) -> List:
        return list(self.__options.keys())

    def select(self, name: str):
        self.selection_time = datetime.now()
        self.select_silent(name)

    def select_silent(self, name: str):
        self.selected_name = name
        self.selected_value = self.__options.get(name)
        self.__notify_listener()
        logging.info(name + " selected (value: " + self.selected_value + ")")
        logging.info(self.info)

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

