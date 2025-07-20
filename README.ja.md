# ComfyUI-send-Eagle(slim)
[English README](README.md)

生成された画像を [Eagle](https://en.eagle.cool/) へ webp形式で連携する [ComfyUI](https://github.com/comfyanonymous/ComfyUI) 用 拡張ノードです。本拡張ノードは前作 [ComfyUI-send-Eagle](https://github.com/shingo1228/ComfyUI-send-eagle) のEagle連携機能を、本ノードに必要な機能に絞って実装し直したものです。

![](misc/sss_top_eagle_ss.jpg)
![](misc/workflow.svg)

## 機能
![](misc/sss_node_visual.jpg)

入力:`image`で入力された生成画像を、webpまたはpng形式でローカルで起動中のEagleに連携します。<br>
webp形式は非可逆圧縮（画質設定）、及び可逆圧縮形式を選択可能です。<br>

- **柔軟なテキスト入力**: `prompt_text`、`negative_text`、`memo_text` を直接入力し、Eagleでのアノテーションやタグとして使用できます。これらの入力はオプションになりました。
- **カスタムフォルダ選択**: 画像を保存するEagle内の `folder_name` を指定できます。フォルダが存在しない場合は、ルートフォルダに保存されます。
- **PNGメタデータ保持**: PNG形式で画像を保存する場合、`prompt` および `extra_pnginfo` がメタデータとして埋め込まれ、画像をComfyUIにドラッグ＆ドロップすることでワークフローを再現できます。

## インストール
1. ComfyUIのカスタムノードディレクトリに移動します
2. `git clone https://github.com/shingo1228/ComfyUI-send-eagle-slim.git`

## 設定
本拡張ノードは、一部の設定に `config.json` を使用します。拡張機能のルートディレクトリに `config.json.template` というテンプレートファイルが提供されています。

設定をカスタマイズするには：
1. `config.json.template` を `config` ディレクトリ内の `config/default_config.json` にコピーします。
2. `config/default_config.json` を編集してパラメータを調整します。

`config/default_config.json` が見つからない場合、デフォルト設定が使用されます。

## 更新
1. クローンしたリポジトリに移動します (例: `custom_nodes/ComfyUI-send-eagle-slim`)
2. `git pull`

## 変更履歴
- 2023/08/17 初期版リリース
- 2023/08/18 `KSampler With Refiner (Fooocus)`,`SDXL Prompt Styler` に暫定対応
- 2023/08/22 `prompt`情報を解析しEagleに送信するフラグを追加
- 2023/08/31 `prompt`、`extra_pnginfo`を**Eagleに送らない（send_promptをdisable）**をデフォルトに変更
- 2024/01/25 新規ノード "Send Eagle with text"を追加
- 2024/07/20 モジュール性と保守性向上のため、プロジェクト構造をリファクタリング。
- 2024/07/20 ノードUIの `prompt_text` および `negative_text` をオプション入力に変更。
- 2024/07/20 Eagleの保存先フォルダを指定する `folder_name` 入力を追加。
- 2024/07/20 メタデータ保持機能を備えたPNG画像保存を実装。
- 2024/07/20 Eagleクライアント機能の単体テストおよび結合テストを追加。
- 2024/07/20 APIの制限により、自動フォルダ作成機能をロールバック。
