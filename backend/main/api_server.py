from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from backend.main.operator_repo import repo
from backend.function.battle.enemy import Enemy
from backend.function.battle.engine import BattleEnvironment

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

@app.on_event("startup")
async def startup_event():
    # 在启动时将干员数据载入内存
    repo.load_all()

# --- Endpoints ---
@app.get("/api/operators")
async def get_operators():
    """获取所有可用干员的列表信息"""
    op_list = repo.get_operator_list()
    # 按照稀有度降序排序，稀有度相同按名字排序
    op_list.sort(key=lambda x: (-(x.get('rarity') or 0), x['name']))
    return {"status": "success", "data": op_list}

@app.get("/api/enemies")
async def get_enemies():
    """获取预设敌人木桩的等级和属性说明"""
    return {
        "status": "success",
        "data": [
            {"level": 0, "name": "0防0抗 纯沙包", "def": 0, "res": 0},
            {"level": 1, "name": "低甲低抗 (500防 20抗)", "def": 500, "res": 20},
            {"level": 2, "name": "中甲中抗 (1000防 30抗)", "def": 1000, "res": 30},
            {"level": 3, "name": "高甲高抗 (2000防 40抗)", "def": 2000, "res": 40},
            {"level": 4, "name": "超高甲超高抗 (3000防 60抗)", "def": 3000, "res": 60},
            {"level": 5, "name": "神仙面板 (5000防 100抗)", "def": 5000, "res": 100},
            {"level": 99, "name": "自定义 2000防 40抗", "def": 2000, "res": 40}
        ]
    }

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
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # 为了方便单独执行脚本也可以启动
    uvicorn.run("backend.main.api_server:app", host="0.0.0.0", port=8000, reload=True)
