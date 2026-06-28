import os, glob, json, re

parsed_dir = 'data/parsed_data'
op_dir = 'backend/function/logic/operators'

prof_map = {}

for py_file in glob.glob(os.path.join(op_dir, '*.py')):
    base_name = os.path.basename(py_file).replace('.py', '').upper()
    json_path = os.path.join(parsed_dir, f'{base_name}.json')
    if not os.path.exists(json_path):
        continue
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    char_type = data.get('character', {}).get('character_type', 'Unknown')
    desc = data.get('character', {}).get('character_description', '')
    atk_time = data.get('atk_time', 1.0)
    
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'class \w+\((\w+)\):', content)
    if match:
        base_class = match.group(1)
        # Avoid duplicate work
        if base_class not in prof_map:
            prof_map[base_class] = {
                'zh_name': char_type,
                'description': desc,
                'atk_time': atk_time
            }

with open('scratch_professions_data.json', 'w', encoding='utf-8') as f:
    json.dump(prof_map, f, ensure_ascii=False, indent=2)
