import os
import json
import requests
import re
from pathlib import Path

# 获取 gamedata
print("Downloading character table...")
data = requests.get('https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/master/zh_CN/gamedata/excel/character_table.json').json()

# 建立一个 name 到 displayNumber 的映射
name_to_display = {}
for k, v in data.items():
    if v.get('rarity') == 'TIER_6':
        name_to_display[v['name']] = v.get('displayNumber', 'UNKNOWN')

parsed_dir = Path('data/parsed_data')
count = 0
for file in parsed_dir.glob('*.json'):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            j = json.load(f)
        
        name = j.get('name')
        if name and name in name_to_display:
            display_num = name_to_display[name]
            
            # 使用安全字符
            op_name_safe = re.sub(r'[\\\\/*?:"<>|]', '_', name)
            display_num_safe = re.sub(r'[\\\\/*?:"<>|]', '_', display_num)
            
            new_name = f'{display_num_safe}_{op_name_safe}.json'
            new_path = parsed_dir / new_name
            
            # 避免重复或自身
            if file.name != new_name:
                print(f"Renaming {file.name} to {new_name}")
                file.rename(new_path)
                count += 1
    except Exception as e:
        print(f'Rename failed for {file}: {e}')

print(f'Successfully renamed {count} files.')
