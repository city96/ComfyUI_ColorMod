import cv2
import torch
import numpy as np

class CV2Tonemap:
	def __init__(self):
		pass

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
				"gamma": ("FLOAT", {"default": 1.0, "min":  0.00, "max": 8.0, "step": 0.01}),
				"mult":  ("FLOAT", {"default": 1.0, "min":  0.00, "max": 8.0, "step": 0.01}),
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "apply_tonemap"
	CATEGORY = "ColorMod/tonemap"
	TITLE = "Tonemap (simple)"
	tonemap_op = getattr(cv2, "createTonemap", None)

	def tonemap(self, raw, mult, **kwargs):
		img = self.tonemap_op(**kwargs).process(raw)
		return np.clip(img * mult, 0.0, 1.0)

	def apply_tonemap(self, image, **kwargs):
		out = []
		for raw in image:
			raw = raw.cpu().numpy()[:, :, ::-1]
			img = self.tonemap(raw, **kwargs)
			out.append(
				torch.from_numpy(img[:, :, ::-1].copy())
			)
		out = torch.stack(out, dim=0)
		return (out,)

class CV2TonemapDrago(CV2Tonemap):
	def __init__(self):
		super().__init__()

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
				"gamma":      ("FLOAT", {"default": 1.0, "min": 0.0, "max": 8.0, "step": 0.01}),
				"saturation": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 8.0, "step": 0.01}),
				"bias":       ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
				"mult":       ("FLOAT", {"default": 1.0, "min": 0.0, "max": 8.0, "step": 0.01}),
			}
		}
	TITLE = "Tonemap (Drago)"
	tonemap_op = getattr(cv2, "createTonemapDrago", None)

class CV2TonemapDurand(CV2Tonemap):
	def __init__(self):
		super().__init__()

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
				"gamma":       ("FLOAT", {"default": 1.0, "min":  0.0, "max": 8.0, "step": 0.01}),
				"contrast":    ("FLOAT", {"default": 1.0, "min":  0.0, "max": 8.0, "step": 0.01}),
				"saturation":  ("FLOAT", {"default": 1.0, "min":  0.0, "max": 8.0, "step": 0.01}),
				"sigma_space": ("FLOAT", {"default": 1.0, "min":  0.0, "max": 8.0, "step": 0.01}),
				"sigma_color": ("FLOAT", {"default": 1.0, "min":  0.0, "max": 8.0, "step": 0.01}),
				"mult":        ("FLOAT", {"default": 1.0, "min":  0.0, "max": 8.0, "step": 0.01}),
			}
		}

	TITLE = "Tonemap (Durand)"
	tonemap_op = getattr(cv2, "createTonemapDurand", None)

class CV2TonemapMantiuk(CV2Tonemap):
	def __init__(self):
		super().__init__()

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
				"gamma":       ("FLOAT", {"default": 1.0, "min": 0.0, "max": 8.0, "step": 0.01}),
				"scale":       ("FLOAT", {"default": 1.0, "min": 0.0, "max": 8.0, "step": 0.01}),
				"saturation":  ("FLOAT", {"default": 1.0, "min": 0.0, "max": 8.0, "step": 0.01}),
				"mult":        ("FLOAT", {"default": 1.0, "min": 0.0, "max": 8.0, "step": 0.01}),
			}
		}

	TITLE = "Tonemap (Mantiuk)"
	tonemap_op = getattr(cv2, "createTonemapMantiuk", None)

class CV2TonemapReinhard(CV2Tonemap):
	def __init__(self):
		super().__init__()

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
				"gamma":       ("FLOAT", {"default": 1.0, "min": 0.0, "max": 8.0, "step": 0.01}),
				"intensity":   ("FLOAT", {"default": 0.0, "min":-8.0, "max": 8.0, "step": 0.01}),
				"light_adapt": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.6, "step": 0.01}),
				"color_adapt": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.6, "step": 0.01}),
				"mult":        ("FLOAT", {"default": 1.0, "min": 0.0, "max": 8.0, "step": 0.01}),
			}
		}

	TITLE = "Tonemap (Reinhard)"
	tonemap_op = getattr(cv2, "createTonemapReinhard", None)

NODE_CLASS_MAPPINGS = {
	"CV2Tonemap": CV2Tonemap,
	"CV2TonemapDrago": CV2TonemapDrago,
	"CV2TonemapDurand": CV2TonemapDurand,
	"CV2TonemapMantiuk": CV2TonemapMantiuk,
	"CV2TonemapReinhard": CV2TonemapReinhard,
}

# not all cv2 versions support all tonemap nodes (e.g Durand require nonfree)
for name in list(NODE_CLASS_MAPPINGS.keys()):
	if NODE_CLASS_MAPPINGS[name].tonemap_op is None:
		print(f"Ignoring node '{name}' due to cv2 edition/version")
		del NODE_CLASS_MAPPINGS[name]
