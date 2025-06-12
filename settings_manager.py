import json
import os

class SettingsManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.settings = self._load_settings()

    def _get_default_settings(self):
        """返回默认设置"""
        return {
            "focus_minutes": 90,
            "break_minutes": 20,
            "micro_break_seconds": 10,
            "random_interval_min": 3,
            "random_interval_max": 5,
            "sound_file": "alert.mp3"
        }

    def _load_settings(self):
        """从 JSON 文件加载设置，如果文件不存在或无效则创建/使用默认设置"""
        if not os.path.exists(self.config_file):
            default_settings = self._get_default_settings()
            self.save_settings(default_settings)
            return default_settings
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # 文件损坏或无法读取，返回默认值
            return self._get_default_settings()

    def save_settings(self, settings_data):
        """将设置保存到 JSON 文件"""
        self.settings = settings_data
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)

    def get(self, key):
        """获取一个设置项"""
        return self.settings.get(key)