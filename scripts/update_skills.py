import os
import json
import re

directory = r"e:\Local_AI_Station\CupCalculation\data\parsed_data"

def process_skill(skill):
    desc = skill.get("description", "")
    current_type = skill.get("skill_type")
    duration = skill.get("duration")

    is_permanent = "持续时间无限" in desc or "切换" in desc
    
    if is_permanent:
        return "permanent"

    is_manual_base = current_type in ["manual", "continuous", "instant"]
    is_auto_base = current_type == "auto"
    
    is_ammo = re.search(r"装有.*[枚发]弹药", desc) is not None
    
    if is_manual_base and is_ammo:
        return "continuous"
    if is_auto_base and is_ammo:
        return "auto"

    is_deploy = "部署后" in desc
    if is_deploy:
        if duration is not None and duration != 0:
            return "continuous"
        else:
            return "instant"

    if is_manual_base:
        if duration is not None and duration != 0: # Treats 0 and None both as null just in case
            return "continuous"
        else:
            return "instant"
    elif is_auto_base:
        return "auto"
    else:
        return current_type

def main():
    count = 0
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
                    continue
            
            modified = False
            if "skills" in data:
                for skill in data["skills"]:
                    new_type = process_skill(skill)
                    if new_type != skill.get("skill_type"):
                        skill["skill_type"] = new_type
                        modified = True
                        
            if modified:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                count += 1
    print(f"Updated {count} files.")

if __name__ == "__main__":
    main()
