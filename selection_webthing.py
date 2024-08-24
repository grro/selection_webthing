import sys
import logging
import tornado.ioloop
from webthing import (SingleThing, Property, Thing, Value, WebThingServer)
from selection import Selection
from typing import Dict




class SelectionThing(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing

    def __init__(self, description: str, selection: Selection):

        Thing.__init__(
            self,
            'urn:dev:ops:selection-1',
            'Selection',
            ['MultiLevelSensor'],
            description
        )
        self.ioloop = tornado.ioloop.IOLoop.current()
        self.selection = selection
        self.values = dict()
        self.selection.set_listener(self.on_value_changed)

        self.selected_name = Value(self.selection.selected_name)
        self.add_property(
            Property(self,
                     'selected_name',
                     self.selected_name,
                     metadata={
                         'title': 'selected_name',
                         "type": "string",
                         'description': 'the selected name',
                         'readOnly': True,
                     }))

        self.selected_value = Value(self.selection.selected_value)
        self.add_property(
            Property(self,
                     'selected_value',
                     self.selected_value,
                     metadata={
                         'title': 'selected_value',
                         "type": "string",
                         'description': 'the selected value',
                         'readOnly': True,
                     }))

        for name in self.selection.selection_names:
            value = Value(False, lambda selected: self.selection.select(name, selected))
            self.add_property(
                Property(self,
                         name,
                         value,
                         metadata={
                             'title': name,
                             "type": "boolean",
                             'description': name,
                             'readOnly': False,
                         }))
            self.values[name] = value

    def on_value_changed(self):
        self.ioloop.add_callback(self._on_value_changed)

    def _on_value_changed(self):
        self.selected_name.notify_of_external_update(self.selection.selected_name)
        self.selected_value.notify_of_external_update(self.selection.selected_value)


def run_server(description: str, port: int, selections: Dict[str, str]):
    selection = Selection(selections)
    server = WebThingServer(SingleThing(SelectionThing(description, selection)), port=port, disable_host_validation=True)
    try:
        logging.info('starting the server http://localhost:' + str(port))
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')



def parse_map(text: str) -> Dict[str, str]:
    result = dict()
    for part in text.split("&"):
        station, url = part.strip().split("=")
        result[station.lower()] = url
    return result


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(name)-20s: %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger('tornado.access').setLevel(logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    run_server("description", int(sys.argv[1]), parse_map(sys.argv[2]))
