import os
import numpy as np
from PIL import Image
from datetime import datetime
import folder_paths
import requests # Added for error handling

# New imports based on the refactored structure
from ..eagle_client.sender import EagleSender
from ..eagle_client.data_formatter import DataFormatter
from ..utils.common_utils import CommonUtils # For general utilities like saving PNGs

class SendImageToEagleNode:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "format": (["webp", "png"],),
                "lossless_webp": ("BOOLEAN", {"default": False, "label_on": "lossless", "label_off": "lossy"}),
                "compression": ("INT", {"default": 80, "min": 1, "max": 100, "step": 1}),
                "folder_name": ("STRING", {"default": "", "multiline": False}),
                "create_date_folder": ("BOOLEAN", {"default": True, "label_on": "Enabled", "label_off": "Disabled"}),
                "prompt_text": ("STRING", {"multiline": True}),
                "negative_text": ("STRING", {"multiline": True}),
                "memo_text": ("STRING", {"multiline": True}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "add_item"
    OUTPUT_NODE = True
    CATEGORY = "EagleTools"

    def add_item(self, images, format="webp", lossless_webp=False, compression=80, prompt_text=None, negative_text=None, memo_text=None, folder_name="", create_date_folder=True, prompt=None, extra_pnginfo=None):
        return self.process_and_send(
            images,
            format=format,
            lossless_webp=lossless_webp,
            compression=compression,
            prompt_text=prompt_text,
            negative_text=negative_text,
            memo_text=memo_text,
            folder_name=folder_name,
            create_date_folder=create_date_folder,
            prompt=prompt,
            extra_pnginfo=extra_pnginfo
        )

    def save_image(self, image, filename, full_output_folder, compression, lossless, prompt, extra_pnginfo):
        i = 255.0 * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        filefullpath = os.path.join(full_output_folder, filename)

        if filename.endswith('.webp'):
            emptyExifData = img.getexif()
            imgexif = DataFormatter.get_exif_from_prompt(emptyExifData, prompt, extra_pnginfo)
            img.save(filefullpath, quality=compression, exif=imgexif, lossless=lossless)
        else:
            CommonUtils.save_png_image(img, filefullpath, prompt, extra_pnginfo)

        return filefullpath

    def send_to_eagle(self, filefullpath, filename, annotation, tags, folder_name):
        eagle_sender = EagleSender()
        return eagle_sender.send_to_eagle(filefullpath, filename, annotation, tags, folder_name)

    def get_full_output_folder(self):
        subfolder_name = datetime.now().strftime("%Y-%m-%d")
        full_output_folder = os.path.join(self.output_dir, subfolder_name)
        if not os.path.exists(full_output_folder):
            os.makedirs(full_output_folder)
        return full_output_folder

    def process_and_send(self, images, **kwargs):
        full_output_folder = self.get_full_output_folder()
        results = []

        base_folder_name = kwargs.get('folder_name', '')
        create_date_folder = kwargs.get('create_date_folder', True)

        target_folder_path = base_folder_name
        if create_date_folder:
            date_str = datetime.now().strftime("%Y%m%d")
            if target_folder_path:
                target_folder_path = os.path.join(target_folder_path, date_str)
            else:
                target_folder_path = date_str

        for image in images:
            filename, annotation, tags = self.prepare_image_data(image, **kwargs)

            filefullpath = self.save_image(
                image,
                filename,
                full_output_folder,
                kwargs.get('compression'),
                kwargs.get('lossless_webp'),
                kwargs.get('prompt'),
                kwargs.get('extra_pnginfo')
            )

            self.send_to_eagle(filefullpath, filename, annotation, tags, target_folder_path)

            results.append(
                {"filename": filename, "subfolder": full_output_folder, "type": self.type}
            )

        return {"ui": {"images": results}}

    def prepare_image_data(self, image, **kwargs):
        prompt_text = kwargs.get('prompt_text')
        negative_text = kwargs.get('negative_text')
        memo_text = kwargs.get('memo_text')
        format = kwargs.get('format')

        i = 255.0 * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        width, height = img.size

        filename = f"{DataFormatter.get_datetime_str_msec()}-{width}-{height}.{format}"
        annotation = DataFormatter.make_annotation_text(prompt_text, negative_text, memo_text)
        tags = DataFormatter.get_prompt_tags(prompt_text)

        return filename, annotation, tags
