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

    def reset(self):
        self.current_hp = self.base_hp
        self.current_def = self.base_def
        self.current_res = self.base_res

    def __str__(self):
        return f"[{self.enemy_id}] {self.name} (HP:{self.base_hp} DEF:{self.base_def} RES:{self.base_res})"
