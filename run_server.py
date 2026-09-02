import sys
import logging
from webthing import (SingleThing, Property, Thing, Value, WebThingServer)
from selection import Selection
from selection_web import SelectionWebServer
from selection_mcp import SelectionMCPServer
from selection_webthing import SelectionThing





def run_server(description: str, port: int, config_file: str):
    selection = Selection(config_file)
    web_server = SelectionWebServer(selection, port=port+1)
    mcp_server = SelectionMCPServer(name="cam", selection=selection, port=port+2)
    server = WebThingServer(SingleThing(SelectionThing(description, selection)), port=port, disable_host_validation=True)
    try:
        logging.info('starting the server http://localhost:' + str(port))
        web_server.start()
        mcp_server.start()
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        web_server.stop()
        mcp_server.stop()
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(name)-20s: %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger('tornado.access').setLevel(logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('mcp.server.lowlevel.server').setLevel(logging.WARNING)
    run_server("description", int(sys.argv[1]), sys.argv[2])
