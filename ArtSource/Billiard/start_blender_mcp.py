import bpy
import addon_utils

def start_mcp():
    addon_utils.enable('blender_mcp', default_set=False, persistent=False)
    if not getattr(bpy.context.scene, 'blendermcp_server_running', False):
        bpy.ops.blendermcp.start_server()
    return None

bpy.app.timers.register(start_mcp, first_interval=2.0)
