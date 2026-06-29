import os
import json
import glob
import importlib.util
import inspect
from typing import Dict, List, Type, Optional
from backend.function.logic.base_operator import Operator

class OperatorRepository:
    """
    负责在内存中缓存所有的干员 JSON 数据和对应的 Python Class，
    避免每次模拟演算都进行 IO 操作和动态导包。
    """
    def __init__(self):
        # character_name -> json dict
        self.operator_data: Dict[str, dict] = {}
        # character_name -> Operator subclass
        self.operator_classes: Dict[str, Type[Operator]] = {}
        
    def load_all(self, data_dir: str = "data/parsed_data", scripts_dir: str = "backend/function/logic/operators"):
        """加载所有数据和脚本到内存"""
        print("开始加载干员仓库...")
        
        # 1. 加载 JSON
        if os.path.exists(data_dir):
            for file_name in os.listdir(data_dir):
                if file_name.endswith(".json"):
                    file_path = os.path.join(data_dir, file_name)
                    with open(file_path, "r", encoding="utf-8") as f:
                        try:
                            data = json.load(f)
                            name = data.get("name")
                            if name:
                                self.operator_data[name] = data
                        except Exception as e:
                            print(f"Error loading {file_name}: {e}")
                            
        # 2. 加载 Python Classes
        if os.path.exists(scripts_dir):
            script_files = glob.glob(os.path.join(scripts_dir, "*.py"))
            for file_path in script_files:
                module_name = os.path.basename(file_path).replace(".py", "")
                if module_name == "__init__":
                    continue
                    
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec is None or spec.loader is None:
                        continue
                        
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 查找定义的 Operator 子类
                    for obj_name, obj in inspect.getmembers(module, inspect.isclass):
                        # 确保类确实继承自 Operator 且是这个文件里定义的，而不是 import 进来的
                        if issubclass(obj, Operator) and obj.__module__ == module.__name__:
                            # 提取名字，文件命名规范是 id_名字.py，所以分割后取最后一段
                            # 如果包含多个下划线，取最后一部分
                            op_name = module_name.split("_")[-1]
                            self.operator_classes[op_name] = obj
                            break # 一个文件通常只有一个主体类
                            
                except Exception as e:
                    print(f"Failed to load operator script {file_path}: {e}")
                    
        print(f"干员仓库加载完成：成功读取 {len(self.operator_data)} 份数据，映射 {len(self.operator_classes)} 个干员逻辑类。")
        
    def get_operator_list(self) -> List[dict]:
        """为前端返回轻量级的干员列表（仅包含在 python 脚本中有对应逻辑的干员）"""
        result = []
        for name, data in self.operator_data.items():
            if name in self.operator_classes:
                result.append({
                    "id": data.get("character_id"),
                    "name": name,
                    "profession": data.get("character_type"),
                    "subProfessionId": data.get("subProfessionId"),
                    "rarity": data.get("rarity"),
                    "skills": [s.get("skill_name") for s in data.get("skills", [])]
                })
        return result
        
    def instantiate_operator(self, name: str) -> Operator:
        """根据名字实例化干员对象"""
        if name not in self.operator_data or name not in self.operator_classes:
            raise ValueError(f"未找到干员 {name} 的完整数据或逻辑代码。")
            
        op_class = self.operator_classes[name]
        op_data = self.operator_data[name]
        return op_class(op_data)

# 单例对象，在服务器启动时初始化
repo = OperatorRepository()
