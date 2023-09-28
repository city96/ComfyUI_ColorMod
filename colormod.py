import os
import png
import json
import torch
import numpy as np


class ColorModPivot:
	def __init__(self):
		pass

	@classmethod
	def INPUT_TYPES(s):
		return {
			"required": {
				"image": ("IMAGE",),
				"pivot": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
				"move":  ("FLOAT", {"default": 0.0, "min": -2.0, "max": 2.0, "step": 0.01}),
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
				"low":	("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}),
				"pivot":  ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
				"high":   ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.01}),
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
