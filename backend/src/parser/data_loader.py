"""
数据加载工具
处理 character_sample.json 格式的文件读写
"""

import json
from pathlib import Path
from typing import List

from src.calculator.models import (
    CharacterData, SkillData, TalentData, SkillParams
)


def load_character(json_path: Path) -> CharacterData:
    """
    从 JSON 文件加载干员数据（兼容 character_sample.json 格式）。

    如果 JSON 中技能已有 skill_params 字段，也会一并加载。
    """
    data = json.loads(json_path.read_text(encoding="utf-8"))

    talents = [
        TalentData(
            talent_id=t["talent_id"],
            talent_name=t["talent_name"],
            talent_decription=t.get("talent_decription", ""),
        )
        for t in data.get("talents", [])
    ]

    skills = []
    for s in data.get("skills", []):
        skill_params = None
        # 若 JSON 内已含解析好的 skill_params，直接加载
        if "skill_params" in s and s["skill_params"]:
            sp = s["skill_params"]
            skill_params = SkillParams(**sp)

        skills.append(SkillData(
            skill_id=s["skill_id"],
            skill_name=s["skill_name"],
            skill_type=s["skill_type"],
            duration=s.get("duration"),
            description=s.get("description", ""),
            skill_params=skill_params,
        ))

    char_info = data.get("character", {})

    return CharacterData(
        character_id=data["character_id"],
        name=data["name"],
        nickname=data.get("nickname", []),
        base_atk=data["base_atk"] + data.get("confidence_atk", 0),
        base_hp=data["base_hp"] + data.get("confidence_hp", 0),
        base_def=data["base_def"] + data.get("confidence_def", 0),
        base_res=data["base_res"] + data.get("confidence_res", 0),
        atk_time=data["atk_time"],
        confidence_atk=data.get("confidence_atk", 0),
        confidence_hp=data.get("confidence_hp", 0),
        confidence_def=data.get("confidence_def", 0),
        confidence_res=data.get("confidence_res", 0),
        character_type=char_info.get("character_type", ""),
        character_description=char_info.get("character_description", ""),
        talents=talents,
        skills=skills,
    )


def load_all_characters(data_dir: Path) -> List[CharacterData]:
    """加载目录下所有 JSON 干员文件"""
    chars = []
    for json_file in sorted(data_dir.glob("*.json")):
        try:
            chars.append(load_character(json_file))
        except Exception as e:
            print(f"  ✗ 加载失败 {json_file.name}：{e}")
    return chars
