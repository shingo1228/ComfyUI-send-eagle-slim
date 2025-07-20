import requests
from .api_client import EagleAPI

class EagleSender:
    def __init__(self, base_url="http://localhost:41595"):
        self.eagle_api = EagleAPI(base_url)

    def send_to_eagle(self, filefullpath, filename, annotation, tags, folder_name=None):
        folder_id = None
        if folder_name:
            try:
                folders = self.eagle_api.get_folder_list()
                for folder in folders.get("data", []):
                    if folder.get("name") == folder_name:
                        folder_id = folder.get("id")
                        break
                if not folder_id:
                    print(f"[ComfyUI-send-eagle-slim] Folder '{folder_name}' not found in Eagle. Item will be added to root.")
            except requests.exceptions.RequestException as e:
                print(f"[ComfyUI-send-eagle-slim] Error getting folder list from Eagle: {e}")

        item = {"path": filefullpath, "name": filename}
        if annotation:
            item["annotation"] = annotation
        if tags:
            item["tags"] = tags
        try:
            return self.eagle_api.add_item_from_path(data=item, folder_id=folder_id)
        except requests.exceptions.RequestException as e:
            print(f"[ComfyUI-send-eagle-slim] Error sending to Eagle: {e}")
            return None
