from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QDialog, QComboBox, QLineEdit, 
                           QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from utils.weather import (get_weather_info, get_weather_by_city, 
                         get_province_list, get_cities_by_province,
                         get_districts_by_city, get_adcode_by_location,
                         is_municipality)

class LocationDialog(QDialog):
    def __init__(self, parent=None, api_key=None):
        super().__init__(parent)
        self.api_key = api_key
        self.setup_ui()
        
        # 设置初始位置
        if parent and isinstance(parent, WeatherWidget):
            self.province_combo.setCurrentText(parent.current_province)
            # 触发省份变化，加载城市列表
            self.on_province_changed(parent.current_province)
            self.city_combo.setCurrentText(parent.current_city)
            # 触发城市变化，加载区县列表
            self.on_city_changed(parent.current_city)
            if parent.current_district:
                self.district_combo.setCurrentText(parent.current_district)

    def setup_ui(self):
        self.setWindowTitle("天气设置")
        self.setFixedWidth(500)
        layout = QVBoxLayout(self)
        
        # API Key 设置区域
        api_group = QGroupBox("API Key 设置")
        api_layout = QVBoxLayout()
        
        # API Key 输入框和按钮
        api_input_layout = QHBoxLayout()
        self.api_input = QLineEdit(self.api_key if self.api_key else "")
        self.api_input.setPlaceholderText("请输入高德地图 API Key")
        verify_btn = QPushButton("验证")
        verify_btn.clicked.connect(self.verify_api_key)
        
        api_input_layout.addWidget(self.api_input)
        api_input_layout.addWidget(verify_btn)
        
        # API Key 说明文本
        api_info = QLabel(
            "获取方式：\n"
            "1. 访问高德开放平台：https://lbs.amap.com\n"
            "2. 注册账号并创建应用\n"
            "3. 获取应用的 API Key"
        )
        api_info.setWordWrap(True)
        
        api_layout.addLayout(api_input_layout)
        api_layout.addWidget(api_info)
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # 位置选择区域
        location_group = QGroupBox("位置设置")
        location_layout = QVBoxLayout()
        
        # 省份选择
        province_layout = QHBoxLayout()
        province_label = QLabel("省份")
        self.province_combo = QComboBox()
        self.province_combo.addItems(get_province_list())
        self.province_combo.currentTextChanged.connect(self.on_province_changed)
        province_layout.addWidget(province_label)
        province_layout.addWidget(self.province_combo)
        
        # 城市选择
        city_layout = QHBoxLayout()
        city_label = QLabel("城市")
        self.city_combo = QComboBox()
        self.city_combo.currentTextChanged.connect(self.on_city_changed)
        city_layout.addWidget(city_label)
        city_layout.addWidget(self.city_combo)
        
        # 区县选择
        district_layout = QHBoxLayout()
        district_label = QLabel("区县")
        self.district_combo = QComboBox()
        district_layout.addWidget(district_label)
        district_layout.addWidget(self.district_combo)
        
        location_layout.addLayout(province_layout)
        location_layout.addLayout(city_layout)
        location_layout.addLayout(district_layout)
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # 确定取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                padding-top: 12px;
                margin-top: 12px;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                padding: 6px 12px;
                font-size: 14px;
            }
        """)
        
    def verify_api_key(self):
        """验证 API Key 是否有效"""
        key = self.api_input.text().strip()
        if not key:
            QMessageBox.warning(self, "验证失败", "请输入 API Key")
            return
            
        # 尝试使用该 key 获取天气信息
        try:
            # 使用北京的 adcode 进行测试
            weather_info = get_weather_info('110100', key)
            if weather_info:
                QMessageBox.information(self, "验证成功", "API Key 有效！")
                self.api_key = key
            else:
                QMessageBox.warning(self, "验证失败", "API Key 无效，请检查后重试")
        except Exception as e:
            QMessageBox.warning(self, "验证失败", f"验证过程出错：{str(e)}")

    def get_api_key(self):
        """获取当前设置的 API Key"""
        return self.api_input.text().strip()

    def on_province_changed(self, province):
        """处理省份选择变化"""
        self.city_combo.clear()
        self.district_combo.clear()
        cities = get_cities_by_province(province)
        self.city_combo.addItems(cities)
        if is_municipality(province) and cities:
            self.city_combo.setCurrentText(province)
            
    def on_city_changed(self, city):
        """处理城市选择变化"""
        if not city:
            return
        self.district_combo.clear()
        province = self.province_combo.currentText()
        districts = get_districts_by_city(province, city)
        self.district_combo.addItems(districts)

class WeatherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.api_key = None
        self.current_province = "广东省"
        self.current_city = "深圳市"
        self.current_district = "宝安区"
        self.setup_ui()
        
    def setup_ui(self):
        # 使用垂直布局作为主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)  # 增加边距
        
        # 创建一个带背景的容器
        container = QWidget()
        container.setObjectName("weatherContainer")
        container.setStyleSheet("""
            #weatherContainer {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
        """)
        
        # 容器的内部布局
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 12, 15, 12)  # 内部边距
        layout.setSpacing(15)  # 增加组件间距
        
        # 左侧信息区域（位置和天气）
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)  # 位置和天气信息之间的间距
        
        # 位置信息容器
        location_container = QWidget()
        location_layout = QHBoxLayout(location_container)
        location_layout.setContentsMargins(0, 0, 0, 0)
        location_layout.setSpacing(8)
        
        # 设置按钮
        self.settings_btn = QPushButton("📍")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # 鼠标悬停时显示手型
        self.settings_btn.clicked.connect(self.show_location_dialog)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 16px;
                padding: 0;
                margin: 0;
                color: #495057;
            }
            QPushButton:hover {
                color: #228be6;
            }
        """)
        
        # 当前位置显示
        self.location_label = QLabel(f"{self.current_province} {self.current_city} {self.current_district}")
        self.location_label.setStyleSheet("""
            font-size: 15px;
            color: #495057;
            font-weight: 500;
        """)
        
        location_layout.addWidget(self.settings_btn)
        location_layout.addWidget(self.location_label)
        
        # 分隔线
        separator = QLabel("|")
        separator.setStyleSheet("""
            color: #dee2e6;
            margin: 0 10px;
            font-size: 15px;
        """)
        
        # 天气信息
        self.weather_label = QLabel("点击📍设置天气信息")
        self.weather_label.setStyleSheet("""
            font-size: 15px;
            color: #495057;
        """)
        
        # 组装布局
        info_layout.addWidget(location_container)
        info_layout.addWidget(separator)
        info_layout.addWidget(self.weather_label)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        main_layout.addWidget(container)
        
    def save_api_key(self):
        """保存 API key 到配置文件"""
        # 获取主窗口实例
        main_window = self.window()
        if hasattr(main_window, 'save_config'):
            main_window.save_config()
            
    def show_location_dialog(self):
        dialog = LocationDialog(self, self.api_key)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 获取并保存新的 API Key
            new_key = dialog.get_api_key()
            if new_key:
                self.api_key = new_key
                self.save_api_key()
            
            # 更新位置信息
            self.current_province = dialog.province_combo.currentText()
            self.current_city = dialog.city_combo.currentText()
            self.current_district = dialog.district_combo.currentText()
            
            # 更新显示
            location_text = f"{self.current_province} {self.current_city}"
            if self.current_district:
                location_text = f"{self.current_province} {self.current_city} {self.current_district}"
            self.location_label.setText(location_text)
            
            # 更新天气信息
            self.update_weather_info()
    
    def update_weather_info(self):
        """更新天气信息"""
        if not self.api_key:
            self.weather_label.setText("请先设置 API Key")
            return
            
        try:
            if self.current_district:
                adcode = get_adcode_by_location(
                    self.current_province, 
                    self.current_city,
                    self.current_district,
                    self.api_key
                )
            else:
                adcode = get_adcode_by_location(
                    self.current_province, 
                    self.current_city,
                    api_key=self.api_key
                )
                
            if adcode:
                weather_info = get_weather_info(adcode, self.api_key)
                if weather_info:
                    self.weather_label.setText(
                        f"🌡️ {weather_info['temperature']}°C  💨 {weather_info['winddirection']}风"
                        f"{weather_info['windpower']}级  💧 {weather_info['humidity']}%  "
                        f"⛅ {weather_info['weather']}")
                    return
                else:
                    self.weather_label.setText("API Key 无效，请重新设置")
                    return
                    
            self.weather_label.setText("无法获取天气信息")
        except Exception as e:
            self.weather_label.setText(f"获取天气信息失败：{str(e)}")

    def set_api_key(self, key):
        """设置 API key"""
        self.api_key = key

    def set_theme(self, theme_name):
        """设置主题"""
        if theme_name == "暗夜主题":
            container_style = """
                #weatherContainer {
                    background-color: #343a40;
                    border: 1px solid #495057;
                    border-radius: 8px;
                }
            """
            text_color = "#dee2e6"
            hover_color = "#74c0fc"
        else:
            container_style = """
                #weatherContainer {
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                }
            """
            text_color = "#495057"
            hover_color = "#228be6"

        self.setStyleSheet(container_style)
        
        self.location_label.setStyleSheet(f"""
            font-size: 15px;
            color: {text_color};
            font-weight: 500;
        """)
        
        self.weather_label.setStyleSheet(f"""
            font-size: 15px;
            color: {text_color};
        """)
        
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background: transparent;
                font-size: 16px;
                padding: 0;
                margin: 0;
                color: {text_color};
            }}
            QPushButton:hover {{
                color: {hover_color};
            }}
        """)

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
                text-align: center;
            }
            QPushButton:hover {
                color: white;
                background-color: #FF4444;
                border-radius: 4px;
            }
        """)
        return delete_btn