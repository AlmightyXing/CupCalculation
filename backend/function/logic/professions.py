from backend.function.logic.base_operator import Operator


class Liberator(Operator):
    """
    职业：解放者
    """
    def __init__(self, data: dict):
        super().__init__(data)
        # 此处可以根据游戏设定设置该职业的默认攻击间隔等
        self.attack_interval = 1.0 
        self.block_count = 1

class UnknownProfession(Operator):
    """
    职业：无畏者
    """
    def __init__(self, data: dict):
        super().__init__(data)
        # 此处可以根据游戏设定设置该职业的默认攻击间隔等
        self.attack_interval = 1.0 
        self.block_count = 1

class Lord(Operator):
    """
    职业：领主
    """
    def __init__(self, data: dict):
        super().__init__(data)
        # 此处可以根据游戏设定设置该职业的默认攻击间隔等
        self.attack_interval = 1.0 
        self.block_count = 1

class CoreCaster(Operator):
    """
    职业：中坚术师
    """
    def __init__(self, data: dict):
        super().__init__(data)
        # 此处可以根据游戏设定设置该职业的默认攻击间隔等
        self.attack_interval = 1.0 
        self.block_count = 1

class PhalanxCaster(Operator):
    """
    职业：阵法术师
    """
    def __init__(self, data: dict):
        super().__init__(data)
        # 此处可以根据游戏设定设置该职业的默认攻击间隔等
        self.attack_interval = 1.0 
        self.block_count = 1

class Deadeye(Operator):
    """
    职业：神射手
    """
    def __init__(self, data: dict):
        super().__init__(data)
        # 此处可以根据游戏设定设置该职业的默认攻击间隔等
        self.attack_interval = 1.0 
        self.block_count = 1

class Marksman(Operator):
    """
    职业：速射手
    """
    def __init__(self, data: dict):
        super().__init__(data)
        # 此处可以根据游戏设定设置该职业的默认攻击间隔等
        self.attack_interval = 1.0 
        self.block_count = 1

class HeavyShooter(Operator):
    """
    职业：重射手
    """
    def __init__(self, data: dict):
        super().__init__(data)
        # 此处可以根据游戏设定设置该职业的默认攻击间隔等
        self.attack_interval = 1.0 
        self.block_count = 1

class Trapmaster(Operator):
    """
    职业：陷阱师
    """
    def __init__(self, data: dict):
        super().__init__(data)
        # 此处可以根据游戏设定设置该职业的默认攻击间隔等
        self.attack_interval = 1.0 
        self.block_count = 1
