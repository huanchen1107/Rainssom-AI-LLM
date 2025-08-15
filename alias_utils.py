# alias_utils.py

import pandas as pd

def normalize_query(query: str) -> str:
    """
    對使用者查詢中的醫美療程名稱進行標準化。
    """
    alias_map = {
        "PicoWay": ["皮秒", "皮秒雷射", "超皮秒"],
        "SylfirmX": ["矽谷電波", "矽谷電波X"],
        "ThermageFLX": ["鳳凰電波", "電波"],
        "Ulthera": ["音波拉提", "極線音波", "音波"],
        "PLT": ["PLT凍晶", "PLT"],
        "Exosome": ["外泌體", "外泌體凍乾"],
        "Sculptra": ["舒顏萃", "4D童妍針", "童顏針"],
        "AestheFill": ["艾麗斯", "百變艾麗斯", "精靈針"],
        "Sunmax": ["双美膚力原", "膚力原"],
        "Botox": ["保妥適", "肉毒"],
    }

    # 進行關鍵字替換
    for standard_name, aliases in alias_map.items():
        for alias in aliases:
            if alias in query:
                query = query.replace(alias, standard_name)
    return query