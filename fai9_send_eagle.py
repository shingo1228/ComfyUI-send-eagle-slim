import os
import json
import numpy as np
import logging

from PIL import Image
from datetime import datetime

import folder_paths

from .util import util
from .prompt_info_extractor import PromptInfoExtractor
from .eagle_api import EagleAPI

FORCE_WRITE_PROMPT = False

# logging.basicConfig(level=logging.DEBUG)


class Fai9SendEagle:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "lossless_webp": (["lossy", "lossless"],),
                "compression": (
                    "INT",
                    {"default": 80, "min": 1, "max": 100, "step": 1},
                ),
                "send_prompt": (
                    "BOOLEAN",
                    {"default": False, "label_on": "enabled", "label_off": "disabled"},
                ),
            },
            "optional": {
                "positive": ("*", ),
                "negative": ("*", ),
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
        lossless_webp="lossy",
        send_prompt=False,
        positive=None,
        negative=None,
        prompt=None,
        extra_pnginfo=None,
    ):
        # Force write prompt and extra_pnginfo to log (for debug)
        if FORCE_WRITE_PROMPT:
            util.write_prompt(prompt, extra_pnginfo)

        if send_prompt:
            try:
                gen_data = PromptInfoExtractor(
                    prompt,
                    str(positive) if positive is not None else None,
                    str(negative) if negative is not None else None
                )

                Eagle_annotation_txt = gen_data.formatted_annotation()
                Eagle_tags = gen_data.get_prompt_tags()

                fn_modelname, _ = os.path.splitext(gen_data.info["model_name"])
                fn_num_of_smp = gen_data.info["steps"]
                fn_seed = gen_data.info["seed"]

            except (json.JSONDecodeError, KeyError, TypeError, Exception) as e:
                if isinstance(e, json.JSONDecodeError):
                    print(f"Json decode error occurred. detail:{e}")
                elif isinstance(e, KeyError):
                    print(f"Key error occurred. detail:{e}")
                elif isinstance(e, TypeError):
                    print(f"Type error occurred. detail:{e}")
                else:
                    print(f"Process error occurred. detail:{e}")
                (
                    Eagle_annotation_txt,
                    Eagle_tags,
                    fn_modelname,
                    fn_num_of_smp,
                    fn_seed,
                ) = util.initialize_defaults(prompt, extra_pnginfo)

        subfolder_name = datetime.now().strftime("%Y-%m-%d")

        full_output_folder = os.path.join(self.output_dir, subfolder_name)
        if not os.path.exists(full_output_folder):
            os.makedirs(full_output_folder)

        lossless = lossless_webp == "lossless"

        results = list()
        eagle_api = EagleAPI()
        for image in images:
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # get the (empty) Exif data of the generated Picture
            emptyExifData = img.getexif()
            imgexif = util.get_exif_from_prompt(emptyExifData, prompt, extra_pnginfo)

            width, height = img.size
            if send_prompt:
                filename = f"{util.get_datetime_str_msec()}-{fn_modelname}-Smp-{fn_num_of_smp}-{fn_seed}-{width}-{height}.webp"
            else:
                filename = f"{util.get_datetime_str_msec()}-{width}-{height}.webp"

            filefullpath = os.path.join(full_output_folder, filename)
            img.save(filefullpath, quality=compression, exif=imgexif, lossless=lossless)

            item = {"path": filefullpath, "name": filename}

            if send_prompt:
                item["annotation"] = Eagle_annotation_txt
                item["tags"] = Eagle_tags

            _ret = eagle_api.add_item_from_path(data=item)
            logging.debug(_ret)

            results.append(
                {"filename": filename, "subfolder": subfolder_name, "type": self.type}
            )

        return {"ui": {"images": results}}
