import sys
import os
import requests
import time
from PIL import Image
import numpy as np

# プロジェクトのルートディレクトリをPythonのパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

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

    # 2. 画像追加テスト (既存フォルダへの追加)
    dummy_image_path = create_dummy_image()
    try:
        print(f"\n画像 '{dummy_image_path}' を既存フォルダに追加中...")
        # ロールバック後のsend_to_eagleはfolder_nameを受け取る
        result = eagle_sender.send_to_eagle(
            filefullpath=os.path.abspath(dummy_image_path),
            filename=os.path.basename(dummy_image_path),
            annotation="結合テスト用画像",
            tags=["test", "comfyui"],
            folder_name="" # ルートフォルダに保存
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