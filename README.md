# ComfyUI_ColorMod

![COLMOD](https://github.com/city96/ComfyUI_ColorMod/assets/125218114/7994d00b-69ad-4908-abcf-91adecba02e5)

This repo currently has two sets of nodes - one set for editing the contrast/color of images and another set for saving images as 16 bit PNG files.

I'd recommend using it with `--fp32-vae` to get the full precision output. BF16 definitely doesn't have enough precision, FP16 might work but will NaN randomly on some VAEs.

I'm not sure it makes sense to do it like this from an implementational standpoint, but (as far as I can tell) the IMAGE inputs/outputs in ComfyUI are `torch.float32`s between 0 and 1, meaning they have a lot of precision compared to 8bit images.

The idea was to make use of this so changing the brightness / contrast / etc would happen in this high-precision space, which would hopefully lessen banding and artifacts due to rounding errors/working with `UINT8`.

## Installation

Simply clone the whole repo to your custom node folder: `git clone https://github.com/city96/ComfyUI_ColorMod ComfyUI/custom_nodes/ComfyUI_ColorMod`

The 16 bit PNG output nodes rely on `pypng`, which can be installed with `pip install pypng`. This isn't a hard requirement, it disables those nodes if it can't find it.

## Precision

I ran a 8 bit gradient through the UNET at 99% denoise, then decoded it using `ft-mse-840000`. After this, I saved the output as a 16 bit PNG using the node in this pack.

The graph below shows the first two decimal digits after converting the image to [0-255]. There is no point in charting INT8 images, since they all end in zero. Here's what I think these results mean:

- The synthetic gradient was 2048 wide, with each column being `(column+1)/2048`% gray. The grouping mostly makes sense here.
- The FP32 VAE adds a bunch of noise, so the distribution ends up pretty even, though it does lean towards values ending in zero (probably due to being trained on 8bit images).
- The FP16 VAE seems to be similar to the synthetic one, maybe due to the lack of precision?
- The BF16 VAE apparently only has 7 bits of precision for the mantissa, so it's a pretty bad format to store the [0-1] VAE output in.

![graph_rem](https://github.com/city96/ComfyUI_ColorMod/assets/125218114/955fc9cc-943d-44a1-93a2-0c1c821f3d63)

*Or I might just be graphing weird float rounding errors. Who knows.*

