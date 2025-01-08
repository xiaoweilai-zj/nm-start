import json
import os
import sys

class ConfigManager:
    def __init__(self, config_path=None):
        # 如果没有指定配置文件路径，则使用程序运行目录下的 config.json
        if config_path is None:
            # 获取程序运行目录
            if getattr(sys, 'frozen', False):
                # 如果是打包后的可执行文件
                app_dir = os.path.dirname(sys.executable)
            else:
                # 如果是开发环境
                app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            self.config_path = os.path.join(app_dir, 'config.json')
        else:
            self.config_path = config_path

    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 如果配置文件不存在，返回默认配置
                return self.get_default_config()
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
            return self.get_default_config()

    def save_config(self, config_data):
        """保存配置"""
        try:
            # 确保配置文件所在目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
            return False

    def get_default_config(self):
        """获取默认配置"""
        return {
            'theme': '默认主题',
            'programs': [],
            'weather_visible': False,
            'weather_api_key': None
        }
