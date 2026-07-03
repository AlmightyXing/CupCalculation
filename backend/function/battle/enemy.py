class Enemy:
    """
    敌人实体基类
    """
    def __init__(self, enemy_id: str, name: str, base_hp: float, base_def: float, base_res: float):
        self.enemy_id = enemy_id
        self.name = name
        self.base_hp = base_hp
        self.base_def = base_def
        self.base_res = base_res
        
        # 实时状态（受 buff/debuff 影响）
        self.current_hp = base_hp
        self.current_def = base_def
        self.current_res = base_res
        
        # 战斗环境面板注入用全局状态
        self.is_cced = False # 是否被施加控制（如停顿、束缚、眩晕等）
        self.global_fragile = 0.0 # 全局脆弱倍率（例如 0.4 表示受到伤害增加40%）
        self.global_arts_flat_dmg = 0.0 # 全局法术附加伤害（每次法伤额外增加的点数）

    def reset(self):
        self.current_hp = self.base_hp
        self.current_def = self.base_def
        self.current_res = self.base_res
        self.is_cced = False
        self.global_fragile = 0.0
        self.global_arts_flat_dmg = 0.0

    def __str__(self):
        return f"[{self.enemy_id}] {self.name} (HP:{self.base_hp} DEF:{self.base_def} RES:{self.base_res})"

    @staticmethod
    def get_dummy_target(level: int):
        """
        获取标准测试木桩 (从 0防0抗 到 5000防100抗)
        """
        dummies = {
            0: Enemy("dummy_0", "0甲 0抗", 1000000, 0, 0),
            1: Enemy("dummy_1", "500甲 20抗", 1000000, 1000, 20),
            2: Enemy("dummy_2", "1000甲 20抗", 1000000, 2000, 40),
            3: Enemy("dummy_3", "2000甲 50抗", 1000000, 3000, 60),
            4: Enemy("dummy_4", "3000甲 70抗", 1000000, 4000, 80),
            5: Enemy("dummy_5", "5000甲 100抗", 1000000, 5000, 100),
            # 用户专门要求测试用的目标：2000防40抗
            99: Enemy("dummy_custom", "专用测试木桩", 1000000, 2000, 40)
        }
        return dummies.get(level, dummies[0])
