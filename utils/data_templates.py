"""
数据处理模板管理
"""

import streamlit as st

def get_stored_password():
    """从 secrets 获取存储的密码"""
    try:
        password = st.secrets.get("TEMPLATE_PASSWORD", "")
        # 调试：显示密码信息（部署后删除）
        st.write(f"【调试】从 Secrets 读取的密码长度: {len(password)}")
        if password:
            st.write(f"【调试】密码前3位: {password[:3]}...")
        else:
            st.write("【调试】Secrets 中没有 TEMPLATE_PASSWORD")
        return str(password).strip() if password else ""
    except Exception as e:
        st.write(f"【调试】读取 Secrets 失败: {e}")
        return ""

def verify_password(input_password):
    """验证密码"""
    stored = get_stored_password()
    if not stored:
        return False
    return str(input_password).strip() == stored

def is_authorized():
    """检查是否已授权"""
    return st.session_state.get('template_authorized', False)

def authorize(password):
    """授权验证"""
    if verify_password(password):
        st.session_state.template_authorized = True
        return True
    return False

def logout():
    """登出"""
    st.session_state.template_authorized = False

# 模板定义
PROCESSING_TEMPLATES = {
    "P1": {
        "name": "OB",
        "description": "处理订单数据：删除空列 → 提升标题 → 分列状态 → 分列选择 → 筛选",
        "protected": True,
         "steps": [
        {"type": "删除列", "params": {"columns": ["Column1", "Column3"]}},
        {"type": "提升为标题", "params": {"row_number": 1}},
        {"type": "分列", "params": {"column": "状态", "separator": "\n", "mode": "最左分隔符"}},
        {"type": "删除列", "params": {"columns": ["输赢/佣金", "状态.3", "状态.4"]}},
        {"type": "分列", "params": {"column": "选择", "separator": "\n", "mode": "最右分隔符"}},
        {"type": "分列", "params": {"column": "选择_1", "separator": "\n", "mode": "最右分隔符"}},
        {"type": "分列", "params": {"column": "选择_1_1", "separator": "\n", "mode": "最右分隔符"}},
        {"type": "分列", "params": {"column": "选择_1_1_1", "separator": "\n", "mode": "最右分隔符"}},
        {"type": "修改表头", "params": {"old_name": "选择_1_1_1_1", "new_name": "下注项"}},
        {"type": "修改表头", "params": {"old_name": "选择_1_1_1_2", "new_name": "玩法"}},
        {"type": "修改表头", "params": {"old_name": "选择_1_1_2", "new_name": "对阵"}},
        {"type": "修改表头", "params": {"old_name": "选择_1_2", "new_name": "联赛"}},
        {"type": "修改表头", "params": {"old_name": "选择_2", "new_name": "开赛时间"}},
        {"type": "修改表头", "params": {"old_name": "状态_1", "new_name": "输赢状态"}},
        {"type": "修改表头", "params": {"old_name": "状态_2", "new_name": "IP"}},
        {"type": "筛选", "params": {"column": "交易时间", "condition": "不等于", "value": "总和"}},
        {"type": "筛选", "params": {"column": "注单号码", "condition": "不为空"}},
        {"type": "类型转换", "params": {"columns": ["承租公司輸贏/佣金", "投注额"], "target_type": "数值"}},
        {"type": "类型转换", "params": {"column": "开赛时间", "target_type": "日期时间"}},
        {"type": "类型转换", "params": {"column": "交易时间", "target_type": "日期时间"}},
        {"type": "删除列", "params": {"columns": ["选择", "选择_1", "选择_1_1", "选择_1_1_1"]}}
    ]
    },
    
    "P2": {
        "name": "FB",
        "description": "清洗销售数据：提升标题 → 转换数值 → 去重",
        "protected": True,
        "steps": [
            {"type": "清理表头", "params": {"pattern": "/.*$", "replacement": ""}},
        
        {"type": "删除列", "params": {"columns": ["会员ID", "渠道", "赛事ID", "提前结算本金", "提前结算返还", "结算时间", "第三方备注", "风险自负", "是否预约", "兑人民币汇率", "正常结算本金", 
            "正常结算返还","订单ID"]}},
        
        {"type": "类型转换", "params": {"columns": ["会员ID","订单ID","赛事ID","投注额","公司输赢","会员输赢" ], "target_type": "数值"}},
        {"type": "类型转换", "params": {"columns": ["投注时间","赛事时间"], "target_type": "日期时间"}},
        {"type": "类型转换", "params": {"columns": [
            "渠道会员ID","渠道","状态","备注","二次结算","投注类型","运动","联赛","赛事","是否滚球","玩法阶段","玩法名称","选项","球线",
            "下注时比分","投注结果","赛果","赔率", "盘口类型","币种","ip地址","设备"
        ], "target_type": "文本"}},
        
        {"type": "筛选", "params": {"column": "状态", "condition": "包含", "value": "已确认"}},
        {"type": "筛选", "params": {"column": "状态", "condition": "包含", "value": "已结算"}}
        ]
    },
    
    "P3": {
        "name": "用户数据清洗",
        "description": "清洗用户数据：删除空列 → 替换状态值",
        "protected": True,
        "steps": [
            {"type": "删除空列", "params": {}},
            {"type": "替换", "params": {"column": "状态", "old": "0", "new": "无效"}},
            {"type": "替换", "params": {"column": "等级", "old": "null", "new": "普通"}}
        ]
    },
    
    "P4": {
        "name": "分列处理",
        "description": "按逗号分列",
        "protected": True,
        "steps": [
            {"type": "分列", "params": {"column": "数据", "separator": ",", "mode": "最左分隔符"}}
        ]
    },
    
    "P5": {
        "name": "模板5",
        "description": "待配置",
        "protected": True,
        "steps": []
    },
    
    "P6": {
        "name": "模板6",
        "description": "待配置",
        "protected": True,
        "steps": []
    },
    
    "P7": {
        "name": "模板7",
        "description": "待配置",
        "protected": True,
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