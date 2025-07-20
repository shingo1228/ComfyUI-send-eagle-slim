import requests
from .api_client import EagleAPI

class EagleSender:
    def __init__(self, base_url="http://localhost:41595"):
        self.eagle_api = EagleAPI(base_url)

    def _get_or_create_folder_id(self, folder_path: str):
        current_folder_id = None
        path_parts = [part for part in folder_path.split('/') if part]

        for i, part in enumerate(path_parts):
            found_id = None
            try:
                folders = self.eagle_api.get_folder_list()
                for folder in folders.get("data", []):
                    if folder.get("name") == part and (folder.get("parentId") == current_folder_id or (folder.get("parentId") is None and current_folder_id is None)):
                        found_id = folder.get("id")
                        break
            except requests.exceptions.RequestException as e:
                print(f"[ComfyUI-send-eagle-slim] Error getting folder list from Eagle: {e}")
                return None # Error, cannot proceed

            if found_id:
                current_folder_id = found_id
            else:
                # Folder not found, create it
                try:
                    print(f"[ComfyUI-send-eagle-slim] Creating folder: {part} under parent ID: {current_folder_id}")
                    new_folder = self.eagle_api.create_folder(part, current_folder_id)
                    current_folder_id = new_folder.get("data").get("id")
                except requests.exceptions.RequestException as e:
                    print(f"[ComfyUI-send-eagle-slim] Error creating folder '{part}' in Eagle: {e}")
                    return None # Error, cannot proceed
        return current_folder_id

    def send_to_eagle(self, filefullpath, filename, annotation, tags, full_folder_path=None):
        folder_id = None
        if full_folder_path:
            folder_id = self._get_or_create_folder_id(full_folder_path)

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
