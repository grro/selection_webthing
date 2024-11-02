import logging
from typing import List
from options import Options



class Selection:

    def __init__(self, options: Options):
        self.__listener = lambda: None    # "empty" listener
        self.__options = options
        self.selected_name = sorted(list(self.__options.names()))[0]
        self.selected_value = self.__options.value(self.selected_name)

    @property
    def selection_names(self) -> List:
        return list(self.__options.names())

    def select(self, name: str):
        self.selected_name = name
        self.selected_value = self.__options.value(name)
        logging.info(name + " selected (value: " + self.selected_value + ")")
        self.__notify_listener()

    def set_listener(self,listener):
        self.__listener = listener

    def __notify_listener(self):
        self.__listener()