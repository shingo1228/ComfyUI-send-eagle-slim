import os
import json
import numpy as np
import traceback
import requests

from PIL import Image
from datetime import datetime

import folder_paths

from .prompt_info_extractor import PromptInfoExtractor

DEBUG = False
FORCE_WRITE_PROMPT = False


def dprint(str):
    if DEBUG:
        print(f"Debug:{str}")


class SendEagleWithText:
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
                "prompt_text": (
                    "STRING",
                    {"multiline": True},
                ),
                "negative_text": (
                    "STRING",
                    {"multiline": True},
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
        lossless_webp="lossy",
        prompt_text=None,
        negative_text=None,
        memo_text=None,
        prompt=None,
        extra_pnginfo=None,
    ):
        if (
            FORCE_WRITE_PROMPT
        ):  # Force write prompt and extra_pnginfo to log (for debug)
            util.write_prompt(prompt, extra_pnginfo)

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

            filename = f"{util.get_datetime_str_msec()}-{width}-{height}.webp"

            filefullpath = os.path.join(full_output_folder, filename)
            img.save(filefullpath, quality=compression, exif=imgexif, lossless=lossless)

            item = {"path": filefullpath, "name": filename}

            item["annotation"] = util.make_annotation_text(
                prompt_text, negative_text, memo_text
            )

            _ret = eagle_api.add_item_from_path(data=item)
            dprint(_ret)

            results.append(
                {"filename": filename, "subfolder": subfolder_name, "type": self.type}
            )

        return {"ui": {"images": results}}


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
                "send_prompt": (
                    "BOOLEAN",
                    {"default": False, "label_on": "enabled", "label_off": "disabled"},
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
        send_prompt=False,
        prompt=None,
        extra_pnginfo=None,
    ):
        if (
            FORCE_WRITE_PROMPT
        ):  # Force write prompt and extra_pnginfo to log (for debug)
            util.write_prompt(prompt, extra_pnginfo)

        if send_prompt:
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
            imgexif = util.getExifFromPrompt(emptyExifData, prompt, extra_pnginfo)

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
            dprint(_ret)

            results.append(
                {"filename": filename, "subfolder": subfolder_name, "type": self.type}
            )

        return {"ui": {"images": results}}


class util:
    def initialize_defaults(prompt, extra_pnginfo):
        util.write_prompt(prompt, extra_pnginfo)
        print("check prompt_decode_err.log")
        traceback.print_exc()
        return "", [], "unknown", "00", "000000"

    @staticmethod
    def make_annotation_text(prompt_text, negative_text, memo_text):
        def is_valid_text(text):
            return isinstance(text, str) and text.strip() and text != "undefined"

        tmp_annotation = ""

        if is_valid_text(prompt_text):
            tmp_annotation += prompt_text

        if is_valid_text(negative_text):
            tmp_annotation += "\n" if tmp_annotation.strip() else ""
            tmp_annotation += "Negative prompt:" + negative_text

        if is_valid_text(memo_text):
            tmp_annotation += "\n" if tmp_annotation.strip() else ""
            tmp_annotation += "Memo:" + memo_text

        return tmp_annotation

    @staticmethod
    def write_prompt(prompt, extra_pnginfo):
        log_file_name = os.path.join(os.path.dirname(__file__), "prompt_decode_err.log")
        with open(log_file_name, "w", encoding="utf-8") as f:
            f.write('"prompt:"\n')
            json.dump(prompt, f, indent=4, ensure_ascii=False)
            if extra_pnginfo is not None:
                f.write('\n\n"extra_pnginfo:"\n')
                json.dump(extra_pnginfo, f, indent=4, ensure_ascii=False)

    @staticmethod
    def get_datetime_str_msec():
        now = datetime.now()
        date_time_str = now.strftime("%Y%m%d_%H%M%S")
        return f"{date_time_str}_{now.microsecond:06}"

    @staticmethod
    def getExifFromPrompt(
        emptyExifData: Image.Exif, prompt, extra_pnginfo
    ) -> Image.Exif:
        """Generate exif information for webp format from hidden items "prompt" and "extra_pnginfo"""
        imgexif = emptyExifData

        # Add PromptString to EXIF position 0x010f (Exif.Image.Make)
        if prompt is not None:
            promptstr = "".join(json.dumps(prompt))
            imgexif[0x010F] = "Prompt:" + promptstr

        # Add Workflowstring to EXIF position 0x010e (Exif.Image.ImageDescription)
        if extra_pnginfo is not None:
            workflowmetadata = str()
            for x in extra_pnginfo:
                workflowmetadata += "".join(json.dumps(extra_pnginfo[x]))

            imgexif[0x010E] = "Workflow:" + workflowmetadata

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
    "Send Eagle with text": SendEagleWithText,
}
