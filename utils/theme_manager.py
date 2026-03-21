"""
主题管理模块：处理深色/浅色主题切换
"""

import streamlit as st

class ThemeManager:
    """主题管理器，控制全局配色方案"""
    
    # ===========================================
    # 深色主题配色 - 科技感深色
    # ===========================================
    DARK_THEME = {
        # 背景色系 - 深邃科技感
        "bg_color": "#0A0C10",           # 主背景 - 深邃黑灰
        "block_bg": "#13161C",            # 区块背景 - 深灰蓝
        "card_bg": "#1A1F2A",             # 卡片背景 - 更深层次
        "sidebar_bg": "#0C0F14",          # 侧边栏背景
        
        # 文字色系 - 清晰明亮
        "text_primary": "#E8EDFF",        # 主要文字 - 柔和白蓝
        "text_secondary": "#9AA7C0",      # 次要文字 - 灰蓝
        "text_emphasis": "#FFFFFF",       # 强调文字 - 纯白
        "text_disabled": "#5A6A85",       # 禁用文字
        
        # 边框色系
        "border": "#2A2F3A",              # 边框/分割线
        "border_light": "#20242E",        # 浅色边框
        "border_active": "#6A4E9B",       # 激活边框
        
        # 按钮色系 - 科技感
        "button_normal": "#2A2F3A",       # 普通按钮
        "button_hover": "#3A4050",        # 按钮悬停
        "button_primary": "#6A4E9B",      # 主要按钮 - 神秘紫
        "button_primary_hover": "#7B5EAC", # 主要按钮悬停
        "button_secondary": "#2A5A6B",    # 次要按钮 - 科技蓝
        "button_secondary_hover": "#3A6A7B",
        "button_danger": "#8B3A3A",       # 危险按钮 - 暗红
        "button_danger_hover": "#9B4A4A",
        
        # 菜单色系
        "menu_bg": "#0C0F14",             # 菜单背景
        "menu_hover": "#1A1F2A",          # 菜单悬停
        "menu_selected": "#6A4E9B",       # 菜单选中
        
        # 特殊色系
        "ai_color": "#4A6A8B",            # AI功能 - 科技蓝
        "success_color": "#2A5A3A",       # 成功提示 - 墨绿
        "warning_color": "#8B6B2A",       # 警告提示 - 暗黄
        "info_color": "#2A5A6B",          # 信息提示 - 深蓝
        "accent_color": "#6A4E9B",        # 强调色
        
        # 图表色系
        "chart_color_1": "#6A4E9B",
        "chart_color_2": "#4A6A8B",
        "chart_color_3": "#2A8B6A",
        "chart_color_4": "#8B6A4A",
        "chart_color_5": "#9B4A6A",
        
        # 字体设置
        "font_family": """
            'Inter', 'Segoe UI', '微软雅黑', 'Microsoft YaHei', 
            -apple-system, BlinkMacSystemFont, sans-serif
        """,
        "code_font": "'Fira Code', Consolas, 'Courier New', monospace",
        
        # 圆角大小
        "border_radius_small": "6px",
        "border_radius_medium": "12px",
        "border_radius_large": "16px",
        
        # 阴影
        "shadow_small": "0 2px 4px rgba(0,0,0,0.3)",
        "shadow_medium": "0 4px 12px rgba(0,0,0,0.4)",
        "shadow_large": "0 8px 24px rgba(0,0,0,0.5)",
    }
    
    # ===========================================
    # 浅色主题配色 - 科技感浅色
    # ===========================================
    LIGHT_THEME = {
        # 背景色系 - 清爽科技感
        "bg_color": "#F5F7FC",            # 主背景 - 浅灰蓝
        "block_bg": "#FFFFFF",            # 区块背景 - 纯白
        "card_bg": "#FFFFFF",             # 卡片背景 - 纯白
        "sidebar_bg": "#F0F2F8",          # 侧边栏背景
        
        # 文字色系 - 深色清晰
        "text_primary": "#1A2634",        # 主要文字 - 深灰蓝
        "text_secondary": "#6C7A8A",      # 次要文字 - 中灰
        "text_emphasis": "#0A1A2A",       # 强调文字 - 深黑蓝
        "text_disabled": "#B0B8C4",       # 禁用文字
        
        # 边框色系
        "border": "#E8ECF2",              # 边框/分割线
        "border_light": "#F0F3F8",        # 浅色边框
        "border_active": "#6A4E9B",       # 激活边框
        
        # 按钮色系 - 现代感
        "button_normal": "#F0F2F8",       # 普通按钮
        "button_hover": "#E8ECF2",        # 按钮悬停
        "button_primary": "#6A4E9B",      # 主要按钮 - 紫色
        "button_primary_hover": "#7B5EAC", # 主要按钮悬停
        "button_secondary": "#4A6A8B",    # 次要按钮 - 科技蓝
        "button_secondary_hover": "#5A7A9B",
        "button_danger": "#DC3545",       # 危险按钮 - 红色
        "button_danger_hover": "#C82333",
        
        # 菜单色系
        "menu_bg": "#F0F2F8",             # 菜单背景
        "menu_hover": "#E8ECF2",          # 菜单悬停
        "menu_selected": "#6A4E9B",       # 菜单选中
        
        # 特殊色系
        "ai_color": "#5A7A9B",            # AI功能 - 科技蓝
        "success_color": "#28A745",       # 成功提示 - 绿色
        "warning_color": "#FFC107",       # 警告提示 - 橙色
        "info_color": "#17A2B8",          # 信息提示 - 青色
        "accent_color": "#6A4E9B",        # 强调色
        
        # 图表色系
        "chart_color_1": "#6A4E9B",
        "chart_color_2": "#4A6A8B",
        "chart_color_3": "#2A8B6A",
        "chart_color_4": "#B87C4A",
        "chart_color_5": "#9B4A6A",
        
        # 字体设置
        "font_family": DARK_THEME["font_family"],
        "code_font": DARK_THEME["code_font"],
        
        # 圆角大小
        "border_radius_small": "6px",
        "border_radius_medium": "12px",
        "border_radius_large": "16px",
        
        # 阴影
        "shadow_small": "0 2px 8px rgba(0,0,0,0.04)",
        "shadow_medium": "0 4px 16px rgba(0,0,0,0.06)",
        "shadow_large": "0 8px 32px rgba(0,0,0,0.08)",
    }
    
    @staticmethod
    def init_theme():
        """初始化主题设置"""
        if 'theme_mode' not in st.session_state:
            st.session_state.theme_mode = 'dark'
    
    @staticmethod
    def get_current_theme():
        """获取当前主题配色"""
        mode = st.session_state.get('theme_mode', 'dark')
        return ThemeManager.DARK_THEME if mode == 'dark' else ThemeManager.LIGHT_THEME
    
    @staticmethod
    def toggle_theme():
        """切换主题"""
        current = st.session_state.theme_mode
        st.session_state.theme_mode = 'light' if current == 'dark' else 'dark'
    
    @staticmethod
    def apply_custom_css():
        """应用自定义CSS"""
        theme = ThemeManager.get_current_theme()
        
        custom_css = f"""
        <style>
            /* =========================================== */
            /* 全局样式 - 科技感设计 */
            /* =========================================== */
            .stApp {{
                background-color: {theme['bg_color']};
                font-family: {theme['font_family']};
            }}
            
            /* 滚动条样式 - 科技感 */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            ::-webkit-scrollbar-track {{
                background: {theme['border_light']};
                border-radius: 4px;
            }}
            ::-webkit-scrollbar-thumb {{
                background: {theme['button_primary']}80;
                border-radius: 4px;
                transition: background 0.2s;
            }}
            ::-webkit-scrollbar-thumb:hover {{
                background: {theme['button_primary']};
            }}
            
            /* =========================================== */
            /* 区块和卡片样式 - 层次感 */
            /* =========================================== */
            .block-container {{
                background-color: {theme['block_bg']};
                border-radius: {theme['border_radius_large']};
                padding: 1.5rem;
                margin-bottom: 1rem;
                border: 1px solid {theme['border']};
                box-shadow: {theme['shadow_small']};
            }}
            
            .card {{
                background-color: {theme['card_bg']};
                border-radius: {theme['border_radius_medium']};
                padding: 1rem;
                border: 1px solid {theme['border']};
                margin-bottom: 0.75rem;
                box-shadow: {theme['shadow_small']};
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .card:hover {{
                transform: translateY(-2px);
                box-shadow: {theme['shadow_medium']};
            }}
            
            /* =========================================== */
            /* 文字颜色 - 清晰对比 */
            /* =========================================== */
            .stMarkdown, .stText, p, li, span, div {{
                color: {theme['text_primary']} !important;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                color: {theme['text_emphasis']} !important;
                font-weight: 600;
                letter-spacing: -0.02em;
            }}
            
            h1 {{
                font-size: 2rem !important;
                margin-bottom: 1rem !important;
                background: linear-gradient(135deg, {theme['text_emphasis']}, {theme['accent_color']});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            h2 {{
                font-size: 1.5rem !important;
                margin-bottom: 0.75rem !important;
                border-left: 4px solid {theme['accent_color']};
                padding-left: 0.75rem;
            }}
            
            h3 {{
                font-size: 1.25rem !important;
                margin-bottom: 0.5rem !important;
            }}
            
            /* 次要文字 */
            .caption, .stCaption, .small-text {{
                color: {theme['text_secondary']} !important;
                font-size: 0.75rem !important;
            }}
            
            /* 禁用文字 */
            .stTextInput > div > div > input:disabled,
            .stSelectbox > div > div > select:disabled {{
                color: {theme['text_disabled']} !important;
            }}
            
            /* =========================================== */
            /* 按钮样式 - 科技感 */
            /* =========================================== */
            .stButton > button {{
                background-color: {theme['button_normal']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                border-radius: {theme['border_radius_small']};
                padding: 0.5rem 1rem;
                font-family: {theme['font_family']};
                font-weight: 500;
                transition: all 0.2s ease;
                cursor: pointer;
                box-shadow: {theme['shadow_small']};
            }}
            
            .stButton > button:hover {{
                background-color: {theme['button_hover']};
                color: {theme['text_emphasis']};
                border-color: {theme['accent_color']};
                transform: translateY(-2px);
                box-shadow: {theme['shadow_medium']};
            }}
            
            .stButton > button:active {{
                transform: translateY(0);
            }}
            
            /* 主要按钮 */
            .stButton > button[kind="primary"],
            .primary-button > button {{
                background: linear-gradient(135deg, {theme['button_primary']}, {theme['button_primary_hover']});
                color: white;
                font-weight: 600;
                border: none;
                box-shadow: 0 4px 12px {theme['button_primary']}40;
            }}
            
            .stButton > button[kind="primary"]:hover,
            .primary-button > button:hover {{
                background: linear-gradient(135deg, {theme['button_primary_hover']}, {theme['button_primary']});
                transform: translateY(-2px);
                box-shadow: 0 6px 16px {theme['button_primary']}60;
            }}
            
            /* 次要按钮 */
            .secondary-button > button {{
                background-color: {theme['button_secondary']};
                color: white;
                border: none;
            }}
            
            .secondary-button > button:hover {{
                background-color: {theme['button_secondary_hover']};
            }}
            
            /* 危险按钮 */
            .stButton > button[kind="danger"],
            .danger-button > button {{
                background-color: {theme['button_danger']};
                color: white;
                border: none;
            }}
            
            .stButton > button[kind="danger"]:hover,
            .danger-button > button:hover {{
                background-color: {theme['button_danger_hover']};
                transform: translateY(-2px);
            }}
            
            /* =========================================== */
            /* 侧边栏样式 */
            /* =========================================== */
            [data-testid="stSidebar"] {{
                background-color: {theme['sidebar_bg']};
                border-right: 1px solid {theme['border']};
                box-shadow: {theme['shadow_medium']};
            }}
            
            [data-testid="stSidebar"] .stMarkdown,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] .stText {{
                color: {theme['text_primary']} !important;
            }}
            
            /* =========================================== */
            /* 输入框样式 - 现代感 */
            /* =========================================== */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > select,
            .stMultiselect > div > div,
            .stNumberInput > div > div > input,
            .stTextArea > div > div > textarea {{
                background-color: {theme['card_bg']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                border-radius: {theme['border_radius_small']};
                padding: 0.5rem 0.75rem;
                font-size: 0.9rem;
                transition: all 0.2s;
            }}
            
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > select:focus,
            .stMultiselect > div > div:focus-within,
            .stNumberInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {{
                border-color: {theme['accent_color']};
                outline: none;
                box-shadow: 0 0 0 3px {theme['accent_color']}40;
            }}
            
            /* 下拉框选项样式 */
            .stSelectbox > div > div > div {{
                background-color: {theme['card_bg']};
                color: {theme['text_primary']};
            }}
            
            /* =========================================== */
            /* 数据表格样式 */
            /* =========================================== */
            .stDataFrame {{
                font-family: {theme['code_font']};
                font-size: 0.85rem;
                border-radius: {theme['border_radius_medium']};
                overflow: hidden;
            }}
            
            .stDataFrame td {{
                color: {theme['text_primary']} !important;
                padding: 0.5rem 0.75rem !important;
                border-bottom: 1px solid {theme['border']};
            }}
            
            .stDataFrame th {{
                color: {theme['text_emphasis']} !important;
                background: linear-gradient(135deg, {theme['block_bg']}, {theme['card_bg']}) !important;
                padding: 0.75rem 0.75rem !important;
                font-weight: 600;
                border-bottom: 2px solid {theme['accent_color']};
            }}
            
            .stDataFrame tbody tr:hover {{
                background-color: {theme['border_light']} !important;
                transition: background 0.2s;
            }}
            
            /* =========================================== */
            /* Metric 卡片样式 - 数据展示 */
            /* =========================================== */
            .stMetric {{
                background: linear-gradient(135deg, {theme['card_bg']}, {theme['block_bg']});
                padding: 1rem;
                border-radius: {theme['border_radius_medium']};
                border: 1px solid {theme['border']};
                margin-bottom: 0.5rem;
                text-align: center;
                transition: all 0.2s ease;
                box-shadow: {theme['shadow_small']};
            }}
            
            .stMetric:hover {{
                transform: translateY(-4px);
                box-shadow: {theme['shadow_medium']};
                border-color: {theme['accent_color']};
            }}
            
            .stMetric label {{
                color: {theme['text_secondary']} !important;
                font-size: 0.75rem !important;
                font-weight: 500 !important;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .stMetric [data-testid="stMetricValue"] {{
                color: {theme['accent_color']} !important;
                font-size: 2rem !important;
                font-weight: 700 !important;
                line-height: 1.2 !important;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .stMetric [data-testid="stMetricDelta"] {{
                color: {theme['text_secondary']} !important;
                font-size: 0.8rem !important;
            }}
            
            /* =========================================== */
            /* 标签页样式 */
            /* =========================================== */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.25rem;
                border-bottom: 2px solid {theme['border']};
                background-color: {theme['block_bg']};
                padding: 0.5rem 0.5rem 0 0.5rem;
                border-radius: {theme['border_radius_medium']} {theme['border_radius_medium']} 0 0;
            }}
            
            .stTabs [data-baseweb="tab"] {{
                background-color: transparent;
                color: {theme['text_secondary']};
                padding: 0.6rem 1.2rem;
                font-weight: 500;
                border-radius: {theme['border_radius_small']} {theme['border_radius_small']} 0 0;
                transition: all 0.2s;
            }}
            
            .stTabs [data-baseweb="tab"]:hover {{
                color: {theme['accent_color']};
                background-color: {theme['border_light']};
            }}
            
            .stTabs [aria-selected="true"] {{
                color: {theme['accent_color']} !important;
                border-bottom: 2px solid {theme['accent_color']};
                background-color: {theme['card_bg']};
            }}
            
            /* =========================================== */
            /* 图例样式 - 确保清晰可见 */
            /* =========================================== */
            .legend, .legends, [data-testid="stLegend"] {{
                background-color: {theme['card_bg']} !important;
                border: 1px solid {theme['border']} !important;
                border-radius: {theme['border_radius_small']} !important;
                padding: 0.5rem !important;
                box-shadow: {theme['shadow_small']} !important;
            }}
            
            .legend text, .legend .legendtext {{
                fill: {theme['text_primary']} !important;
                color: {theme['text_primary']} !important;
            }}
            
            /* =========================================== */
            /* Plotly 图表工具条 */
            /* =========================================== */
            .modebar-container {{
                background: transparent !important;
            }}
            
            .modebar {{
                background-color: {theme['card_bg']} !important;
                border-radius: {theme['border_radius_small']} !important;
                border: 1px solid {theme['border']} !important;
                padding: 4px !important;
                box-shadow: {theme['shadow_small']} !important;
            }}
            
            .modebar-btn {{
                color: {theme['text_primary']} !important;
            }}
            
            .modebar-btn:hover {{
                background-color: {theme['accent_color']}20 !important;
            }}
            
            /* =========================================== */
            /* 主内容区域边距 - 确保工具条完整显示 */
            /* =========================================== */
            .main .block-container {{
                padding: 1rem 2rem 2rem 2rem !important;
                max-width: 100% !important;
            }}
            
            .stPlotlyChart {{
                overflow: visible !important;
            }}
            
            .modebar-container {{
                right: 10px !important;
                top: 10px !important;
                z-index: 100 !important;
            }}
            
            .element-container:has(.stPlotlyChart) {{
                overflow-x: auto !important;
            }}
            
            /* =========================================== */
            /* 侧边栏折叠按钮 */
            /* =========================================== */
            [data-testid="stSidebarCollapsedControl"] {{
                position: relative;
                cursor: pointer;
            }}
            
            [data-testid="stSidebarCollapsedControl"]:hover {{
                opacity: 0.8;
            }}
            
            [data-testid="stSidebarCollapsedControl"]::after {{
                content: "◀";
                position: absolute;
                left: 30px;
                top: 50%;
                transform: translateY(-50%);
                color: {theme['text_primary']};
                font-size: 14px;
                opacity: 0.7;
            }}
            
            /* =========================================== */
            /* 分割线样式 */
            /* =========================================== */
            hr {{
                border-color: {theme['border']};
                margin: 1rem 0;
                background: linear-gradient(90deg, transparent, {theme['accent_color']}, transparent);
                height: 1px;
                border: none;
            }}
            
            /* =========================================== */
            /* 展开/折叠样式 */
            /* =========================================== */
            .streamlit-expanderHeader {{
                background-color: {theme['block_bg']};
                color: {theme['text_primary']};
                border-radius: {theme['border_radius_small']};
                font-weight: 500;
                transition: all 0.2s;
            }}
            
            .streamlit-expanderHeader:hover {{
                color: {theme['accent_color']};
                background-color: {theme['border_light']};
            }}
            
            /* =========================================== */
            /* 通知/公告样式 */
            /* =========================================== */
            .announcement-info {{
                background: linear-gradient(135deg, {theme['info_color']}20, {theme['info_color']}10);
                border-left: 4px solid {theme['info_color']};
                padding: 1rem;
                border-radius: {theme['border_radius_small']};
                margin-bottom: 1rem;
                color: {theme['text_primary']};
            }}
            
            .announcement-warning {{
                background: linear-gradient(135deg, {theme['warning_color']}20, {theme['warning_color']}10);
                border-left: 4px solid {theme['warning_color']};
                padding: 1rem;
                border-radius: {theme['border_radius_small']};
                margin-bottom: 1rem;
                color: {theme['text_primary']};
            }}
            
            .announcement-success {{
                background: linear-gradient(135deg, {theme['success_color']}20, {theme['success_color']}10);
                border-left: 4px solid {theme['success_color']};
                padding: 1rem;
                border-radius: {theme['border_radius_small']};
                margin-bottom: 1rem;
                color: {theme['text_primary']};
            }}
            
            /* =========================================== */
            /* 底部样式 */
            /* =========================================== */
            .footer {{
                text-align: center;
                padding: 2rem;
                color: {theme['text_secondary']};
                border-top: 1px solid {theme['border']};
                margin-top: 2rem;
                font-size: 0.8rem;
            }}
            
            .footer a {{
                color: {theme['accent_color']};
                text-decoration: none;
                margin: 0 0.5rem;
                transition: color 0.2s;
            }}
            
            .footer a:hover {{
                color: {theme['button_primary_hover']};
                text-decoration: underline;
            }}
            
            /* =========================================== */
            /* 代码块样式 */
            /* =========================================== */
            code, pre {{
                font-family: {theme['code_font']};
                background-color: {theme['block_bg']};
                border: 1px solid {theme['border']};
                border-radius: {theme['border_radius_small']};
                padding: 0.2rem 0.4rem;
                font-size: 0.85rem;
            }}
            
            /* =========================================== */
            /* 加载进度条 */
            /* =========================================== */
            .stProgress > div > div {{
                background: linear-gradient(90deg, {theme['accent_color']}, {theme['button_primary_hover']});
                border-radius: 4px;
            }}
            /* =========================================== */
            /* 增强折叠按钮可见性 */
            /* =========================================== */
            [data-testid="stSidebarCollapsedControl"] {{
                background-color: {theme['accent_color']} !important;
                border-radius: 0 8px 8px 0 !important;
                padding: 8px 4px !important;
                opacity: 0.8 !important;
                transition: all 0.2s ease;
            }}
            
            [data-testid="stSidebarCollapsedControl"]:hover {{
                opacity: 1 !important;
                transform: scale(1.05);
                background-color: {theme['button_primary_hover']} !important;
            }}
            /* 去除顶部留白 */
            .stApp > header {{
                display: none !important;
            }}

            /* 调整主容器位置，填补顶部空白 */
            .main .block-container {{
                padding-top: 0.5rem !important;
                padding-bottom: 2rem !important;
            }}

            /* 如果有公告区域，调整其位置 */
            .announcement-info, .announcement-warning, .announcement-success {{
                margin-top: 0.5rem !important;
            }}
            /* =========================================== */
            /* 欢迎页面提示区域样式 */
            /* =========================================== */
            #upload-hint {{
                transition: all 0.3s ease;
                cursor: pointer;
            }}

            #upload-hint:hover {{
                transform: translateY(-4px);
                box-shadow: 0 8px 24px {theme['accent_color']}4D;
                border-color: {theme['accent_color']} !important;
            }}

            /* =========================================== */
            /* 增强折叠按钮可见性 */
            /* =========================================== */
            [data-testid="stSidebarCollapsedControl"] {{
                background-color: {theme['accent_color']} !important;
                border-radius: 0 8px 8px 0 !important;
                padding: 8px 4px !important;
                opacity: 0.8 !important;
                transition: all 0.2s ease;
            }}

            [data-testid="stSidebarCollapsedControl"]:hover {{
                opacity: 1 !important;
                transform: scale(1.05);
                background-color: {theme['button_primary_hover']} !important;
            }}
            /* =========================================== */
            /* 下拉框样式修复 - 深色主题适配 */
            /* =========================================== */
            /* 下拉框输入框 */
            .stSelectbox > div > div > select {{
                background-color: {theme['card_bg']} !important;
                color: {theme['text_primary']} !important;
                border: 1px solid {theme['border']} !important;
                border-radius: {theme['border_radius_small']} !important;
                padding: 0.5rem 0.75rem !important;
                font-size: 0.9rem !important;
            }}

            .stSelectbox > div > div > select:focus {{
                border-color: {theme['accent_color']} !important;
                outline: none !important;
                box-shadow: 0 0 0 2px {theme['accent_color']}40 !important;
            }}

            /* 下拉选项面板容器 */
            .stSelectbox [data-baseweb="popover"] {{
                background-color: {theme['card_bg']} !important;
                border: 1px solid {theme['border']} !important;
                border-radius: {theme['border_radius_small']} !important;
                box-shadow: {theme['shadow_medium']} !important;
            }}

            /* 下拉选项菜单 */
            .stSelectbox [data-baseweb="menu"] {{
                background-color: {theme['card_bg']} !important;
                border-radius: {theme['border_radius_small']} !important;
                padding: 4px 0 !important;
            }}

            /* 下拉选项项 */
            .stSelectbox [data-baseweb="menu"] [role="option"] {{
                background-color: {theme['card_bg']} !important;
                color: {theme['text_primary']} !important;
                padding: 0.5rem 1rem !important;
                font-size: 0.9rem !important;
                transition: all 0.15s ease !important;
                cursor: pointer !important;
            }}

            /* 下拉选项悬停效果 */
            .stSelectbox [data-baseweb="menu"] [role="option"]:hover {{
                background-color: {theme['border_light']} !important;
                color: {theme['text_emphasis']} !important;
            }}

            /* 下拉选项选中状态 */
            .stSelectbox [data-baseweb="menu"] [role="option"][aria-selected="true"] {{
                background-color: {theme['accent_color']} !important;
                color: white !important;
            }}

            /* 下拉选项高亮状态（键盘导航） */
            .stSelectbox [data-baseweb="menu"] [role="option"][aria-selected="false"][data-highlighted="true"] {{
                background-color: {theme['accent_color']}40 !important;
                color: {theme['text_emphasis']} !important;
            }}
            /* =========================================== */
            /* 多选下拉框样式修复 - 深色主题适配 */
            /* =========================================== */
            /* 多选下拉框容器 */
            .stMultiSelect [data-baseweb="select"] > div {{
                background-color: {theme['card_bg']} !important;
                border: 1px solid {theme['border']} !important;
                border-radius: {theme['border_radius_small']} !important;
            }}

            /* 多选下拉框输入区域 */
            .stMultiSelect [data-baseweb="select"] input {{
                color: {theme['text_primary']} !important;
            }}

            /* 多选下拉框已选标签 */
            .stMultiSelect [data-baseweb="tag"] {{
                background-color: {theme['accent_color']} !important;
                color: white !important;
                border-radius: 4px !important;
                padding: 2px 8px !important;
            }}

            /* 多选下拉框已选标签关闭按钮 */
            .stMultiSelect [data-baseweb="tag"] svg {{
                fill: white !important;
            }}

            /* 多选下拉框选项面板 */
            .stMultiSelect [data-baseweb="popover"] {{
                background-color: {theme['card_bg']} !important;
                border: 1px solid {theme['border']} !important;
                border-radius: {theme['border_radius_small']} !important;
                box-shadow: {theme['shadow_medium']} !important;
            }}

            /* 多选下拉框选项菜单 */
            .stMultiSelect [data-baseweb="menu"] {{
                background-color: {theme['card_bg']} !important;
            }}

            /* 多选下拉框选项 */
            .stMultiSelect [data-baseweb="menu"] [role="option"] {{
                background-color: {theme['card_bg']} !important;
                color: {theme['text_primary']} !important;
                padding: 0.5rem 1rem !important;
            }}

            /* 多选下拉框选项悬停 */
            .stMultiSelect [data-baseweb="menu"] [role="option"]:hover {{
                background-color: {theme['border_light']} !important;
            }}

            /* 多选下拉框选项选中 */
            .stMultiSelect [data-baseweb="menu"] [role="option"][aria-selected="true"] {{
                background-color: {theme['accent_color']}40 !important;
                color: {theme['text_emphasis']} !important;
            }}
            /* =========================================== */
            /* 修复下拉菜单背景和文字颜色 - 最高优先级 */
            /* =========================================== */
            /* 下拉菜单容器 */
            div[data-testid="stSelectbox"] [data-baseweb="popover"],
            div[data-testid="stSelectbox"] [data-baseweb="menu"],
            div[data-testid="stSelectbox"] ul,
            div[data-testid="stSelectbox"] [role="listbox"] {{
                background-color: {theme['card_bg']} !important;
                border: 1px solid {theme['border']} !important;
            }}

            /* 下拉菜单选项 */
            div[data-testid="stSelectbox"] [role="option"],
            div[data-testid="stSelectbox"] li {{
                background-color: {theme['card_bg']} !important;
                color: {theme['text_primary']} !important;
            }}

            /* 下拉菜单选项悬停 */
            div[data-testid="stSelectbox"] [role="option"]:hover,
            div[data-testid="stSelectbox"] li:hover {{
                background-color: {theme['border_light']} !important;
                color: {theme['text_emphasis']} !important;
            }}

            /* 下拉菜单选中状态 */
            div[data-testid="stSelectbox"] [role="option"][aria-selected="true"],
            div[data-testid="stSelectbox"] li[aria-selected="true"] {{
                background-color: {theme['accent_color']} !important;
                color: white !important;
            }}

            /* 覆盖默认类名 */
            .st-emotion-cache-sy3zga {{
                background-color: {theme['card_bg']} !important;
                color: {theme['text_primary']} !important;
                border-color: {theme['border']} !important;
            }}
            .stDataFrame {{
                transition: none !important;
            }}


           /* =========================================== */
            /* 下拉菜单样式 - 简化版，避免背景叠加 */
            /* =========================================== */

            /* 1. 下拉菜单容器 - 只设置边框和阴影，背景由内部决定 */
            ul[data-testid*="stVirtualDropdown"] {{
                background-color: {theme['card_bg']} !important;
                border: 1px solid {theme['border']} !important;
                border-radius: {theme['border_radius_small']} !important;
                box-shadow: {theme['shadow_medium']} !important;
                padding: 4px 0 !important;
                margin: 0 !important;
                list-style: none !important;
                max-height: 300px !important;
                overflow-y: auto !important;
            }}

            /* 2. 下拉菜单选项 - 统一背景和文字颜色 */
            ul[data-testid*="stVirtualDropdown"] li {{
                background-color: {theme['card_bg']} !important;
                color: {theme['text_primary']} !important;
                padding: 8px 12px !important;
                font-size: 0.9rem !important;
                cursor: pointer !important;
                border-bottom: 1px solid {theme['border_light']} !important;
                list-style: none !important;
            }}

            /* 3. 最后一个选项去掉边框 */
            ul[data-testid*="stVirtualDropdown"] li:last-child {{
                border-bottom: none !important;
            }}

            /* 4. 选项悬停 - 使用半透明背景 */
            ul[data-testid*="stVirtualDropdown"] li:hover {{
                background-color: {theme['accent_color']}30 !important;
                color: {theme['text_emphasis']} !important;
            }}

            /* 5. 选项选中 - 使用实色背景，白色文字 */
            ul[data-testid*="stVirtualDropdown"] li[aria-selected="true"] {{
                background-color: {theme['accent_color']} !important;
                color: white !important;
            }}

            /* 6. 高亮状态（键盘导航） */
            ul[data-testid*="stVirtualDropdown"] li[data-highlighted="true"] {{
                background-color: {theme['accent_color']}50 !important;
                color: {theme['text_emphasis']} !important;
            }}

            /* 7. 移除可能的外层紫色背景 */
            div[data-testid="stSelectbox"] [data-baseweb="popover"],
            div[data-testid="stSelectbox"] [data-baseweb="menu"] {{
                background-color: transparent !important;
                background: none !important;
            }}

            /* 8. 覆盖可能的默认类名，防止叠加 */
            .st-emotion-cache-sy3zga,
            .st-emotion-cache-1wbqy5l,
            .st-emotion-cache-1l2pt3c,
            .st-emotion-cache-1p5n6z1 {{
                background-color: transparent !important;
                background: none !important;
            }}

            /* 9. 滚动条样式 */
            ul[data-testid*="stVirtualDropdown"]::-webkit-scrollbar {{
                width: 6px !important;
            }}

            ul[data-testid*="stVirtualDropdown"]::-webkit-scrollbar-track {{
                background: {theme['border_light']} !important;
                border-radius: 3px !important;
            }}

            ul[data-testid*="stVirtualDropdown"]::-webkit-scrollbar-thumb {{
                background: {theme['accent_color']} !important;
                border-radius: 3px !important;
            }}

            ul[data-testid*="stVirtualDropdown"]::-webkit-scrollbar-thumb:hover {{
                background: {theme['button_primary_hover']} !important;
            }}
            /* 防止布局抖动 */
            .main .block-container {{
                transition: none !important;
                width: 100% !important;
            }}

            [data-testid="stSidebar"] {{
                transition: width 0.2s ease !important;
            }}

            .stDataFrame {{
                width: 100% !important;
                table-layout: fixed !important;
            }}
        </style>
        """
        
        st.markdown(custom_css, unsafe_allow_html=True)