import json
import os

class ConfigLoader:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
        except FileNotFoundError:
            print(f"[ComfyUI-send-eagle-slim] Config file not found: {config_path}")
            self._config = {}
        except json.JSONDecodeError:
            print(f"[ComfyUI-send-eagle-slim] Error decoding config file: {config_path}")
            self._config = {}

    def get(self, key, default=None):
        return self._config.get(key, default)

    def set(self, key, value):
        self._config[key] = value
        # Optionally, save the config back to file if changes need to be persistent
        # self._save_config()

    def _save_config(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_config.json")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ComfyUI-send-eagle-slim] Error saving config file: {e}")

