![ColorModExample](https://github.com/city96/ComfyUI_ColorMod/assets/125218114/3be66a59-46df-46a6-bbcf-ac05142442ec)

This repo contains nodes around image color manipulation, as well as HDR and tonemapping operations.

## Installation

As with most node packs, you can install it by git cloning it to your custom nodes folder or by installing it through the manager.
```
git clone https://github.com/city96/ComfyUI_ColorMod ./ComfyUI/custom_nodes/ComfyUI_ColorMod
```

> [!IMPORTANT]  
> Installing the requirements isn't strictly required, but most of the core nodes will be missing without them.

For regular installs, this can be done using the usual `pip install -r requirements.txt` in the node folder with the correct env/venv active.

For standalone ComfyUI installs on windows, open a command line in the same location your `run_nvidia_gpu.bat` file is located and run the following:
```
.\python_embeded\python.exe -s -m pip install -r .\ComfyUI\custom_nodes\ComfyUI_ExtraModels\requirements.txt
```

# Usage

The ColorMod nodes all change the image color values in some way. In the most recent version, they all come with a small visualization tool to show how the values will affect the image.

The graph, without any changes, is a straight line from the bottom left to the top right corner. The horizontal axis represents the input values while the vertical axist represents the remapped ones. As an example, moving the left side up will result in darker areas being brighter.

Clipping should be enabled (unless HDR images are being manipulated), as passing values outside the expected range to the VAE/UNET can cause some odd behavior. 


For the HDR workflow in the image above, you can use this [Sample workflow](https://github.com/city96/ComfyUI_ColorMod/files/14913017/ColorModNarrowWF.json).

Most of the HDR nodes require a bit of trial-and-error, especially the one for creating HDR images. Realistically, there is no "exposure" with generated images so these values will have to be guessed.

Another issue can be that different diffusion passes at different brightness levels can end up diverging, resulting in artifacts when recombining them. Controlnet and similar techniques to keep the inputs and outputs similar are recommended.

The tonemapping nodes also require some testing to get right, and **behave slightly differently for HDR/SDR** images. The "multiplier" value is largely non-standard, and is an idea adapted from [this great article](https://learnopencv.com/high-dynamic-range-hdr-imaging-using-opencv-cpp-python/) by Satya Mallick, which I referenced while figuring out the proper implementation. For HDR tonemapping, setting a multiplier of 2-3 might result in better image quality.

Using HDR images directly without tonemapping is probably useless, and has a chance to cause errors since the values are no longer in the expected `[0.0,1.0]` range.

## Precision

(needs retesting on newer versions)

<details>
<summary>Click to expand.</summary>

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

</details>
