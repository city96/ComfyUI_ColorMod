import cv2
import torch
import numpy as np

class HDRExposureFusion:
	def __init__(self):
		pass

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image_a": ("IMAGE",),
			},
			"optional": {
				"image_b": ("IMAGE",),
				"image_c": ("IMAGE",),
				"image_d": ("IMAGE",),
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "create_hdr"
	CATEGORY = "ColorMod/hdr"
	TITLE = "Exposure Fusion"

	def create_hdr(self, image_a, image_b=None, image_c=None, image_d=None):
		def img_to_cv2(img):
			img = img.cpu().numpy()
			img = img[:, :, ::-1] # PIL RGB to OpenCV BGR
			img = (img * 255.0).astype(np.uint8)
			return img

		images = [x.clone() for x in [image_a, image_b, image_c, image_d] if x is not None]
		assert all([x.shape[0] == images[0].shape[0] for x in images[1:]]), "Batch size mismatch!"
		images = torch.stack(images, dim=1)

		out = []
		for batch in images:
			batch = [img_to_cv2(x) for x in batch]
			hdr = cv2.createMergeMertens().process(batch)
			out.append(
				torch.from_numpy(hdr[:, :, ::-1].copy())
			)
		out = torch.stack(out, dim=0)
		return (out,)

class HDRCreate:
	def __init__(self):
		pass

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image_a": ("IMAGE",),
				"image_b": ("IMAGE",),
				"image_c": ("IMAGE",),
				"exposure_a": ("FLOAT", {"default": 1.0, "min":  0.001, "max": 1024.0, "step": 0.1}),
				"exposure_b": ("FLOAT", {"default": 2.5, "min":  0.001, "max": 1024.0, "step": 0.1}),
				"exposure_c": ("FLOAT", {"default": 8.0, "min":  0.001, "max": 1024.0, "step": 0.1}),
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "create_hdr"
	CATEGORY = "ColorMod/hdr"
	TITLE = "Create HDR image"

	def create_hdr(self, image_a, image_b, image_c, exposure_a, exposure_b, exposure_c):
		def img_to_cv2(img):
			img = img.cpu().numpy()
			img = img[:, :, ::-1] # PIL RGB to OpenCV BGR
			img = (img * 255.0).astype(np.uint8)
			return img

		images = [x.clone() for x in [image_a, image_b, image_c]]
		assert all([x.shape[0] == images[0].shape[0] for x in images[1:]]), "Batch size mismatch!"
		images = torch.stack(images, dim=1)
		times = [exposure_a, exposure_b, exposure_c]
		times = np.array(times, dtype=np.float32)
		
		out = []
		for batch in images:
			batch = [img_to_cv2(x) for x in batch]
			cal = cv2.createCalibrateDebevec().process(batch, times)
			hdr = cv2.createMergeDebevec().process(batch, times, cal)
			out.append(
				torch.from_numpy(hdr[:, :, ::-1].copy())
			)
		out = torch.stack(out, dim=0)
		return (out,)

NODE_CLASS_MAPPINGS = {
	"HDRExposureFusion": HDRExposureFusion,
	"HDRCreate": HDRCreate,
}
