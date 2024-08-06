import cv2
import torch
import numpy as np

# You can add any color spaces supported by cv2
# [x[6:] for x in dir(cv2) if x.startswith("COLOR_")]
common = [
	"RGB", "BGR", "HLS", "HSV", "YCrCb", "YUV"
]

class ColorspaceConvert:
	def __init__(self):
		pass

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
				"src": (common, {"default": "RGB"}),
				"dst": (common, {"default": "RGB"}),
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "convert"
	CATEGORY = "ColorMod"
	TITLE = "Convert color space"

	def convert(self, image, src, dst):
		if src == dst:
			return (image, )
		
		atr = getattr(cv2, f"COLOR_{src}2{dst}", None)
		assert atr, f"Color conversion failed! Missing cv2 op 'COLOR_{src}2{dst}'"
		
		out = []
		for batch in image:
			img = (batch.cpu().numpy() * 255.0).astype(np.uint8)
			mod = cv2.cvtColor(img, atr)
			out.append(torch.from_numpy(mod.copy()) / 255.0)
		out = torch.stack(out, dim=0)
		print(torch.min(out), torch.mean(out), torch.max(out))
		return (out,)

NODE_CLASS_MAPPINGS = {
	"ColorspaceConvert": ColorspaceConvert,
}
