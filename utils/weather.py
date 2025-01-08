import requests
import json
import os
import sys

def load_city_data():
    try:
        # 获取JSON文件路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            base_path = sys._MEIPASS
        else:
            # 如果是开发环境
            base_path = os.path.dirname(os.path.dirname(__file__))
            
        json_path = os.path.join(base_path, 'resources', 'city_data.json')
        
        # 读取JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载城市数据失败：{str(e)}")
        return None

def get_weather_info(adcode, api_key):
    """获取天气信息"""
    url = f"https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": api_key,
        "city": adcode,
        "extensions": "base"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "1" and data["lives"]:
            return data["lives"][0]
    except Exception as e:
        print(f"获取天气信息失败: {str(e)}")
    
    return None

def get_province_list():
    """获取省份列表"""
    city_data = load_city_data()
    return list(city_data.keys())

def get_cities_by_province(province):
    """获取指定省份的城市列表"""
    city_data = load_city_data()
    if province in city_data:
        # 返回城市列表（不包括区）
        cities = list(city_data[province]["cities"].keys())
        # 如果是直辖市，只返回市本身
        if len(cities) == 1 and cities[0] == province:
            return cities
        return sorted(cities)  # 按字母顺序排序
    return []

def get_districts_by_city(province, city):
    """获取指定城市的区列表"""
    city_data = load_city_data()
    if province in city_data and city in city_data[province]["cities"]:
        return list(city_data[province]["cities"][city]["districts"].keys())
    return []

def get_adcode_by_location(province, city, district=None, api_key=None):
    """获取区域编码"""
    city_data = load_city_data()
    if province in city_data:
        if city in city_data[province]["cities"]:
            if district:
                # 如果指定了区，返回区的adcode
                districts = city_data[province]["cities"][city]["districts"]
                if district in districts:
                    return districts[district]["adcode"]
            else:
                # 如果只指定到市，返回市的adcode
                return city_data[province]["cities"][city]["adcode"]
    return None

def get_weather_by_city(province, city):
    """根据省份和城市获取天气信息"""
    adcode = get_adcode_by_location(province, city)
    if adcode:
        return get_weather_info(adcode)
    return None

def is_municipality(province):
    """判断是否为直辖市"""
    return province in ["北京市", "上海市", "天津市", "重庆市"]
