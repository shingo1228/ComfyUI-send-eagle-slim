import os
import sys
import json
import numpy as np
import traceback
import requests

from PIL import Image
from datetime import datetime

import folder_paths

sys.path.append(os.path.dirname(__file__))
from prompt_info_extractor import PromptInfoExtractor

DEBUG = False


def dprint(str):
    if DEBUG:
        print(f"Debug:{str}")


class SendEagle:
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
        prompt=None,
        extra_pnginfo=None,
    ):
        def initialize_defaults(prompt, extra_pnginfo):
            log_file_name = os.path.join(
                os.path.dirname(__file__), "prompt_decode_err.log"
            )
            with open(log_file_name, "w", encoding="utf-8") as f:
                f.write('"prompt:"\n')
                json.dump(prompt, f, indent=4, ensure_ascii=False)
                if extra_pnginfo is not None:
                    f.write('\n\n"extra_pnginfo:"\n')
                    json.dump(extra_pnginfo, f, indent=4, ensure_ascii=False)

            print("check prompt_decode_err.log")
            traceback.print_exc()
            return "", [], "unknown", "00", "000000"

        try:
            gen_data = PromptInfoExtractor(prompt)

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
            ) = initialize_defaults(prompt, extra_pnginfo)

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
            imgexif = util.getExifFromPrompt(emptyExifData, prompt, extra_pnginfo)

            width, height = img.size
            fn_width = width
            fn_height = height

            filename = f"{util.get_datetime_str_msec()}-{fn_modelname}-Smp-{fn_num_of_smp}-{fn_seed}-{fn_width}-{fn_height}.webp"
            filefullpath = os.path.join(full_output_folder, filename)

            img.save(filefullpath, quality=compression, exif=imgexif, lossless=lossless)

            item = {
                "path": filefullpath,
                "name": filename,
                "annotation": Eagle_annotation_txt,
                "tags": Eagle_tags,
            }
            _ret = eagle_api.add_item_from_path(data=item)
            dprint(_ret)

            results.append(
                {"filename": filename, "subfolder": subfolder_name, "type": self.type}
            )

        return {"ui": {"images": results}}


class util:
    @staticmethod
    def get_datetime_str_msec():
        now = datetime.now()
        date_time_str = now.strftime("%Y%m%d_%H%M%S")
        return f"{date_time_str}_{now.microsecond:06}"

    @staticmethod
    def getExifFromPrompt(emptyExifData, prompt, extra_pnginfo):
        """Generate exif information for webp format from hidden items "prompt" and "extra_pnginfo"""
        workflowmetadata = str()
        promptstr = str()

        imgexif = emptyExifData
        if prompt is not None:
            promptstr = "".join(json.dumps(prompt))  # prepare prompt String
            imgexif[0x010F] = (
                "Prompt:" + promptstr
            )  # Add PromptString to EXIF position 0x010f (Exif.Image.Make)
        if extra_pnginfo is not None:
            for x in extra_pnginfo:
                workflowmetadata += "".join(json.dumps(extra_pnginfo[x]))
        imgexif[0x010E] = (
            "Workflow:" + workflowmetadata
        )  # Add Workflowstring to EXIF position 0x010e (Exif.Image.ImageDescription)
        return imgexif


class EagleAPI:
    def __init__(self, base_url="http://localhost:41595"):
        self.base_url = base_url

    def add_item_from_path(self, data, folder_id=None):
        if folder_id:
            data["folderId"] = folder_id
        return self._send_request("/api/item/addFromPath", method="POST", data=data)

    # Private method for sending requests
    def _send_request(self, endpoint, method="GET", data=None):
        url = self.base_url + endpoint
        headers = {"Content-Type": "application/json"}

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()


NODE_CLASS_MAPPINGS = {
    "Send Webp Image to Eagle": SendEagle,
}
