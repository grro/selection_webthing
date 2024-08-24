import logging
from typing import List, Dict




class Selection:

    def __init__(self, selections: Dict[str, str]):
        self.__listener = lambda: None    # "empty" listener
        self.__selections = selections
        self.selected_name = sorted(list(self.__selections.keys()))[0]
        self.selected_value = self.__selections[self.selected_name]

    @property
    def selection_names(self) -> List:
        return list(self.__selections.keys())

    def select(self, name: str, selected: bool):
        logging.info(name + " selected="  +str(selected))
        if selected:
            self.selected_name = name
            self.selected_value = self.__selections.get(name)
            self.__notify_listener()

    def set_listener(self,listener):
        self.__listener = listener

    def __notify_listener(self):
        self.__listener()