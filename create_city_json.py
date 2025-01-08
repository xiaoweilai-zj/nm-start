import json
import os
from typing import Dict, List, Optional
import requests

class CityDataGenerator:
    """城市数据生成器"""
    
    API_URL = "https://restapi.amap.com/v3/config/district"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.city_data: Dict[str, Dict] = {}
        
    def fetch_district_data(self, keywords: str = "中国") -> Optional[List[Dict]]:
        """获取行政区划数据"""
        params = {
            "key": self.api_key,
            "keywords": keywords,
            "subdistrict": 3,  # 获取三级行政区划
            "extensions": "base"
        }
        
        try:
            response = requests.get(self.API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "1" and data["districts"]:
                return data["districts"]
            return None
            
        except Exception as e:
            print(f"获取行政区划数据失败: {str(e)}")
            return None
            
    def process_district_data(self, districts: List[Dict]):
        """处理行政区划数据"""
        for province in districts[0]["districts"]:
            province_name = province["name"]
            self.city_data[province_name] = {
                "adcode": province["adcode"],
                "cities": {}
            }
            
            # 处理城市
            for city in province["districts"]:
                city_name = city["name"]
                self.city_data[province_name]["cities"][city_name] = {
                    "adcode": city["adcode"],
                    "districts": {}
                }
                
                # 处理区县
                for district in city["districts"]:
                    district_name = district["name"]
                    self.city_data[province_name]["cities"][city_name]["districts"][district_name] = {
                        "adcode": district["adcode"]
                    }
                    
    def save_data(self, output_path: str):
        """保存城市数据到文件"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.city_data, f, ensure_ascii=False, indent=2)
            print(f"城市数据已保存到: {output_path}")
        except Exception as e:
            print(f"保存城市数据失败: {str(e)}")
            
    def generate(self, output_path: str) -> bool:
        """生成城市数据"""
        print("开始获取城市数据...")
        
        # 获取数据
        districts = self.fetch_district_data()
        if not districts:
            print("获取城市数据失败")
            return False
            
        # 处理数据
        print("正在处理城市数据...")
        self.process_district_data(districts)
        
        # 保存数据
        print("正在保存城市数据...")
        self.save_data(output_path)
        
        return True


def main():
    """主函数"""
    # 高德地图API密钥
    API_KEY = "your_api_key_here"  # 替换为你的API密钥
    
    # 输出文件路径
    output_path = os.path.join("resources", "city_data.json")
    
    # 生成城市数据
    generator = CityDataGenerator(API_KEY)
    if generator.generate(output_path):
        print("城市数据生成完成！")
    else:
        print("城市数据生成失败！")


if __name__ == "__main__":
    main() 