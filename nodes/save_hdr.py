import os
import cv2
import torch
import hashlib
import numpy as np

import folder_paths

class SaveImageHDR:
	def __init__(self):
		self.output_dir = folder_paths.get_output_directory()

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"images": ("IMAGE", ),
				"filename_prefix": ("STRING", {"default": "HDR/ComfyUI"})
			}
		}

	OUTPUT_NODE = True
	RETURN_TYPES = ()
	FUNCTION = "save_image"
	CATEGORY = "ColorMod/hdr"
	TITLE = "Save Image (HDR)"

	def save_image(self, images, filename_prefix):
		full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
			filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0]
		)
		for image in images:
			file = f"{filename}_{counter:05}_.hdr"
			path = os.path.join(full_output_folder, file)
			image = image.cpu().numpy()
			image = image[:, :, ::-1]
			cv2.imwrite(path, image)
		return ()

class LoadImageHDR:
	def __init__(self):
		pass

	@classmethod
	def INPUT_TYPES(s):
		exts = [".hdr"]
		input_dir = folder_paths.get_input_directory()
		files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
		files = [f for f in files if any([f.endswith(x) for x in exts])]
		return {
			"required" : {
				"image": (sorted(files),)
			}
		}

	RETURN_TYPES = ("IMAGE",)
	FUNCTION = "load_image"
	CATEGORY = "ColorMod/hdr"
	TITLE = "Load Image (HDR)"

	def load_image(self, image):
		path = folder_paths.get_annotated_filepath(image)
		img = cv2.imread(path, -1)
		assert img is not None, "Failed to read image!"
		out = torch.from_numpy(img[:, :, ::-1].copy()).unsqueeze(0)
		print(f"Loaded HDR image [{torch.min(out)},{torch.max(out)}]")
		return (out,)

	@classmethod
	def IS_CHANGED(s, image):
		image_path = folder_paths.get_annotated_filepath(image)
		m = hashlib.sha256()
		with open(image_path, 'rb') as f:
			m.update(f.read())
		return m.digest().hex()

	@classmethod
	def VALIDATE_INPUTS(s, image):
		if not folder_paths.exists_annotated_filepath(image):
			return "Invalid image file: {}".format(image)
		return True

NODE_CLASS_MAPPINGS = {
	"SaveImageHDR": SaveImageHDR,
	"LoadImageHDR": LoadImageHDR,
}
