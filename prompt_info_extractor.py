import json
import re

DEBUG = False


def dprint(str):
    if DEBUG:
        print(f"debug:{str}")


class PromptInfoExtractor:
    def __init__(self, prompt, config_filepath=None):
        """constructor

        Args:
            prompt (_type_): ComfyUI hidden object "prompt".
            config_filepath (_type_, optional): Configration file path. Defaults to None.
        """
        #        self.load_data(prompt)
        self._prompt = prompt

        if DEBUG:
            self._show_data()

        if config_filepath:
            self.load_config(config_filepath)
        else:
            self.config = {
                "search_class_types": ["KSampler", "KSamplerAdvanced"],
                "output_format": "Steps: {steps}, Sampler: {sampler_name} {scheduler}, CFG scale: {cfg}, Seed: {seed}, Size: {width}x{height}, Model: {model_name}",
            }
        self.info = self.gather_info()

    def load_data(self, json_filepath):
        """Load JSON data from the provided filepath."""
        with open(json_filepath, "r") as file:
            self._prompt = json.load(file)

    def load_config(self, config_filepath):
        """Load configuration from the provided filepath."""
        with open(config_filepath, "r") as config_file:
            self.config = json.load(config_file)

    def _show_data(self):
        """For debug. show information of ComfyUI hidden object "prompt" and "extra_onginfo"."""
        dprint(f"type of prompt:{type(self._prompt)}")
        dprint(f"Prompt:{self._prompt}")

    def gather_info(self):
        ksampler_items = self.get_ksampler_items()

        if not ksampler_items:
            return None

        key, ksampler_item = ksampler_items[0]

        model_name = self.extract_model_name(ksampler_item)
        latent_image_info = self.extract_latent_image_info(ksampler_item)
        prompt_text = self.extract_prompt_info()

        info_dict = {
            "steps": ksampler_item["inputs"]["steps"],
            "sampler_name": ksampler_item["inputs"]["sampler_name"],
            "scheduler": ksampler_item["inputs"]["scheduler"],
            "cfg": ksampler_item["inputs"]["cfg"],
            "seed": ksampler_item["inputs"].get(
                "seed", ksampler_item["inputs"].get("noise_seed", None)
            ),
            "model_name": model_name,
            "width": latent_image_info["inputs"]["width"],
            "height": latent_image_info["inputs"]["height"],
            "prompt": prompt_text["prompt"],
            "negative": prompt_text["negative"],
        }

        return info_dict

    def get_ksampler_items(self):
        ksampler_items = [
            (k, v)
            for k, v in self._prompt.items()
            if v["class_type"] in self.config["search_class_types"]
        ]
        return sorted(ksampler_items, key=lambda x: int(x[0]))

    def extract_model_name(self, item):
        return (
            self.get_ckpt_name(item["inputs"]["model"][0])
            .replace("/", "_")
            .replace("\\", "_")
        )

    def get_ckpt_name(self, node_number):
        """Recursively search for the 'ckpt_name' key starting from the specified node."""
        node = self._prompt[node_number]
        if "ckpt_name" in node["inputs"]:
            return node["inputs"]["ckpt_name"]
        if "model" in node["inputs"]:
            return self.get_ckpt_name(node["inputs"]["model"][0])
        return None

    def extract_latent_image_info(self, item):
        latent_image_node_number = item["inputs"]["latent_image"][0]
        target_item = self._prompt[latent_image_node_number]

        if target_item["class_type"] == "EmptyLatentImage":
            return target_item

        elif target_item["class_type"] == "SDXL Empty Latent Image":
            resolusion_str = target_item["inputs"]["resolution"]
            pattern = r"(\d+) x (\d+)"
            match = re.search(pattern, resolusion_str)

            latent_image_info = {
                "inputs": {"width": int(match.group(1)), "height": int(match.group(2))}
            }
            return latent_image_info

        else:
            latent_image_info = {"inputs": {"width": 0, "height": 0}}
            return latent_image_info

    def extract_prompt_info(self):
        positive_text = self.extract_text_by_key("positive")
        negative_text = self.extract_text_by_key("negative")

        info_dict = {}
        if positive_text:
            info_dict["prompt"] = positive_text
        if negative_text:
            info_dict["negative"] = negative_text

        return info_dict

    def extract_text_by_key(self, key):
        """Extract text by the given key, either 'positive' or 'negative'."""
        ksampler_items = self.get_ksampler_items()

        if not ksampler_items:
            return None

        ksampler_item = ksampler_items[0][1]

        if key not in ksampler_item["inputs"]:
            return None

        target_node_number = ksampler_item["inputs"][key][0]
        target_node = self._prompt.get(str(target_node_number), {})
        extracted_text = self.extract_text_from_node_v2(target_node)

        return extracted_text

    def extract_text_from_node_v2(self, node):
        # Extract direct text if available
        direct_text = node.get("inputs", {}).get("text")

        # Extract text_g and text_l and check if they are same or different
        text_g = node.get("inputs", {}).get("text_g")
        text_l = node.get("inputs", {}).get("text_l")

        if direct_text:
            return direct_text
        elif text_g and text_l:
            if text_g == text_l:
                return text_g
            else:
                return f"text_g:{text_g} text_l:{text_l}"
        elif text_g:
            return text_g
        elif text_l:
            return text_l

        return None

    def format_info(self, info_dict):
        """Format the gathered information based on the configuration."""
        formatted_str = self.config["output_format"].format(**info_dict)
        return formatted_str

    def extract_and_format(self):
        """Extract and format the required information from the loaded JSON data."""
        info = self.gather_info()
        if not info:
            return "No suitable data found."
        return self.format_info(info)

    def formatted_annotation(self):
        annotation = ""
        if len(self.info["prompt"]) > 0:
            annotation += self.info["prompt"]

        if len(self.info["negative"]) > 0:
            if len(annotation) > 0:
                annotation += "\n"
            annotation += "Negative prompt: "
            annotation += self.info["negative"]

        if len(annotation) > 0:
            annotation += "\n"
        annotation += self.extract_and_format()

        return annotation

    def get_prompt_tags(self):
        cleaned_string = re.sub(r":\d+\.\d+", "", self.info["prompt"])
        items = cleaned_string.split(",")

        return [
            re.sub(r"[\(\)]", "", item).strip()
            for item in items
            if re.sub(r"[\(\)]", "", item).strip()
        ]
