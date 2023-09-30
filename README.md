# ComfyUI_ColorMod

![COLMOD](https://github.com/city96/ComfyUI_ColorMod/assets/125218114/7994d00b-69ad-4908-abcf-91adecba02e5)

This repo currently has two sets of nodes - one set for editing the contrast/color of images and another set for saving images as 16 bit PNG files.

I'd recommend using it with `--fp32-vae` to get the full precision output. BF16 definitely doesn't have enough precision, FP16 might work but will NaN randomly on some VAEs.

I'm not sure it makes sense to do it like this from an implementational standpoint, but (as far as I can tell) the IMAGE inputs/outputs in ComfyUI are `torch.float32`s between 0 and 1, meaning they have a lot of precision compared to 8bit images.

The idea was to make use of this so changing the brightness / contrast / etc would happen in this high-precision space, which would hopefully lessen banding and artifacts due to rounding errors/working with `UINT8`.

## Installation

Simply clone the whole repo to your custom node folder: `git clone https://github.com/city96/ComfyUI_ColorMod ComfyUI/custom_nodes/ComfyUI_ColorMod`

The 16 bit PNG output nodes rely on `pypng`, which can be installed with `pip install pypng`. This isn't a hard requirement, it disables those nodes if it can't find it.

For the standalone comfy install, you can install it with `python_embeded\python.exe -m pip install pypng`.

# Usage

The custom nodes are in images and images/postprocessing respectively. Below is a simple graph that explains what the values do, though I'd like to add a JS widget to show these changes live eventually.

![usage](https://github.com/city96/ComfyUI_ColorMod/assets/125218114/e8355d04-ba8a-4d6f-a7dd-c360c82fa05e)


## Precision

## VAE

After I added the node to load images in 16 bit precision, I could test how much gets lost when doing a single VAE encode -> VAE decode pass. The added noise makes it hard to see on a histogram, so I just ran a very agressive edge-detect to highlight any banding.

From top to bottom:
- `N16` = Native 16 bit gradient, 2048 wide, every column a different color. Not encoded.
- `FP32` = `N16` as the input image, `--fp32-vae` launch arg
- `FP16` = `N16` as the input image, `--fp16-vae` launch arg
- `BF16` = `N16` as the input image, `--bf16-vae` launch arg ([default on 20XX cards and up](https://github.com/comfyanonymous/ComfyUI/commit/b8c7c770d3259543af35acfc45608449b3bc6caa))
- `N8` = Native 8 bit gradient, 2048 wide with 256 different colors. Not encoded.

### ft-mse-840000.ckpt
I accidentally cropped the bottom edge off of `FP32`, hence the lack of noise there.

![vae840k](https://github.com/city96/ComfyUI_ColorMod/assets/125218114/f1a0a14b-eb49-4636-b176-a1613f3734ce)

### sdxl_v0.9.safetensors
Had to use the [FP16 VAE](https://huggingface.co/madebyollin/sdxl-vae-fp16-fix) for the FP16 test.

![vaeXL](https://github.com/city96/ComfyUI_ColorMod/assets/125218114/8ce9e157-681a-4054-ab4b-48468dfde984)

## UNET

(I need to re-test this part to rule out the VAE messing with the results - i.e. run fp32 VAE, pass a 16 bit image into the UNET to begin with, etc, etc.)

I ran a 8 bit gradient through the UNET at 99% denoise, then decoded it using `ft-mse-840000`. After this, I saved the output as a 16 bit PNG using the node in this pack.

The graph below shows the first two decimal digits after converting the image to [0-255]. There is no point in charting INT8 images, since they all end in zero. Here's what I think these results mean:

- The synthetic gradient was 2048 wide, with each column being `(column+1)/2048`% gray. The grouping mostly makes sense here.
- The FP32 VAE adds a bunch of noise, so the distribution ends up pretty even, though it does lean towards values ending in zero (probably due to being trained on 8bit images).
- The FP16 VAE seems to be similar to the synthetic one, maybe due to the lack of precision?
- The BF16 VAE apparently only has 7 bits of precision for the mantissa, so it's a pretty bad format to store the [0-1] VAE output in.

![graph_rem](https://github.com/city96/ComfyUI_ColorMod/assets/125218114/955fc9cc-943d-44a1-93a2-0c1c821f3d63)

*Or I might just be graphing weird float rounding errors. Who knows.*

