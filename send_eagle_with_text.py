import os
import numpy as np
import logging

from PIL import Image
from datetime import datetime

import folder_paths

from .util import util
from .eagle_api import EagleAPI

FORCE_WRITE_PROMPT = False

# logging.basicConfig(level=logging.DEBUG)


class SendEagleWithText:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
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
        compression=80,
        lossless_webp=False,
        prompt_text=None,
        negative_text=None,
        memo_text=None,
        prompt=None,
        extra_pnginfo=None,
    ):
        # Force write prompt and extra_pnginfo to log (for debug)
        if FORCE_WRITE_PROMPT:
            util.write_prompt(prompt, extra_pnginfo)

        subfolder_name = datetime.now().strftime("%Y-%m-%d")

        full_output_folder = os.path.join(self.output_dir, subfolder_name)
        if not os.path.exists(full_output_folder):
            os.makedirs(full_output_folder)

        results = list()
        eagle_api = EagleAPI()

        for image in images:
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # get the (empty) Exif data of the generated Picture
            emptyExifData = img.getexif()
            imgexif = util.get_exif_from_prompt(emptyExifData, prompt, extra_pnginfo)

            width, height = img.size
            filename = f"{util.get_datetime_str_msec()}-{width}-{height}.webp"
            filefullpath = os.path.join(full_output_folder, filename)
            img.save(
                filefullpath, quality=compression, exif=imgexif, lossless=lossless_webp
            )

            item = {"path": filefullpath, "name": filename}

            item["annotation"] = util.make_annotation_text(
                prompt_text, negative_text, memo_text
            )
            item["tags"] = util.get_prompt_tags(prompt_text)

            _ret = eagle_api.add_item_from_path(data=item)
            logging.debug(_ret)

            results.append(
                {"filename": filename, "subfolder": subfolder_name, "type": self.type}
            )

        return {"ui": {"images": results}}
