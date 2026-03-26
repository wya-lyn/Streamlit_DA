"""
数据处理模板管理
存储预定义的数据处理流程模板
"""

# 模板定义
PROCESSING_TEMPLATES = {
    "P1": {
        "name": "OB",
        "description": "处理订单数据：删除空列 → 提升标题 → 分列状态 → 分列选择 → 筛选",
        "steps": [
            {"type": "删除列", "params": {"columns": ["Column1", "Column3"]}},
            {"type": "提升为标题", "params": {"row_number": 1}},
            {"type": "分列", "params": {"column": "状态", "separator": "\n", "mode": "最左分隔符"}},
            {"type": "删除列", "params": {"columns": ["输赢/佣金", "状态.3", "状态.4"]}},
            {"type": "分列", "params": {"column": "选择", "separator": "\n", "mode": "最右分隔符"}},
            {"type": "分列", "params": {"column": "选择_1", "separator": "\n", "mode": "最右分隔符"}},
            {"type": "分列", "params": {"column": "选择_1_1", "separator": "\n", "mode": "最右分隔符"}},
            {"type": "分列", "params": {"column": "选择_1_1_1", "separator": "\n", "mode": "最左分隔符"}},
            {"type": "修改表头", "params": {"old_name": "选择_1_1_1_1", "new_name": "下注项"}},
            {"type": "修改表头", "params": {"old_name": "选择_1_1_1_2", "new_name": "玩法"}},
            {"type": "修改表头", "params": {"old_name": "选择_1_1_2", "new_name": "对阵"}},
            {"type": "修改表头", "params": {"old_name": "选择_1_2", "new_name": "联赛"}},
            {"type": "修改表头", "params": {"old_name": "选择_2", "new_name": "开赛时间"}},
            {"type": "修改表头", "params": {"old_name": "状态_1", "new_name": "输赢状态"}},
            {"type": "修改表头", "params": {"old_name": "状态_2", "new_name": "IP"}},
            {"type": "筛选", "params": {"column": "交易时间", "condition": "不等于", "value": "总和"}},
            {"type": "筛选", "params": {"column": "注单号码", "condition": "不为空"}},
            {"type": "类型转换", "params": {"column": "开赛时间", "target_type": "文本"}},
            {"type": "类型转换", "params": {"column": "交易时间", "target_type": "日期时间"}},
            {"type": "删除列", "params": {"columns": ["选择","选择_1", "状态", "选择_1_1","选择_1_1_1","注单号码","系统账号"]}},
            {"type": "类型转换", "params": {"columns": [ "承租公司輸贏/佣金","投注额"], "target_type": "数值"}}
        ]
    },
    
    "P2": {
        "name": "销售报表清洗",
        "description": "清洗销售数据：提升标题 → 转换数值 → 去重",
        "steps": [
            {"type": "提升为标题", "params": {"row_number": 3}},
            {"type": "类型转换", "params": {"column": "销售额", "target_type": "数值"}},
            {"type": "类型转换", "params": {"column": "利润", "target_type": "数值"}},
            {"type": "去重", "params": {"subset": ["品牌名"], "keep": "first"}}
        ]
    },
    
    "P3": {
        "name": "用户数据清洗",
        "description": "清洗用户数据：删除空列 → 替换状态值",
        "steps": [
            {"type": "删除空列", "params": {}},
            {"type": "替换", "params": {"column": "状态", "old": "0", "new": "无效"}},
            {"type": "替换", "params": {"column": "等级", "old": "null", "new": "普通"}}
        ]
    },
    
    "P4": {
        "name": "分列处理",
        "description": "按逗号分列",
        "steps": [
            {"type": "分列", "params": {"column": "数据", "separator": ",", "mode": "最左分隔符"}}
        ]
    },
    
    "P5": {
        "name": "模板5",
        "description": "待配置",
        "steps": []
    },
    
    "P6": {
        "name": "模板6",
        "description": "待配置",
        "steps": []
    },
    
    "P7": {
        "name": "模板7",
        "description": "待配置",
        "steps": []
    }
}


def get_template_names():
    """获取所有模板名称列表"""
    return list(PROCESSING_TEMPLATES.keys())


def get_template(template_id):
    """获取指定模板"""
    return PROCESSING_TEMPLATES.get(template_id)


def get_template_by_name(name):
    """根据名称获取模板"""
    for tid, template in PROCESSING_TEMPLATES.items():
        if template["name"] == name:
            return template
    return None


def update_template(template_id, name, description, steps):
    """更新模板"""
    PROCESSING_TEMPLATES[template_id] = {
        "name": name,
        "description": description,
        "steps": steps
    }