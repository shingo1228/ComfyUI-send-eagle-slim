import unittest
from unittest.mock import patch, MagicMock
import json
import requests

# テスト対象のモジュールをインポート
from eagle_client.api_client import EagleAPI
from eagle_client.sender import EagleSender

class TestEagleClient(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://localhost:41595"
        self.eagle_api = EagleAPI(self.base_url)
        self.eagle_sender = EagleSender(self.base_url)

    @patch('requests.get')
    def test_get_folder_list_success(self, mock_get):
        # モックのレスポンスを設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": [{"id": "folder1", "name": "TestFolder", "parentId": None}]}
        mock_get.return_value = mock_response

        # メソッドを呼び出し
        folders = self.eagle_api.get_folder_list()

        # アサーション
        mock_get.assert_called_once_with(f"{self.base_url}/api/folder/list", headers={"Content-Type": "application/json"})
        self.assertEqual(folders["data"][0]["name"], "TestFolder")

    @patch('requests.post')
    def test_add_item_from_path_success(self, mock_post):
        # モックのレスポンスを設定
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": {"id": "item1"}}
        mock_post.return_value = mock_response

        # メソッドを呼び出し
        data = {"path": "/path/to/image.png", "name": "image.png"}
        result = self.eagle_api.add_item_from_path(data, folder_id="folder1")

        # アサーション
        mock_post.assert_called_once_with(f"{self.base_url}/api/item/addFromPath", headers={"Content-Type": "application/json"}, json={"path": "/path/to/image.png", "name": "image.png", "folderId": "folder1"})
        self.assertEqual(result["data"]["id"], "item1")

    @patch('requests.post')
    @patch('requests.get')
    def test_get_or_create_folder_id_create_new_root_folder(self, mock_get, mock_post):
        # フォルダリストが空の場合
        mock_get.return_value.json.return_value = {"status": "success", "data": []}
        # 新しいフォルダ作成のモック
        mock_post.return_value.json.return_value = {"status": "success", "data": {"id": "new_root_folder_id", "name": "NewRootFolder"}}

        folder_id = self.eagle_sender._get_or_create_folder_id("NewRootFolder")

        mock_get.assert_called_once()
        mock_post.assert_called_once_with(f"{self.base_url}/api/folder/create", headers={"Content-Type": "application/json"}, json={"name": "NewRootFolder"})
        self.assertEqual(folder_id, "new_root_folder_id")

    @patch('requests.post')
    @patch('requests.get')
    def test_get_or_create_folder_id_create_nested_folder(self, mock_get, mock_post):
        # フォルダリストのモック
        mock_get.return_value.json.return_value = {"status": "success", "data": [
            {"id": "parent_folder_id", "name": "ParentFolder", "parentId": None}
        ]}
        # 新しいサブフォルダ作成のモック
        mock_post.return_value.json.return_value = {"status": "success", "data": {"id": "child_folder_id", "name": "ChildFolder"}}

        folder_id = self.eagle_sender._get_or_create_folder_id("ParentFolder/ChildFolder")

        # get_folder_list が1回呼ばれることを確認
        mock_get.assert_called_once()
        # create_folder が1回呼ばれることを確認
        mock_post.assert_called_once_with(f"{self.base_url}/api/folder/create", headers={"Content-Type": "application/json"}, json={"name": "ChildFolder", "parent": "parent_folder_id"})
        self.assertEqual(folder_id, "child_folder_id")

    @patch('eagle_client.sender.EagleSender._get_or_create_folder_id')
    @patch('eagle_client.api_client.EagleAPI.add_item_from_path')
    def test_send_to_eagle_with_folder(self, mock_add_item, mock_get_or_create_folder_id):
        mock_get_or_create_folder_id.return_value = "mock_folder_id"
        mock_add_item.return_value = {"status": "success", "data": {"id": "mock_item_id"}}

        filefullpath = "/path/to/test.png"
        filename = "test.png"
        annotation = "Test Annotation"
        tags = ["tag1", "tag2"]
        folder_name = "MyFolder"

        result = self.eagle_sender.send_to_eagle(filefullpath, filename, annotation, tags, folder_name)

        mock_get_or_create_folder_id.assert_called_once_with(folder_name)
        mock_add_item.assert_called_once_with(data={
            "path": filefullpath,
            "name": filename,
            "annotation": annotation,
            "tags": tags
        }, folder_id="mock_folder_id")
        self.assertEqual(result["data"]["id"], "mock_item_id")

if __name__ == '__main__':
    unittest.main()