import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton, QVBoxLayout, 
                           QHBoxLayout, QListWidget, QFileDialog, QMessageBox,
                           QLabel, QSplitter, QInputDialog, QListWidgetItem,
                           QComboBox, QDialog)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QIcon, QColor
from utils.config import ConfigManager
from utils.weather import (get_weather_info, get_weather_by_city, 
                         get_province_list, get_cities_by_province,
                         get_districts_by_city, get_adcode_by_location,
                         is_municipality)
import subprocess
from gui.weather_widget import WeatherWidget  # 添加导入

class MainWindow(QMainWindow):
    def __init__(self, icon_path):
        super().__init__()
        self.setWindowTitle("🐮🐴启动器")
        self.setMinimumSize(1000, 600)  # 增加最小宽度到1000
        
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

        # 配置管理
        self.config_manager = ConfigManager()  # 不再传入固定路径
        
        # 主窗口布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(0)  # 隐藏分割线
        splitter.setChildrenCollapsible(False)  # 禁止折叠
        
        # 左面板
        left_panel = QWidget()
        left_panel.setFixedWidth(200)  # 固定左侧面板宽度
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)  # 设置按钮之间的间距
        left_layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        
        # 按钮数据
        buttons_data = [
            ("⊕ 选择程序", self.on_select_program),
            ("▶ 启动程序", self.on_start_programs),
            ("💾 保存程序", self.on_save_programs),
            ("🗑 清除所有", self.on_clear_all),
            ("🎨 切换主题", self.on_choose_theme),
            ("🌤 天气显示", self.toggle_weather)
        ]
        
        for text, handler in buttons_data:
            btn = QPushButton(text)
            btn.setMinimumHeight(40)  # 增加按钮高度
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 5px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #4a90e2;
                    color: white;
                }
            """)
            btn.clicked.connect(handler)
            left_layout.addWidget(btn)
        
        left_layout.addStretch()  # 添加弹性空间
        
        # 右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # 设置右侧面板的最小宽度
        right_panel.setMinimumWidth(700)  # 增加最小宽度
        
        # 天气信息
        self.weather_widget = WeatherWidget()
        self.weather_widget.hide()  # 默认隐藏天气组件
        
        # 程序列表区域
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)  # 移除间距
        
        # 表头容器
        header_container = QWidget()
        header_container.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
        """)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(15, 12, 15, 12)
        header_layout.setSpacing(10)  # 设置间距与列表项一致
        
        # 表头标签
        name_header = QLabel("程序名称")
        name_header.setFixedWidth(220)  # 增加宽度
        name_header.setMinimumWidth(220)
        name_header.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        path_header = QLabel("程序路径")
        path_header.setFixedWidth(400)  # 增加宽度
        path_header.setMinimumWidth(400)
        path_header.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        operation_header = QLabel("操作")
        operation_header.setFixedWidth(80)
        operation_header.setMinimumWidth(80)
        operation_header.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                padding: 0;
                qproperty-alignment: AlignCenter;
            }
        """)
        
        # 添加一个弹性空间，确保右对齐
        header_layout.addWidget(name_header)
        header_layout.addWidget(path_header)
        header_layout.addWidget(operation_header)
        header_layout.addStretch()
        
        # 程序列表
        self.programs_list = QListWidget()
        self.programs_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.programs_list.setSizeAdjustPolicy(QListWidget.SizeAdjustPolicy.AdjustToContents)
        self.programs_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.programs_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                outline: none;
                text-align: center;
            }
            QListWidget::item {
                padding: 0;
                border-bottom: 1px solid #eee;
                background-color: transparent;
            }
            QListWidget::item:last-child {
                border-bottom: none;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background-color: transparent;
                color: black;
            }
            QListWidget::item:focus {
                background-color: transparent;
                outline: none;
            }
        """)
        
        list_layout.addWidget(header_container)
        list_layout.addWidget(self.programs_list)
        
        # 添加到右侧布局
        right_layout.addWidget(self.weather_widget)
        right_layout.addWidget(list_container)
        
        # 添加到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.statusBar().showMessage("🐮🐴启动器 - 一键启动牛马所有要用到的程序。@PangHu")
        
        # 添加时间标签到状态栏右侧
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: #666666;
                padding: 0 10px;
            }
        """)
        self.statusBar().addPermanentWidget(self.time_label)
        
        # 创建定时器更新时间
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 每秒更新一次
        self.update_time()  # 立即更新一次时间
        
        self.current_theme = "深蓝主题"  # 添加默认主题
        self.load_config()
        self.update_weather_info()

    def toggle_weather(self):
        """切换天气组件的显示状态"""
        if self.weather_widget.isVisible():
            self.weather_widget.hide()
        else:
            self.weather_widget.show()
            # 只在显示时且有 API key 时更新天气
            if self.weather_widget.api_key:
                self.weather_widget.update_weather_info()

    def on_select_program(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择应用程序",
            "",
            "可执行文件 (*.exe)"
        )
        for file_path in files:
            program_name = os.path.basename(file_path)
            item, item_widget = self.create_program_item(program_name, file_path)
            self.programs_list.addItem(item)
            self.programs_list.setItemWidget(item, item_widget)
            
        self.save_config()

    def create_label(self, text: str, width: int) -> QLabel:
        """创建统一样式的标签"""
        label = QLabel(text)
        label.setFixedWidth(width)
        label.setMinimumWidth(width)
        return label

    def create_delete_button(self) -> QPushButton:
        """创建统一样式的删除按钮"""
        delete_btn = QPushButton("删除")
        delete_btn.setFixedWidth(80)
        delete_btn.setMinimumWidth(80)
        delete_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: #FF4444;
                font-size: 14px;
                background-color: transparent;
                padding: 0;
                margin: 0;
                qproperty-alignment: AlignCenter;
            }
            QPushButton:hover {
                color: white;
                background-color: #FF4444;
                border-radius: 4px;
            }
        """)
        return delete_btn

    def create_program_item(self, name: str, path: str) -> tuple[QListWidgetItem, QWidget]:
        """创建程序列表项"""
        item = QListWidgetItem()
        item_widget = QWidget()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(10)
        
        # 使用辅助方法创建标签和按钮
        name_label = self.create_label(name, 220)
        path_label = self.create_label(path, 400)
        delete_btn = self.create_delete_button()
        delete_btn.clicked.connect(lambda: self.remove_program(item))
        
        layout.addWidget(name_label)
        layout.addWidget(path_label)
        layout.addWidget(delete_btn)
        layout.addStretch()
        
        item_widget.setLayout(layout)
        item.setSizeHint(item_widget.sizeHint())
        
        return item, item_widget

    def remove_program(self, item):
        row = self.programs_list.row(item)
        self.programs_list.takeItem(row)
        self.save_config()

    def on_start_programs(self):
        if self.programs_list.count() == 0:
            QMessageBox.information(self, "提示", "请先选择需要启动的程序。")
            return
            
        if self.programs_list.count() > 10:
            reply = QMessageBox.question(self, "确认启动", 
                                       "您即将启动超过10个程序。是否继续？",
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
                
        for i in range(self.programs_list.count()):
            item = self.programs_list.item(i)
            widget = self.programs_list.itemWidget(item)
            path_label = widget.layout().itemAt(1).widget()
            program_path = path_label.text()
            
            try:
                subprocess.Popen(program_path)
            except Exception as e:
                QMessageBox.critical(self, "启动失败", 
                                   f"无法启动应用程序：{program_path}\n错误信息{str(e)}")

    def get_programs_data(self):
        """获取程序列表数据"""
        programs = []
        try:
            for i in range(self.programs_list.count()):
                item = self.programs_list.item(i)
                widget = self.programs_list.itemWidget(item)
                if widget and widget.layout():
                    name_label = widget.layout().itemAt(0).widget()
                    path_label = widget.layout().itemAt(1).widget()
                    
                    if name_label and path_label:
                        programs.append({
                            'name': name_label.text(),
                            'path': path_label.text()
                        })
        except Exception as e:
            print(f"获取程序数据时发生错误: {str(e)}")
        
        return programs

    def on_save_programs(self):
        """保存程序列表"""
        reply = QMessageBox(self)
        reply.setWindowTitle("保存确认")
        reply.setText("是否保存当前程序列表？")
        reply.setIcon(QMessageBox.Icon.Question)
        
        save_button = reply.addButton("保存", QMessageBox.ButtonRole.YesRole)
        cancel_button = reply.addButton("取消", QMessageBox.ButtonRole.NoRole)
        
        reply.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: #333;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #ddd;
                padding: 5px 20px;
                border-radius: 3px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4a90e2;
                color: white;
                border: 1px solid #4a90e2;
            }
        """)
        
        reply.exec()
        
        if reply.clickedButton() == save_button:
            if self.save_config():  # 检查保存是否成功
                QMessageBox.information(self, "保存成功", "程序列表已保存！")
            else:
                QMessageBox.warning(self, "保存失败", "保存程序列表时发生错误！")

    def on_clear_all(self):
        """清除所有程序"""
        reply = QMessageBox(self)
        reply.setWindowTitle("清除确认")
        reply.setText("确定要清除所有程序吗？")
        reply.setIcon(QMessageBox.Icon.Warning)
        
        # 自定义按钮
        clear_button = reply.addButton("清除", QMessageBox.ButtonRole.YesRole)
        cancel_button = reply.addButton("取消", QMessageBox.ButtonRole.NoRole)
        
        # 设置对话框样式
        reply.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: #333;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #ddd;
                padding: 5px 20px;
                border-radius: 3px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4a90e2;
                color: white;
                border: 1px solid #4a90e2;
            }
        """)
        
        reply.exec()
        
        if reply.clickedButton() == clear_button:
            self.programs_list.clear()

    def on_choose_theme(self):
        """选择主题"""
        themes = ["默认主题", "黑色主题", "绿色主题"]
        current_index = themes.index(self.current_theme) if self.current_theme in themes else 0
        
        # 创建自定义对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("主题设置")
        dialog.setFixedWidth(300)
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        
        # 添加标签
        label = QLabel("请选择主题方案：")
        label.setStyleSheet("""
            color: #333;
            font-size: 14px;
            padding: 10px;
        """)
        layout.addWidget(label)
        
        # 添加下拉框
        combo = QComboBox()
        combo.addItems(themes)
        combo.setCurrentIndex(current_index)
        combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #ddd;
                padding: 5px;
                border-radius: 3px;
                min-width: 200px;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 1px solid #4a90e2;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(resources/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        layout.addWidget(combo)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        
        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(dialog.accept)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #ddd;
                padding: 5px 20px;
                border-radius: 3px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4a90e2;
                color: white;
                border: 1px solid #4a90e2;
            }
        """)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #ddd;
                padding: 5px 20px;
                border-radius: 3px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4a90e2;
                color: white;
                border: 1px solid #4a90e2;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 设置对话框样式
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)
        
        # 显示对话框
        if dialog.exec() == QDialog.DialogCode.Accepted:
            theme = combo.currentText()
            if theme != self.current_theme:
                self.current_theme = theme
                self.apply_theme(theme)
                # 保存配置
                self.save_config()

    def save_config(self):
        """保存配置到文件"""
        try:
            config_data = {
                'theme': getattr(self, 'current_theme', '默认主题'),
                'programs': self.get_programs_data(),
                'weather_visible': self.weather_widget.isVisible(),
                'weather_api_key': self.weather_widget.api_key  # 保存 API key
            }
            
            # 保存前先验证数据
            if not config_data['programs']:
                print("警告：没有要保存的程序数据")
                
            # 使用 config_manager 的路径
            print(f"配置文件路径: {self.config_manager.config_path}")
            print(f"要保存的数据: {config_data}")
            
            success = self.config_manager.save_config(config_data)
            if not success:
                print("保存配置失败")
                return False
                
            return True
            
        except Exception as e:
            print(f"保存配置时发生错误: {str(e)}")
            return False

    def load_config(self):
        config_data = self.config_manager.load_config()
        if not config_data:
            return

        if 'theme' in config_data:
            self.current_theme = config_data['theme']
            self.apply_theme(self.current_theme)

        if 'programs' in config_data:
            self.programs_list.clear()
            for program in config_data['programs']:
                if os.path.exists(program['path']):
                    item, item_widget = self.create_program_item(program['name'], program['path'])
                    self.programs_list.addItem(item)
                    self.programs_list.setItemWidget(item, item_widget)
    
        # 加载天气组件状态
        if 'weather_visible' in config_data:
            if config_data['weather_visible']:
                self.weather_widget.show()
            else:
                self.weather_widget.hide()

        # 加载天气 API key
        if 'weather_api_key' in config_data:
            self.weather_widget.set_api_key(config_data['weather_api_key'])

    def update_weather_info(self):
        """更新当前选中地区的天气信息"""
        # 直接调用 WeatherWidget 的更新方法
        self.weather_widget.update_weather_info()

    def apply_theme(self, theme_name):
        if theme_name == "黑色主题":
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; }
                QWidget#centralWidget { color: white; }
                QListWidget { 
                    background-color: #3b3b3b; 
                    color: white;
                    border: 1px solid #444;
                }
                QListWidget::item { 
                    background-color: #3b3b3b;
                    border-bottom: 1px solid #444;
                }
                QListWidget::item:hover { 
                    background-color: #444;
                }
                QPushButton { 
                    background-color: #4a4a4a; 
                    color: white;
                    border: 1px solid #555;
                }
                QPushButton:hover {
                    background-color: #555;
                }
                QLabel { 
                    color: white; 
                }
                .weather-widget {
                    background-color: #4a4a4a;
                    color: white;
                }
            """)
            
            # 单独设置天气组件样式
            self.weather_widget.setStyleSheet("""
                QWidget {
                    background-color: #4a4a4a;
                    color: white;
                    border-radius: 5px;
                }
                QLabel {
                    color: white;
                }
                QComboBox {
                    color: white;
                    background-color: #3b3b3b;
                    border: 1px solid #555;
                }
                QComboBox:hover {
                    border: 1px solid #666;
                }
            """)
            self.time_label.setStyleSheet("color: #aaaaaa; padding: 0 10px;")
            
        elif theme_name == "绿色主题":
            self.setStyleSheet("""
                QMainWindow { background-color: #e8f5e9; }
                QListWidget { 
                    background-color: white;
                    border: 1px solid #c8e6c9;
                }
                QListWidget::item { 
                    background-color: white;
                    border-bottom: 1px solid #c8e6c9;
                }
                QListWidget::item:hover { 
                    background-color: #f1f8e9;
                }
                QPushButton { 
                    background-color: #81c784;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #66bb6a;
                }
                .weather-widget {
                    background-color: #66bb6a;
                }
            """)
            self.time_label.setStyleSheet("color: #2e7d32; padding: 0 10px;")
            
        else:  
            self.setStyleSheet("""
                QMainWindow { background-color: white; }
                QListWidget { 
                    background-color: white;
                    border: 1px solid #ddd;
                }
                QListWidget::item { 
                    background-color: white;
                    border-bottom: 1px solid #eee;
                }
                QListWidget::item:hover { 
                    background-color: #f5f5f5;
                }
                QPushButton { 
                    background-color: white;
                    border: 1px solid #ddd;
                }
                QPushButton:hover {
                    background-color: #4a90e2;
                    color: white;
                }
            """)
            self.time_label.setStyleSheet("color: #666666; padding: 0 10px;")
        
        # 更新天气组件题
        self.weather_widget.set_theme(theme_name)
        
        # 设置对话框的全局样式
        self.setStyleSheet(self.styleSheet() + """
            QMessageBox, QInputDialog, QDialog {
                background-color: white;
            }
            QMessageBox QLabel, QInputDialog QLabel, QDialog QLabel {
                color: #333333;
            }
            QMessageBox QPushButton, QInputDialog QPushButton, QDialog QPushButton {
                background-color: white;
                color: #333333;
                border: 1px solid #ddd;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QMessageBox QPushButton:hover, QInputDialog QPushButton:hover, QDialog QPushButton:hover {
                background-color: #4a90e2;
                color: white;
                border: 1px solid #4a90e2;
            }
            QDialog QComboBox {
                background-color: white;
                color: #333333;
                border: 1px solid #ddd;
                padding: 5px;
                border-radius: 3px;
            }
            QDialog QComboBox:hover {
                border: 1px solid #4a90e2;
            }
        """)

    def on_item_double_clicked(self, item):
        # 由于我现在使用了定义的表项布局，击事件可以改为显示程序详细信息
        widget = self.programs_list.itemWidget(item)
        name_label = widget.layout().itemAt(0).widget()
        path_label = widget.layout().itemAt(1).widget()
        
        message = f"程序名称：{name_label.text()}\n程序路径：{path_label.text()}"
        QMessageBox.information(self, "程序信息", message)

    def update_time(self):
        current_time = QDateTime.currentDateTime()
        formatted_time = current_time.toString("yyyy-MM-dd hh:mm:ss")
        self.time_label.setText(formatted_time)