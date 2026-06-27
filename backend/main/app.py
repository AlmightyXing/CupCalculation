from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# 此处仅作示例，实际应用中可以动态导入或预加载所有的干员逻辑
from backend.function.battle.engine import BattleEnvironment
from backend.function.battle.enemy import Enemy
# from backend.function.logic.operators.char_103_angel import Char103Angel

app = FastAPI(title="明日方舟杯级模拟后端")

class SimulateRequest(BaseModel):
    operator_id: str
    enemy_id: str

@app.get("/")
def root():
    return {"message": "杯级模拟服务器已启动"}

@app.post("/api/simulate")
def simulate_battle(req: SimulateRequest):
    """
    接收前端参数，构建战斗环境并跑出伤害数据
    """
    env = BattleEnvironment()
    
    # [开发中] 通过工厂模式或 getattr 根据 ID 获取对应的对象实例
    # op = Char103Angel(data=...)
    # env.add_operator(op)
    
    # [开发中] 获取敌人实例
    dummy_enemy = Enemy(req.enemy_id, "测试敌人", 100000, 500, 20)
    env.add_enemy(dummy_enemy)
    
    result = env.simulate()
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
