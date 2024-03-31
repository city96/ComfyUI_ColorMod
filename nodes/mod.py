import torch

class ColorModCompress:
	def __init__(self):
		pass

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "mod_compress"
	CATEGORY = "image/postprocessing"
	TITLE = "ColorMod (compress to [0;1])"

	def check_range(self, image):
		image_min = torch.min(image)
		image_max = torch.max(image)
		if image_min < 0.0:
			print("low trs hit")
			image = image + image_min

		if image_max > 1.0:
			print("high trs hit")
			image = image * (1 / image_max)

		new_max = torch.max(image)
		if new_max > 1.0:
			print("high due to low trs hit")
			image = image * (1 / new_max)

		print("MCX",image_min,image_max,new_max)

	def mod_compress(self, image):
		ll = torch.minimum(image, torch.zeros(image.shape))
		ll = torch.clip(torch.abs(ll) * 8, 0.0, 1.0)
		hh = torch.maximum(image, torch.ones(image.shape))
		hh = torch.clip((torch.abs(hh)-1.0) * 8, 0.0, 1.0)
		image = ll + hh

		# self.check_range(image) # debug
		out = torch.clip(image, 0.0, 1.0) # sanity
		return (out,)

class ColorModPivot:
	def __init__(self):
		pass

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
				"pivot": ("FLOAT", {"default": 0.5, "min":  0.001, "max": 0.999, "step": 0.01}),
				"move":  ("FLOAT", {"default": 0.0, "min": -2.000, "max": 2.000, "step": 0.01}),
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "mod_pivot"
	CATEGORY = "image/postprocessing"
	TITLE = "ColorMod (move pivot)"

	def mod_pivot(self, image, pivot, move):
		pivot_map = torch.ones(image.shape) * pivot
		image_high = torch.maximum(image, pivot_map) - pivot
		image_low = torch.minimum(image, pivot_map)

		image_high = image_high * (1/(1-pivot)) * (1-(pivot + move))
		image_low  = image_low * (1/pivot) * (pivot + move)
		out = torch.clip((image_high + image_low), 0.0, 1.0)
		return (out,)

class ColorModEdges:
	def __init__(self):
		pass

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
				"low":   ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}),
				"high":  ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}),
				"pivot": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "mod_edges"
	CATEGORY = "image/postprocessing"
	TITLE = "ColorMod (edges)"

	def mod_edges(self, image, low, pivot, high):
		pivot_map = torch.ones(image.shape) * pivot
		image_high = torch.maximum(image, pivot_map) - pivot
		image_low = torch.minimum(image, pivot_map)

		image_low = image_low * low + pivot * (1-low)
		image_high = image_high * high
		out = torch.clip((image_high + image_low), 0.0, 1.0)
		return (out,)

NODE_CLASS_MAPPINGS = {
	"ColorModCompress": ColorModCompress,
	"ColorModPivot": ColorModPivot,
	"ColorModEdges": ColorModEdges,
}
