import os
import numpy as np
import json

from PIL import Image
from PIL.PngImagePlugin import PngInfo
from datetime import datetime

import folder_paths

from .util import util
from .eagle_api import EagleAPI

FORCE_WRITE_PROMPT = False


class SendEagleWithText:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "format": (["webp", "png"],),
                "lossless_webp": (
                    "BOOLEAN",
                    {"default": False, "label_on": "lossless", "label_off": "lossy"},
                ),
                "compression": (
                    "INT",
                    {"default": 80, "min": 1, "max": 100, "step": 1},
                ),
                "prompt_text": (
                    "STRING",
                    {"forceInput": True, "multiline": True},
                ),
                "negative_text": (
                    "STRING",
                    {"forceInput": True, "multiline": True},
                ),
                "memo_text": (
                    "STRING",
                    {"multiline": True},
                ),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "add_item"
    OUTPUT_NODE = True
    CATEGORY = "EagleTools"

    def add_item(
        self,
        images,
        format="webp",
        lossless_webp=False,
        compression=80,
        prompt_text=None,
        negative_text=None,
        memo_text=None,
        prompt=None,
        extra_pnginfo=None,
    ):
        subfolder_name = datetime.now().strftime("%Y-%m-%d")

        full_output_folder = os.path.join(self.output_dir, subfolder_name)
        if not os.path.exists(full_output_folder):
            os.makedirs(full_output_folder)

        results = list()
        eagle_api = EagleAPI()

        for image in images:
            # Make Image object
            normalized_pixels = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(normalized_pixels, 0, 255).astype(np.uint8))

            file_name = ""
            file_full_path = ""
            width, height = img.size

            if format == "webp":
                # Save webp image file
                file_name = f"{util.get_datetime_str_msec()}-{width}-{height}.webp"
                file_full_path = os.path.join(full_output_folder, file_name)

                exif_data = util.get_exif_from_prompt(
                    img.getexif(), prompt, extra_pnginfo
                )

                img.save(
                    file_full_path,
                    quality=compression,
                    exif=exif_data,
                    lossless=lossless_webp,
                )

            else:
                # Save png image file
                file_name = f"{util.get_datetime_str_msec()}-{width}-{height}.png"
                file_full_path = os.path.join(full_output_folder, file_name)
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

                img.save(file_full_path, pnginfo=metadata, compress_level=4)

                util.save_png_image(img, file_full_path, prompt, extra_pnginfo)

            # Send image to Eagle
            item = {"path": file_full_path, "name": file_name}
            item["annotation"] = util.make_annotation_text(
                prompt_text, negative_text, memo_text
            )
            item["tags"] = util.get_prompt_tags(prompt_text)

            _ret = eagle_api.add_item_from_path(data=item)

            results.append(
                {"filename": file_name, "subfolder": subfolder_name, "type": self.type}
            )

        return {"ui": {"images": results}}
