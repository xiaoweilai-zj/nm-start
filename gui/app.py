from PyQt6.QtWidgets import QApplication
from gui.main_frame import MainWindow
import sys
import os

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        # 使用相对路径获取图标
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, 'resources', 'nm.ico')
        self.window = MainWindow(icon_path)
        self.window.show()
        
    def run(self):
        return self.app.exec()