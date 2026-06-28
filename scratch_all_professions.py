import os, glob, json, re

parsed_dir = 'data/parsed_data'

prof_map = {}

for json_path in glob.glob(os.path.join(parsed_dir, '*.json')):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    char_type = data.get('character', {}).get('character_type', 'Unknown')
    desc = data.get('character', {}).get('character_description', '')
    atk_time = data.get('atk_time', 1.0)
    
    if char_type not in prof_map:
        prof_map[char_type] = {
            'description': desc,
            'atk_time': atk_time,
            'count': 1
        }
    else:
        prof_map[char_type]['count'] += 1

with open('scratch_all_professions.json', 'w', encoding='utf-8') as f:
    json.dump(prof_map, f, ensure_ascii=False, indent=2)
