import torch

class ColorModCompress:
	def __init__(self):
		pass

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
				"mode": (["clip", "normalize", "compress"],)
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "mod_compress"
	CATEGORY = "ColorMod"
	TITLE = "ColorMod (compress)"

	def mod_compress(self, image, mode):
		image = image.clone()
		if mode == "clip":
			out = torch.clip(image, 0.0, 1.0)
		elif mode == "normalize":
			out = []
			for img in image:
				img_min = torch.min(image)
				img_max = torch.max(image)
				print(f"Normalizing [{img_min:6.4f}:{img_max:6.4f}] => [0.0;1.0]")
				img = (img - img_min) / (img_max - img_min)
				out.append(img)
			out = torch.stack(out, dim=0)
		elif mode == "compress":
			out = []
			for img in image:
				ll = torch.minimum(image, torch.zeros(image.shape))
				ll = torch.clip(torch.abs(ll), 0.0, 1.0)
				hh = torch.maximum(image, torch.ones(image.shape))
				hh = torch.clip((torch.abs(hh)-1.0), 0.0, 1.0)
				out.append(ll + hh)
			out = torch.stack(out, dim=0)
		else:
			raise ValueError(f"Unknown mode '{mode}'")

		# self.check_range(image) # debug
		out = torch.clip(out, 0.0, 1.0) # sanity
		return (out,)

class ColorModMove:
	def __init__(self):
		pass

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
				"move":  ("FLOAT", {"default": 0.0, "min": -1.000, "max": 1.000, "step": 0.01}),
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "mod_move"
	CATEGORY = "ColorMod"
	TITLE = "ColorMod (move)"

	def mod_move(self, image, move):
		image = image.clone()

		move_map = torch.ones(image.shape) * move
		out = torch.clip((image + move_map), -4.0, 4.0)
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
	CATEGORY = "ColorMod"
	TITLE = "ColorMod (move pivot)"

	def mod_pivot(self, image, pivot, move):
		image = image.clone()

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
				"pivot": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
				"high":  ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}),
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "mod_edges"
	CATEGORY = "ColorMod"
	TITLE = "ColorMod (edges)"

	def mod_edges(self, image, low, pivot, high):
		image = image.clone()

		pivot_map = torch.ones(image.shape) * pivot
		image_high = torch.maximum(image, pivot_map) - pivot
		image_low = torch.minimum(image, pivot_map)

		image_low = image_low * low + pivot * (1-low)
		image_high = image_high * high
		out = torch.clip((image_high + image_low), 0.0, 1.0)
		return (out,)

NODE_CLASS_MAPPINGS = {
	"ColorModCompress": ColorModCompress,
	"ColorModMove" : ColorModMove,
	"ColorModPivot": ColorModPivot,
	"ColorModEdges": ColorModEdges,
}
