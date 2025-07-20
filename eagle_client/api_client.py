import requests


class EagleAPI:
    def __init__(self, base_url="http://localhost:41595"):
        self.base_url = base_url

    def add_item_from_path(self, data, folder_id=None):
        if folder_id:
            data["folderId"] = folder_id
        return self._send_request("/api/item/addFromPath", method="POST", data=data)

    def create_folder(self, name, parent_id=None):
        data = {"name": name}
        if parent_id:
            data["parent"] = parent_id
        return self._send_request("/api/folder/create", method="POST", data=data)

    def get_folder_list(self):
        return self._send_request("/api/folder/list", method="GET")

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
