from mcp_server import MCPServer
from selection import Selection


class SelectionMCPServer(MCPServer):

    def __init__(self, name: str, port: int, selection : Selection):
        super().__init__(name, port)
        self.selection = selection

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


# npx @modelcontextprotocol/inspector

