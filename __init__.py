# only import if running as a custom node
try:
	import comfy.utils
except ImportError:
	pass
else:
	from .colormod import ColorModPivot, ColorModEdges

	NODE_CLASS_MAPPINGS = {
		"ColorModPivot": ColorModPivot,
		"ColorModEdges": ColorModEdges,
	}
	NODE_DISPLAY_NAME_MAPPINGS = {
		"ColorModPivot": ColorModPivot.TITLE,
		"ColorModEdges": ColorModEdges.TITLE,
	}
	try:
		import png
	except ImportError:
		print("Can't find pypng! Please install to enable 16bit image support.")
		pass
	else:
		from .highprec import SaveImageHighPrec, PreviewImageHighPrec, LoadImageHighPrec
		NODE_CLASS_MAPPINGS.update({
			"SaveImageHighPrec": SaveImageHighPrec,
			"PreviewImageHighPrec": PreviewImageHighPrec,
			"LoadImageHighPrec": LoadImageHighPrec,
		})
		
		NODE_DISPLAY_NAME_MAPPINGS.update({
			"SaveImageHighPrec": SaveImageHighPrec.TITLE,
			"PreviewImageHighPrec": PreviewImageHighPrec.TITLE,
			"LoadImageHighPrec": LoadImageHighPrec.TITLE,
		})
