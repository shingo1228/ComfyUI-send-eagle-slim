import os
import json
import re
from PIL import Image
from datetime import datetime

class DataFormatter:
    @staticmethod
    def make_annotation_text(
        prompt_text: str, negative_text: str, memo_text: str
    ) -> str:
        """
        Generates annotation text.

        This method creates text for annotations by combining prompt text, negative text, and memo text.
        """

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
    def get_datetime_str_msec() -> str:
        """
        Gets the current datetime as a string with millisecond precision.

        This method generates and returns a string representing the current datetime with millisecond precision.
        """
        now = datetime.now()
        date_time_str = now.strftime("%Y%m%d_%H%M%S")
        return f"{date_time_str}_{now.microsecond:06}"

    @staticmethod
    def get_exif_from_prompt(
        emptyExifData: Image.Exif, prompt, extra_pnginfo
    ) -> Image.Exif:
        """
        Generate exif information for webp format from hidden items "prompt" and "extra_pnginfo
        """
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

    @staticmethod
    def get_prompt_tags(prompt_text: str) -> list:
        if (
            not isinstance(prompt_text, str)
            or not prompt_text.strip()
            or prompt_text == "undefined"
        ):
            return []

        cleaned_string = re.sub(r":\d+\.\d+", "", prompt_text)
        items = cleaned_string.split(",")
        return [
            re.sub(r"[\(\)]", "", item).strip()
            for item in items
            if re.sub(r"[\(\)]", "", item).strip()
        ]

