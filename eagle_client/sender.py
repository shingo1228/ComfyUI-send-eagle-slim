import requests
from .api_client import EagleAPI

class EagleSender:
    def __init__(self, base_url="http://localhost:41595"):
        self.eagle_api = EagleAPI(base_url)

    def send_to_eagle(self, filefullpath, filename, annotation, tags):
        item = {"path": filefullpath, "name": filename}
        if annotation:
            item["annotation"] = annotation
        if tags:
            item["tags"] = tags
        try:
            return self.eagle_api.add_item_from_path(data=item)
        except requests.exceptions.RequestException as e:
            print(f"[ComfyUI-send-eagle-slim] Error sending to Eagle: {e}")
            return None
