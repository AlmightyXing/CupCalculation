import os
import json
import traceback
from backend.main.operator_repo import repo
from backend.function.battle.enemy import Enemy

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/Operators")
os.makedirs(DATA_DIR, exist_ok=True)

def generate_full_json(enemy_def: int, enemy_res: int):
    filename = f"operator_{enemy_def}_{enemy_res}.json"
    filepath = os.path.join(DATA_DIR, filename)
    
    print(f"Generating full JSON for {enemy_def} DEF / {enemy_res} RES...")
    
    if not repo.operator_data:
        repo.load_all()
        
    op_names = [op["name"] for op in repo.get_operator_list()]
    enemy = Enemy(f"target_{enemy_def}_{enemy_res}", "Target", 1000000, enemy_def, enemy_res)
    
    cached_data = {}
    
    for name in op_names:
        try:
            op = repo.instantiate_operator(name)
            if not hasattr(op, "final_base_atk"):
                op.final_base_atk = op.base_atk
                
            op_skills_data = []
            for i, skill_info in enumerate(op.skills):
                try:
                    res = op.calculate_dps(enemy, i)
                    op_skills_data.append({
                        "skill_idx": i,
                        "skill_name": skill_info.get("name", f"技能 {i+1}"),
                        "skill_type": skill_info.get("skill_type", "manual"),
                        "dps": res.get("dps", 0),
                        "total_dmg": res.get("total_damage", 0),
                        "cycle_dps": res.get("cycle_dps", res.get("dps", 0))
                    })
                except Exception as e:
                    op_skills_data.append({
                        "skill_idx": i,
                        "skill_name": skill_info.get("name", f"技能 {i+1}"),
                        "skill_type": skill_info.get("skill_type", "manual"),
                        "dps": "N/A",
                        "total_dmg": "N/A",
                        "cycle_dps": "N/A"
                    })
            cached_data[name] = op_skills_data
        except Exception as e:
            cached_data[name] = [{
                "skill_idx": 0,
                "skill_name": "N/A",
                "skill_type": "N/A",
                "dps": "N/A",
                "total_dmg": "N/A",
                "cycle_dps": "N/A"
            }]
            
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cached_data, f, ensure_ascii=False, indent=2)
        
    print(f"Finished {filename}")

if __name__ == "__main__":
    for def_val, res_val in [(0, 0), (1000, 20), (2000, 40), (3000, 60), (4000, 80), (5000, 100)]:
        generate_full_json(def_val, res_val)
