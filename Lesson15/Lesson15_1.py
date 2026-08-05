import os
import json
from pprint import pprint
from typing import Dict,Any

CONFIG_FILE = "products_config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        config_data:Dict = json.load(file)
        #pprint(config_data.get("project_name"))
        print(f"✅ 成功載入設定檔！專案名稱：{config_data.get('project_name')}")
        print(f"📦 監控品類數量：{len(config_data.get('monitor_products', []))} 大類")
else:
    print(f"❌ 找不到設定檔 {CONFIG_FILE}")