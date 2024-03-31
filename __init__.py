# only import if running as a custom node
try:
	import comfy.utils
except ImportError:
	pass
else:
	NODE_CLASS_MAPPINGS = {}

	# main nodes (no deps)
	from .nodes.mod import NODE_CLASS_MAPPINGS as mod_nodes
	NODE_CLASS_MAPPINGS.update(mod_nodes)

	# 10bit PNG nodes
	try:
		import png
	except ImportError:
		print("ColorMod: Can't find pypng! Please install to enable 16bit image support.")
	else:
		from .nodes.save import NODE_CLASS_MAPPINGS as save_nodes
		NODE_CLASS_MAPPINGS.update(save_nodes)

	# export
	WEB_DIRECTORY = "./web"
	NODE_DISPLAY_NAME_MAPPINGS = {k:v.TITLE for k,v in NODE_CLASS_MAPPINGS.items()}
	__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
