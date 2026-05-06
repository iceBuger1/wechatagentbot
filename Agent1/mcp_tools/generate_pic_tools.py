from typing import Optional, List
import os
import random
import time
import requests

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel


mcp = FastMCP()


# =========================================================
# Config
# =========================================================

COMFYUI_ADDRESS = "http://127.0.0.1:8188"

PROMPT_API = f"{COMFYUI_ADDRESS}/prompt"


DEFAULT_NEGATIVE_PROMPT = """
modern, recent, old, oldest, cartoon, graphic, text, painting,
crayon, graphite, abstract, glitch, deformed, mutated, ugly,
disfigured, long body, lowres, bad hands, missing fingers,
extra digits, fewer digits, cropped, very displeasing,
(worst quality, bad quality:1.2), bad anatomy, sketch,
jpeg artifacts, signature, watermark, username,
simple background, conjoined, bad ai-generated,
dead eyes, cross-eyed, deformed pupils
"""


# =========================================================
# Response Model
# =========================================================

class ImageResponse(BaseModel):
    success: bool

    saved_files: Optional[List[str]] = None

    message: Optional[str] = None


# =========================================================
# Utils
# =========================================================

def download_image(
    image_url: str,
    save_path: str,
    filename: Optional[str] = None
):
    """
    Download image from ComfyUI output
    """

    response = requests.get(image_url)
    response.raise_for_status()

    os.makedirs(save_path, exist_ok=True)

    if filename is None:

        if "filename=" in image_url:
            filename = image_url.split("filename=")[-1].split("&")[0]

        else:
            filename = f"{int(time.time())}.png"

    full_path = os.path.join(save_path, filename)

    with open(full_path, "wb") as f:
        f.write(response.content)

    return full_path


# =========================================================
# Tool
# =========================================================

@mcp.tool(
    name="generate_anime_image",
    description="Generate anime illustration using ComfyUI"
)
def generate_anime_image(

    prompt: str,

    negative_prompt: Optional[str] = None,

    width: int = 1024,
    height: int = 1024,

    steps: int = 28,
    cfg: float = 4.5,

    seed: Optional[int] = None,

    sampler_name: str = "euler_ancestral",
    scheduler: str = "simple",

    denoise: float = 0.75,

    checkpoint: str = "novaAnimeXL_ilV180.safetensors",

    save_dir: str = r"C:\Users\19553\Desktop\code1\generated_images"
):

    try:

        final_negative = (
            negative_prompt
            if negative_prompt
            else DEFAULT_NEGATIVE_PROMPT
        )

        final_seed = (
            seed
            if seed is not None
            else random.randint(0, 2**63 - 1)
        )

        workflow = {

            "5": {
                "inputs": {
                    "text": prompt,
                    "clip": ["18", 0]
                },
                "class_type": "CLIPTextEncode"
            },

            "7": {
                "inputs": {
                    "text": final_negative,
                    "clip": ["20", 0]
                },
                "class_type": "CLIPTextEncode"
            },

            "8": {
                "inputs": {
                    "samples": ["21", 0],
                    "vae": ["12", 2]
                },
                "class_type": "VAEDecode"
            },

            "10": {
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            },

            "12": {
                "inputs": {
                    "ckpt_name": checkpoint
                },
                "class_type": "CheckpointLoaderSimple"
            },

            "18": {
                "inputs": {
                    "stop_at_clip_layer": -2,
                    "clip": ["12", 1]
                },
                "class_type": "CLIPSetLastLayer"
            },

            "20": {
                "inputs": {
                    "stop_at_clip_layer": -2,
                    "clip": ["12", 1]
                },
                "class_type": "CLIPSetLastLayer"
            },

            "21": {
                "inputs": {

                    "seed": final_seed,

                    "steps": steps,
                    "cfg": cfg,

                    "sampler_name": sampler_name,
                    "scheduler": scheduler,

                    "denoise": denoise,

                    "model": ["12", 0],

                    "positive": ["5", 0],

                    "negative": ["7", 0],

                    "latent_image": ["22", 0]
                },

                "class_type": "KSampler"
            },

            "22": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },

                "class_type": "EmptyLatentImage"
            }
        }

        # =================================================
        # Submit Prompt
        # =================================================

        response = requests.post(
            PROMPT_API,
            json={"prompt": workflow},
            headers={"Content-Type": "application/json"}
        )

        response.raise_for_status()

        result = response.json()

        prompt_id = result["prompt_id"]

        # =================================================
        # Wait for completion
        # =================================================

        history_api = f"{COMFYUI_ADDRESS}/history/{prompt_id}"

        while True:

            history_response = requests.get(history_api)

            history_data = history_response.json()

            if prompt_id in history_data:

                outputs = history_data[prompt_id]["outputs"]

                saved_files = []

                for _, output_data in outputs.items():

                    if "images" in output_data:

                        for img in output_data["images"]:

                            filename = img["filename"]

                            subfolder = img.get("subfolder", "")

                            img_type = img.get("type", "output")

                            image_url = (
                                f"{COMFYUI_ADDRESS}/view"
                                f"?filename={filename}"
                                f"&subfolder={subfolder}"
                                f"&type={img_type}"
                            )

                            local_path = download_image(
                                image_url=image_url,
                                save_path=save_dir,
                                filename=filename
                            )

                            saved_files.append(local_path)

                return ImageResponse(
                    success=True,
                    message=f"image generated successfully, saved in {saved_files}"
                )

            time.sleep(1)

    except Exception as e:

        return ImageResponse(
            success=False,
            message=str(e)
        )


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":

    mcp.run(transport="stdio")