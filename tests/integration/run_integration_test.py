import requests
import os
import time
from PIL import Image
import numpy as np

from eagle_client.api_client import EagleAPI
from eagle_client.sender import EagleSender

def create_dummy_image(path="dummy_image.png"):
    """ダミーのPNG画像を生成する"""
    img = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
    img.save(path)
    return path

def main():
    base_url = "http://localhost:41595"
    eagle_api = EagleAPI(base_url)
    eagle_sender = EagleSender(base_url)

    print("--- Eagle API 結合テスト開始 ---")

    # 1. Eagle APIが起動しているか確認
    try:
        response = requests.get(f"{base_url}/api/application/info")
        response.raise_for_status()
        print(f"Eagle API接続成功: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Eagle API接続失敗: {e}")
        print("Eagleアプリケーションが起動していることを確認してください。")
        return

    # 2. フォルダ作成テスト
    test_folder_name = "ComfyUITestFolder_" + str(int(time.time()))
    test_nested_folder_name = f"{test_folder_name}/SubFolder/NestedFolder"
    try:
        print(f"\nフォルダ '{test_nested_folder_name}' を作成中...")
        created_folder_id = eagle_sender._get_or_create_folder_id(test_nested_folder_name)
        if created_folder_id:
            print(f"フォルダ '{test_nested_folder_name}' 作成成功。ID: {created_folder_id}")
        else:
            print(f"フォルダ '{test_nested_folder_name}' 作成失敗。")
            return
    except Exception as e:
        print(f"フォルダ作成中にエラーが発生しました: {e}")
        return

    # 3. 画像追加テスト
    dummy_image_path = create_dummy_image()
    try:
        print(f"\n画像 '{dummy_image_path}' を '{test_nested_folder_name}' に追加中...")
        result = eagle_sender.send_to_eagle(
            filefullpath=os.path.abspath(dummy_image_path),
            filename=os.path.basename(dummy_image_path),
            annotation="結合テスト用画像",
            tags=["test", "comfyui"],
            full_folder_path=test_nested_folder_name
        )
        if result and result.get("status") == "success":
            print(f"画像追加成功: {result}")
        else:
            print(f"画像追加失敗: {result}")
    except Exception as e:
        print(f"画像追加中にエラーが発生しました: {e}")
    finally:
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)

    print("\n--- Eagle API 結合テスト完了 ---")

if __name__ == '__main__':
    main()
