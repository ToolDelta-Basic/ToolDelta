from tooldelta.plugin_manager import plugin_manager
import tooldelta

if 1:
    tooldelta.start_tool_delta()
else:
    plugin_manager.manage_plugins()
