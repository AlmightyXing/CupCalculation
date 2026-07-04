from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from backend.main.operator_repo import repo
from backend.function.battle.enemy import Enemy
from backend.function.battle.engine import BattleEnvironment
from backend.function.battle.rank_engine import generate_ranking

# --- Models ---
class OperatorRequest(BaseModel):
    name: str
    skill_index: int = -1

class SimulateRequest(BaseModel):
    enemy_level: int
    team: List[OperatorRequest]

# --- App Setup ---
app = FastAPI(title="Cup Calculation Backend API")

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

@app.on_event("startup")
async def startup_event():
    # 在启动时将干员数据载入内存
    repo.load_all()

import os
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../frontend")
app.mount("/app", StaticFiles(directory=frontend_dir, html=True), name="static")

avatars_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/avatars_head_portrait")
if os.path.exists(avatars_dir):
    app.mount("/avatars", StaticFiles(directory=avatars_dir), name="avatars")


# --- Endpoints ---
@app.get("/api/operators")
async def get_operators():
    """获取所有可用干员的列表信息"""
    op_list = repo.get_operator_list()
    # 按照稀有度降序排序，稀有度相同按名字排序
    op_list.sort(key=lambda x: (-(x.get('rarity') or 0), x['name']))
    return {"status": "success", "data": op_list}

@app.get("/api/operator/{name}")
async def get_operator_detail(name: str):
    """获取指定名称干员的完整数据字典"""
    # 考虑到干员中英文或URL编码等情况，需在repo的内存里找
    op_data = repo.operator_data.get(name)
    if not op_data:
        raise HTTPException(status_code=404, detail=f"Operator '{name}' not found.")
    return {"status": "success", "data": op_data}


@app.get("/api/enemies")
async def get_enemies():
    """获取预设敌人木桩的等级和属性说明"""
    return {
        "status": "success",
        "data": [
            {"level": 0, "name": "0防0抗", "def": 0, "res": 0},
            {"level": 1, "name": "1000防 20抗", "def": 1000, "res": 20},
            {"level": 2, "name": "2000防 30抗", "def": 2000, "res": 40},
            {"level": 3, "name": "3000防 40抗", "def": 3000, "res": 60},
            {"level": 4, "name": "4000防 60抗", "def": 4000, "res": 80},
            {"level": 5, "name": "5000甲 100抗", "def": 5000, "res": 100},
            {"level": 99, "name": "专用测试木桩", "def": 2000, "res": 40}
        ]
    }

@app.get("/api/rankings")
async def get_rankings(enemy_def: int = 1000, enemy_res: int = 20):
    """
    根据给定的敌人防御和法抗，返回全服 130 名干员的实时 DPS/总伤排行榜
    """
    try:
        res = generate_ranking(enemy_def, enemy_res)
        return res
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ranking calculation failed: {str(e)}")

@app.post("/api/simulate")
async def run_simulation(req: SimulateRequest):
    """根据传递的干员和技能阵型进行协同模拟运算"""
    if not req.team:
        raise HTTPException(status_code=400, detail="Team cannot be empty")
        
    try:
        # 创建环境
        env = BattleEnvironment()
        
        # 组装木桩
        enemy = Enemy.get_dummy_target(req.enemy_level)
        env.add_enemy(enemy)
        
        # 组装干员队伍
        for op_req in req.team:
            try:
                op_instance = repo.instantiate_operator(op_req.name)
                env.add_operator(op_instance, skill_index=op_req.skill_index)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
                
        # 运行模拟
        result = env.simulate()
        
        # 处理返回结果以便于前端渲染
        # 将 result['combat_report'] 格式化为数组形式
        combat_report_list = []
        for op_id, reps in result.get('combat_report', {}).items():
            # 找到干员的名字
            op_name = op_id
            for op, _ in env.operators:
                if op.character_id == op_id:
                    op_name = op.raw_data.get('name', op_id)
                    break
                    
            for rep in reps:
                combat_report_list.append({
                    "operator_id": op_id,
                    "operator_name": op_name,
                    "enemy_id": rep["enemy_id"],
                    "dps": round(rep["dps"], 2),
                    "total_damage": round(rep["total_damage"], 2)
                })
        
        return {
            "status": "success",
            "data": {
                "enemy": {
                    "id": enemy.enemy_id,
                    "base_def": enemy.base_def,
                    "base_res": enemy.base_res,
                },
                "applied_buffs": result.get("applied_buffs", {}),
                "combat_report": combat_report_list
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
class SandboxSimulateRequest(BaseModel):
    operator_name: str
    skill_index: int = 0
    enemy_def: int = 0
    enemy_res: int = 0
    buffs: Optional[List[str]] = None

@app.post("/api/sandbox/simulate")
async def sandbox_simulate(req: SandboxSimulateRequest):
    """战斗环境（沙盒）接口，单干员实时演算"""
    try:
        op_instance = repo.instantiate_operator(req.operator_name)
        enemy = Enemy("sandbox_target", "Target", 1000000, req.enemy_def, req.enemy_res)
        
        if not hasattr(op_instance, "final_base_atk"):
            op_instance.final_base_atk = op_instance.base_atk
            
        result = op_instance.calculate_dps(enemy, req.skill_index)
        
        return {
            "status": "success",
            "data": {
                "dps": round(result.get("dps", 0), 2),
                "total_damage": round(result.get("total_damage", 0), 2),
                "cycle_dps": round(result.get("cycle_dps", result.get("dps", 0)), 2)
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Sandbox simulation failed: {str(e)}")
        
if __name__ == "__main__":
    import uvicorn
    # 为了方便单独执行脚本也可以启动
    uvicorn.run("backend.main.api_server:app", host="0.0.0.0", port=8000, reload=True)
