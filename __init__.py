# only import if running as a custom node
try:
	import comfy.utils
except ImportError:
	pass
else:
	WEB_DIRECTORY = "./web"
	NODE_CLASS_MAPPINGS = {}

	# main nodes (no deps)
	from .nodes.mod import NODE_CLASS_MAPPINGS as mod_nodes
	NODE_CLASS_MAPPINGS.update(mod_nodes)

	# pypng dep
	try:
		import png
	except ImportError:
		print("ColorMod: Can't find pypng! Please install to enable 16bit image support.")
	else:
		# 10bit PNG nodes
		from .nodes.save_png import NODE_CLASS_MAPPINGS as save_png_nodes
		NODE_CLASS_MAPPINGS.update(save_png_nodes)

	# cv2 dep
	try:
		import cv2
	except ImportError:
		print("ColorMod: Can't find opencv! Please install to enable HDR/tonemapping support.")
	else:
		# HDR creation/etc nodes
		from .nodes.hdr import NODE_CLASS_MAPPINGS as hdr_nodes
		NODE_CLASS_MAPPINGS.update(hdr_nodes)
		
		# HDR save/load nodes
		from .nodes.save_hdr import NODE_CLASS_MAPPINGS as save_hdr_nodes
		NODE_CLASS_MAPPINGS.update(save_hdr_nodes)

	# export
	NODE_DISPLAY_NAME_MAPPINGS = {k:v.TITLE for k,v in NODE_CLASS_MAPPINGS.items()}
	__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
