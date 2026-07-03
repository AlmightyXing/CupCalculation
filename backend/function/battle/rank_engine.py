import os
import json
import traceback
from typing import Dict, List, Any
from backend.main.operator_repo import repo
from backend.function.battle.enemy import Enemy

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../data/Operators")

def init_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def _get_cup_level(rank: int, total: int) -> str:
    """
    前10%是超大杯·上，10%-20%是超大杯·中，20%-30%是超大杯·下，30%-60%是大杯，60%以后是中杯
    """
    if total == 0:
        return "中杯"
    
    percentile = rank / total
    
    if percentile <= 0.10:
        return "超大杯·上"
    elif percentile <= 0.20:
        return "超大杯·中"
    elif percentile <= 0.30:
        return "超大杯·下"
    elif percentile <= 0.60:
        return "大杯"
    else:
        return "中杯"

def generate_ranking(enemy_def: int, enemy_res: int) -> Dict[str, Any]:
    init_data_dir()
    
    filename = f"operator_{enemy_def}_{enemy_res}.json"
    filepath = os.path.join(DATA_DIR, filename)
    
    # Load existing cache
    cached_data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
        except Exception:
            pass
            
    # Load all operators
    if not repo.operator_data:
        repo.load_all()
        
    op_names = [op["name"] for op in repo.get_operator_list()]
    
    # Create enemy
    # In case we need an exact match, we can just create a custom Enemy object
    enemy = Enemy(f"target_{enemy_def}_{enemy_res}", "Target", 1000000, enemy_def, enemy_res)
    
    dirty = False
    
    for name in op_names:
        if name not in cached_data:
            dirty = True
            try:
                op = repo.instantiate_operator(name)
                # Ensure final_base_atk is set for safety
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
                        # Log error locally if interrupted/crashed
                        error_log_path = os.path.join(DATA_DIR, "../../logs/phase6_errors.log")
                        os.makedirs(os.path.dirname(error_log_path), exist_ok=True)
                        with open(error_log_path, "a", encoding="utf-8") as lf:
                            lf.write(f"Error calculating {name} skill {i}:\n{traceback.format_exc()}\n")
                            
                cached_data[name] = op_skills_data
            except Exception as e:
                error_log_path = os.path.join(DATA_DIR, "../../logs/phase6_errors.log")
                os.makedirs(os.path.dirname(error_log_path), exist_ok=True)
                with open(error_log_path, "a", encoding="utf-8") as lf:
                    lf.write(f"Error instantiating {name}:\n{traceback.format_exc()}\n")
    
    if dirty:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cached_data, f, ensure_ascii=False, indent=2)
            
    # Now we have all performances, calculate rankings
    # Idle: auto skills, highest cycle_dps
    # Burst: manual skills, highest total_damage
    
    operator_scores = []
    
    for op_name, skills in cached_data.items():
        best_idle_dps = 0
        best_burst_dmg = 0
        best_overall_dps = 0
        best_overall_total = 0
        
        for sk in skills:
            if sk.get("skill_type") == "auto":
                if sk.get("cycle_dps", 0) > best_idle_dps:
                    best_idle_dps = sk.get("cycle_dps", 0)
            elif sk.get("skill_type") == "manual":
                if sk.get("total_dmg", 0) > best_burst_dmg:
                    best_burst_dmg = sk.get("total_dmg", 0)
            
            if sk.get("dps", 0) > best_overall_dps:
                best_overall_dps = sk.get("dps", 0)
            if sk.get("total_dmg", 0) > best_overall_total:
                best_overall_total = sk.get("total_dmg", 0)
                
        # Some operators only have auto skills, or only manual skills.
        # Fallbacks: if no auto skill, use highest manual DPS.
        if best_idle_dps == 0:
            best_idle_dps = best_overall_dps
        if best_burst_dmg == 0:
            best_burst_dmg = best_overall_total
            
        # 补充干员属性以便前端渲染
        op_info = repo.operator_data.get(op_name, {})
        
        operator_scores.append({
            "name": op_name,
            "profession": op_info.get("character_type", "未知"),
            "rarity": op_info.get("rarity", 6),
            "idle_score": best_idle_dps,
            "burst_score": best_burst_dmg,
            "best_dps": best_overall_dps,
            "best_total_dmg": best_overall_total,
            "skills": skills
        })
        
    # Rank Idle
    operator_scores.sort(key=lambda x: x["idle_score"], reverse=True)
    for i, op in enumerate(operator_scores):
        op["idleRank"] = i + 1
        
    # Rank Burst
    operator_scores.sort(key=lambda x: x["burst_score"], reverse=True)
    for i, op in enumerate(operator_scores):
        op["burstRank"] = i + 1
        
    # Combine ranks for Total Cup
    # A simple combined score: lower is better
    for op in operator_scores:
        op["combined_score"] = op["idleRank"] + op["burstRank"]
        
    operator_scores.sort(key=lambda x: x["combined_score"])
    
    total_ops = len(operator_scores)
    
    # Assign Total Cup Rank and Cup Level
    for i, op in enumerate(operator_scores):
        op["totalRank"] = i + 1
        op["cup_level"] = _get_cup_level(i + 1, total_ops)
        # Default rank to use in frontend depending on tab
        op["rank"] = i + 1
        
    return {
        "status": "success",
        "data": {
            "operators": operator_scores
        }
    }
