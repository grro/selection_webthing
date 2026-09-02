import asyncio
import logging
import threading
import socket
from threading import Thread
from time import sleep
from typing import List, Dict, Any, Optional, Callable

from fastmcp import FastMCP
from pydantic import AnyUrl, TypeAdapter
from zeroconf import IPVersion, ServiceInfo, Zeroconf

from selection import Selection


logger = logging.getLogger(__name__)


class MDNS:
    def __init__(self):
        self.registered: Dict[str, ServiceInfo] = dict()
        self.zc = Zeroconf(ip_version=IPVersion.V4Only)
        self.service_type = "_mcp._tcp.local."
        self.hostname = socket.gethostname()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            self.local_ip = s.getsockname()[0]
        finally:
            s.close()

    def register_mdns(self, name: str, port: int):
        try:
            service_name = f"{name}.{self.service_type}"
            service_info = ServiceInfo(
                type_=self.service_type,
                name=service_name,
                addresses=[socket.inet_aton(self.local_ip)],
                port=port,
                properties={
                    "version": "1.0",
                    "path": "/sse",
                    "server_type": "fastmcp"
                },
                server=f"{self.hostname}.local.",
            )

            logging.info(f"mDNS: Registering {service_name} at {self.local_ip}:{port}")
            self.zc.register_service(service_info)
            self.registered[name] = service_info
        except Exception as e:
            logging.error(f"mDNS Registration failed: {e}")

    def unregister_mdns(self, name: str):
        service_info = self.registered.get(name)
        if service_info is not None:
            logging.info("mDNS: Unregistering service...")
            self.zc.unregister_service(service_info)
            self.zc.close()



class SelectionMCPServer:

    def __init__(self, port: int, name: str, selection : Selection, host: str = "0.0.0.0"):
        self.name = name
        self.host = host
        self.port = port
        self.selection = selection

        self.mdns = MDNS()
        self.mcp = FastMCP(self.name)

        self.is_running = True

        self._setup_mcp()


    def _setup_mcp(self):

        @self.mcp.resource("selection://list/names")
        def list_valid_names() -> str:
            """Returns a comma-separated list of all available selection names."""
            return ", ".join(self.selection.selection_names)

        @self.mcp.resource("selection://current/name")
        def get_selected_name() -> str:
            """Returns the name of the currently selected item."""
            return str(self.selection.selected_name)

        @self.mcp.resource("selection://current/value")
        def get_selected_value() -> str:
            """Returns the value associated with the current selection."""
            return str(self.selection.selected_value)

        @self.mcp.resource("selection://current/selection_time")
        def get_selection_time() -> str:
            """Returns the ISO timestamp of the last selection change."""
            return self.selection.selection_time.strftime("%Y-%m-%dT%H:%M:%S")

        @self.mcp.tool()
        def select_item(name: str) -> str:
            """
            Changes the active selection.
            Args:
                name: The name of the item to select.
            """
            if name in self.selection.selection_names:
                self.selection.select(name)
                return f"Successfully selected: {name}"
            else:
                valid = ", ".join(self.selection.selection_names)
                return f"Error: '{name}' is not valid. Choose from: {valid}"

        @self.mcp.tool()
        def select_silent_item(name: str) -> str:
            """
            Changes the active selection silently.
            Args:
                name: The name of the item to select.
            """
            if name in self.selection.selection_names:
                self.selection.select_silent(name)
                return f"Successfully selected: {name}"
            else:
                valid = ", ".join(self.selection.selection_names)
                return f"Error: '{name}' is not valid. Choose from: {valid}"


    async def __run(self) -> None:
        logger.info(f"MCP Server '{self.name}' running on http://{self.host}:{self.port}/sse")
        await self.mcp.run_async(transport="sse", host=self.host, port=self.port)


    def start(self):
        self.mdns.register_mdns(self.name, self.port)

        def _run_loop():
            asyncio.set_event_loop(self.loop)
            try:
                self.loop.run_until_complete(self.__run())
            finally:
                self.loop.close()

        thread = threading.Thread(target=_run_loop, daemon=True)
        thread.start()


    def stop(self):
        self.mdns.unregister_mdns(self.name)
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.is_running = False
        logging.info("MCP Server stopped")



