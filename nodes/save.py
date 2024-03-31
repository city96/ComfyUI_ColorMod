import os
import png
import json
import torch
import random
import numpy as np
from io import BytesIO
from PIL import Image
from PIL.PngImagePlugin import PngInfo

import folder_paths
from comfy.cli_args import args
from nodes import SaveImage, PreviewImage, LoadImage

def get_PIL_tEXt(image, prompt, extra_pnginfo):
	"""This is extremely stupid"""
	# prepare PIL image as normal
	print(image.dtype)
	i = image.cpu().numpy()
	img = np.clip(255.0*i, 0, 255).astype(np.uint8)
	img = Image.fromarray(img)

	metadata = None
	if not args.disable_metadata:
		metadata = PngInfo()
		if prompt is not None:
			metadata.add_text("prompt", json.dumps(prompt))
		if extra_pnginfo is not None:
			for x in extra_pnginfo:
				metadata.add_text(x, json.dumps(extra_pnginfo[x]))

	# write temp PIL image
	tmp = BytesIO()
	img.save(tmp, "png", pnginfo=metadata, compress_level=0)
	tmp.seek(0)

	# read it back and PNG and get the tEXt chunks
	img=png.Reader(tmp)
	metadata = [x for x in img.chunks() if x[0] == b"tEXt"]
	return metadata

def save_png(image, extra_chunks, path):
	i = image.cpu().numpy()
	img = np.clip(65535.0*i, 0, 65535).astype(np.uint16)

	writer = png.Writer(
		size = (img.shape[1],img.shape[0]),
		bitdepth    = 16,
		greyscale   = False,
		compression = 9,
	)
	data = img.reshape(-1, img.shape[1]*img.shape[2]).tolist()
	# default writer without metadata
	if not extra_chunks:
		with open(path, "wb") as f:
			writer.write(f, data)
		return
	# jank in the tEXt chunks as well
	tmp = BytesIO()
	writer.write(tmp, data)
	tmp.seek(0)
	chunks = list(png.Reader(tmp).chunks())
	for k in extra_chunks:
		chunks.insert(1, k)
	with open(path, "wb") as f:
		png.write_chunks(f, chunks)

class SaveImageHighPrec(SaveImage):
	TITLE = "Save Image (16 bit)"
	def save_images(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
		filename_prefix += self.prefix_append
		full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
		results = list()
		for image in images:
			metadata = get_PIL_tEXt(image, prompt, extra_pnginfo)

			file = f"{filename}_{counter:05}_.png"
			path = os.path.join(full_output_folder, file)
			save_png(image, metadata, path)

			results.append({
				"filename": file,
				"subfolder": subfolder,
				"type": self.type
			})
			counter += 1

		return { "ui": { "images": results } }

# Directly copied from nodes.py
class PreviewImageHighPrec(SaveImageHighPrec):
	TITLE = "Preview Image (16 bit)"
	def __init__(self):
		self.output_dir = folder_paths.get_temp_directory()
		self.type = "temp"
		self.prefix_append = "_temp_" + ''.join(
			random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5)
		)

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"images": ("IMAGE",)
			},
			"hidden": {
				"prompt": "PROMPT",
				"extra_pnginfo": "EXTRA_PNGINFO"
			}
		}

class LoadImageHighPrec(LoadImage):
	TITLE = "Load Image (16 bit)"
	FUNCTION = "load_image_high_precision"

	def load_image_high_precision(self, image):
		if not image.endswith(".png"):
			print("ColorMod: Only PNG files can be loaded in 16 bit color.")
			return (self.load_image(image))

		image_path = folder_paths.get_annotated_filepath(image)
		reader = png.Reader(image_path)

		raw = reader.read()
		image = np.vstack(list(map(np.uint16, raw[2])))

		dim_rgb = image.shape[1] // raw[0]
		div_max = 1.0 if np.max(image) <= 255 else 256.0

		image = np.reshape(image,(raw[1], raw[0], dim_rgb))
		image = np.array(image).astype(np.float32) / (255.0 * div_max )
		image = torch.from_numpy(np.clip(image, 0.0, 1.0))[None,]

		if image.shape[3] == 4:
			mask = 1.0 - image[:,:,:,3]
			image = torch.stack([image[:,:,:,x] for x in range(3)], dim = 3)
		else:
			mask = torch.zeros((64,64), dtype=torch.float32, device="cpu").unsqueeze(0)
		return (image, mask)

NODE_CLASS_MAPPINGS = {
	"SaveImageHighPrec": SaveImageHighPrec,
	"PreviewImageHighPrec": PreviewImageHighPrec,
	"LoadImageHighPrec": LoadImageHighPrec,
}
