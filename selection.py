from time import sleep
import logging
import yaml
from typing import List
from threading import Thread
from  pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



class BackToDefaultTimer:

    def __init__(self, selection, back_to_default_sec: int):
        self.__selection = selection
        self.__back_to_default_sec = back_to_default_sec

    def start(self):
        Thread(target=self.__run, daemon=True).start()

    def __run(self):
        while True:
            now = datetime.now()
            elapsed = (now - self.__selection.selection_time).total_seconds()
            if elapsed >= self.__back_to_default_sec:
                default_name = self.__selection.selection_names[0]
                if self.__selection.selected_name != default_name:
                    logging.info(f"back to default selection '{default_name}' after {self.__back_to_default_sec} seconds")
                    self.__selection.select(default_name)
            try:
                sleep_time = max(1, self.__back_to_default_sec - elapsed)
                sleep(sleep_time)
            except Exception:
                pass
            sleep(2)


class Selection(FileSystemEventHandler):

    def __init__(self, file: str, back_to_default_sec: int):
        self.__listener = lambda: None    # "empty" listener
        self.__options = dict()
        self.__selections = dict()
        self.__file = file
        logging.info("using config file " + self.__file)
        self.__parse()
        self.selected_name = self.selection_names[0]
        self.selected_value = self.__options.get(self.selected_name)
        self.selection_time = datetime.now()
        observer = Observer()
        observer.schedule(self, Path(file).parent, recursive=False)
        observer.start()
        logging.info("back to default activated: " + str(back_to_default_sec) + " seconds (" + self.__options.get(self.selection_names[0]) + ")" if back_to_default_sec is not None else "back to default deactivated")
        if back_to_default_sec < 60*60*24*365:
            BackToDefaultTimer(self, back_to_default_sec).start()

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




