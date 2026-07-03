import time
from backend.main.operator_repo import repo
from backend.function.battle.enemy import Enemy

def test_speed():
    repo.load_all()
    op_names = [op["name"] for op in repo.get_operator_list()]
    
    t0 = time.time()
    enemy = Enemy.get_dummy_target(2) # 1000 def, 30 res
    
    skill_results = []
    
    for name in op_names:
        op = repo.instantiate_operator(name)
        # Ensure final_base_atk is set for safety if engine doesn't set it
        if not hasattr(op, "final_base_atk"):
            op.final_base_atk = op.base_atk
            
        for i, skill in enumerate(op.skills):
            try:
                res = op.calculate_dps(enemy, i)
                skill_results.append({
                    "name": name,
                    "skill_idx": i,
                    "dps": res.get("dps", 0),
                    "total_dmg": res.get("total_damage", 0),
                    "cycle_dps": res.get("cycle_dps", res.get("dps", 0))
                })
            except Exception as e:
                print(f"Error in {name} skill {i}: {e}")
            
    t1 = time.time()
    print(f"Evaluated {len(skill_results)} skills in {t1-t0:.4f} seconds.")

if __name__ == "__main__":
    test_speed()
