"""
主题管理模块：处理深色/浅色主题切换
"""

import streamlit as st

class ThemeManager:
    """主题管理器，控制全局配色方案"""
    
    # 深色主题配色
    DARK_THEME = {
        # 背景色系
        "bg_color": "#0A0A0A",           # 主背景 - 纯黑
        "block_bg": "#1E1E1E",            # 区块背景 - 深灰
        "card_bg": "#2D2D2D",             # 卡片背景 - 中灰
        "sidebar_bg": "#151515",          # 侧边栏背景
        
        # 文字色系
        "text_primary": "#E0E0E0",        # 主要文字 - 浅灰
        "text_secondary": "#A0A0A0",      # 次要文字 - 中灰
        "text_emphasis": "#FFFFFF",       # 强调文字 - 纯白
        
        # 边框色系
        "border": "#3D3D3D",              # 边框/分割线
        "border_light": "#2A2A2A",        # 浅色边框
        
        # 按钮色系
        "button_normal": "#3D3D3D",       # 普通按钮
        "button_hover": "#4D4D4D",        # 按钮悬停
        "button_primary": "#6A4E9B",      # 主要按钮 - 紫色
        "button_primary_hover": "#7B5EAC", # 主要按钮悬停
        "button_danger": "#8B3A3A",       # 危险按钮 - 暗红
        "button_danger_hover": "#9B4A4A", # 危险按钮悬停
        
        # 菜单色系
        "menu_bg": "#151515",             # 菜单背景
        "menu_hover": "#2D2D2D",          # 菜单悬停
        "menu_selected": "#6A4E9B",       # 菜单选中
        
        # 特殊色系
        "ai_color": "#4A6A8B",            # AI功能 - 科技蓝
        "success_color": "#2A5A3A",       # 成功提示 - 墨绿
        "warning_color": "#8B6B2A",       # 警告提示 - 暗黄
        "info_color": "#2A5A6B",          # 信息提示 - 深蓝
        
        # 字体设置
        "font_family": """
            '微软雅黑', 'Microsoft YaHei', 
            -apple-system, BlinkMacSystemFont, 
            'Segoe UI', Roboto, sans-serif
        """,
        "code_font": "Consolas, 'Courier New', monospace",
        
        # 圆角大小
        "border_radius_small": "4px",
        "border_radius_medium": "8px",
        "border_radius_large": "12px",
    }
    
    # 浅色主题配色
    LIGHT_THEME = {
        # 背景色系
        "bg_color": "#F8F9FA",            # 主背景 - 浅灰白
        "block_bg": "#FFFFFF",            # 区块背景 - 纯白
        "card_bg": "#FFFFFF",             # 卡片背景 - 纯白
        "sidebar_bg": "#F0F2F6",          # 侧边栏背景 - 浅灰
        
        # 文字色系
        "text_primary": "#2C3E50",        # 主要文字 - 深蓝灰
        "text_secondary": "#6C757D",      # 次要文字 - 中灰
        "text_emphasis": "#1A2634",       # 强调文字 - 深灰黑
        
        # 边框色系
        "border": "#E9ECEF",              # 边框/分割线 - 浅灰
        "border_light": "#F1F3F5",        # 浅色边框
        
        # 按钮色系
        "button_normal": "#F0F2F6",       # 普通按钮 - 浅灰
        "button_hover": "#E9ECEF",        # 按钮悬停 - 更浅灰
        "button_primary": "#6A4E9B",      # 主要按钮 - 紫色
        "button_primary_hover": "#7B5EAC", # 主要按钮悬停
        "button_danger": "#DC3545",       # 危险按钮 - 红色
        "button_danger_hover": "#C82333", # 危险按钮悬停
        
        # 菜单色系
        "menu_bg": "#F0F2F6",             # 菜单背景 - 浅灰
        "menu_hover": "#E9ECEF",          # 菜单悬停 - 更浅灰
        "menu_selected": "#6A4E9B",       # 菜单选中 - 紫色
        
        # 特殊色系
        "ai_color": "#5A7A9B",            # AI功能 - 科技蓝
        "success_color": "#28A745",       # 成功提示 - 绿色
        "warning_color": "#FFC107",       # 警告提示 - 黄色
        "info_color": "#17A2B8",          # 信息提示 - 青色
        
        # 字体设置
        "font_family": DARK_THEME["font_family"],
        "code_font": DARK_THEME["code_font"],
        
        # 圆角大小
        "border_radius_small": "4px",
        "border_radius_medium": "8px",
        "border_radius_large": "12px",
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
            /* 全局样式 */
            /* =========================================== */
            .stApp {{
                background-color: {theme['bg_color']};
                font-family: {theme['font_family']};
            }}
            
            /* 滚动条样式 */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            ::-webkit-scrollbar-track {{
                background: {theme['border_light']};
                border-radius: 4px;
            }}
            ::-webkit-scrollbar-thumb {{
                background: {theme['border']};
                border-radius: 4px;
            }}
            ::-webkit-scrollbar-thumb:hover {{
                background: {theme['button_primary']};
            }}
            
            /* =========================================== */
            /* 区块和卡片样式 */
            /* =========================================== */
            .block-container {{
                background-color: {theme['block_bg']};
                border-radius: {theme['border_radius_medium']};
                padding: 1.5rem;
                margin-bottom: 1rem;
                border: 1px solid {theme['border']};
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }}
            
            .card {{
                background-color: {theme['card_bg']};
                border-radius: {theme['border_radius_medium']};
                padding: 1rem;
                border: 1px solid {theme['border']};
                margin-bottom: 0.5rem;
                box-shadow: 0 1px 2px rgba(0,0,0,0.03);
            }}
            
            /* =========================================== */
            /* 文字颜色 */
            /* =========================================== */
            .stMarkdown, .stText, p, li, span {{
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
            }}
            h2 {{
                font-size: 1.5rem !important;
                margin-bottom: 0.75rem !important;
            }}
            h3 {{
                font-size: 1.25rem !important;
                margin-bottom: 0.5rem !important;
            }}
            
            /* 次要文字 */
            .caption, .stCaption {{
                color: {theme['text_secondary']} !important;
                font-size: 0.8rem !important;
            }}
            
            /* =========================================== */
            /* 按钮样式 */
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
            }}
            
            .stButton > button:hover {{
                background-color: {theme['button_hover']};
                color: {theme['text_emphasis']};
                border-color: {theme['button_primary']};
                transform: translateY(-1px);
            }}
            
            .stButton > button:active {{
                transform: translateY(0);
            }}
            
            /* 主要按钮样式 */
            .stButton > button[kind="primary"],
            .primary-button > button {{
                background-color: {theme['button_primary']};
                color: white;
                font-weight: 600;
                border: none;
            }}
            
            .stButton > button[kind="primary"]:hover,
            .primary-button > button:hover {{
                background-color: {theme['button_primary_hover']};
                color: white;
                transform: translateY(-1px);
            }}
            
            /* 危险按钮样式 */
            .stButton > button[kind="danger"],
            .danger-button > button {{
                background-color: {theme['button_danger']};
                color: white;
                border: none;
            }}
            
            .stButton > button[kind="danger"]:hover,
            .danger-button > button:hover {{
                background-color: {theme['button_danger_hover']};
                color: white;
            }}
            
            /* =========================================== */
            /* 侧边栏样式 */
            /* =========================================== */
            [data-testid="stSidebar"] {{
                background-color: {theme['sidebar_bg']};
                border-right: 1px solid {theme['border']};
            }}
            
            [data-testid="stSidebar"] .stMarkdown,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] .stText {{
                color: {theme['text_primary']} !important;
            }}
            
            /* =========================================== */
            /* 输入框样式 */
            /* =========================================== */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > select,
            .stMultiselect > div > div,
            .stNumberInput > div > div > input {{
                background-color: {theme['card_bg']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                border-radius: {theme['border_radius_small']};
                padding: 0.5rem 0.75rem;
                font-size: 0.9rem;
            }}
            
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > select:focus {{
                border-color: {theme['button_primary']};
                outline: none;
                box-shadow: 0 0 0 2px {theme['button_primary']}40;
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
            }}
            
            .stDataFrame td {{
                color: {theme['text_primary']} !important;
                padding: 0.4rem 0.6rem !important;
            }}
            
            .stDataFrame th {{
                color: {theme['text_emphasis']} !important;
                background-color: {theme['block_bg']} !important;
                padding: 0.6rem 0.8rem !important;
                font-weight: 600;
                border-bottom: 2px solid {theme['border']};
            }}
            
            /* 表格悬停效果 */
            .stDataFrame tbody tr:hover {{
                background-color: {theme['border_light']} !important;
            }}
            
            /* =========================================== */
            /* Metric 卡片样式 */
            /* =========================================== */
            .stMetric {{
                background-color: {theme['card_bg']};
                padding: 1rem;
                border-radius: {theme['border_radius_medium']};
                border: 1px solid {theme['border']};
                margin-bottom: 0.5rem;
                text-align: center;
                transition: all 0.2s ease;
            }}
            
            .stMetric:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            
            .stMetric label {{
                color: {theme['text_secondary']} !important;
                font-size: 0.85rem !important;
                font-weight: 500 !important;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .stMetric [data-testid="stMetricValue"] {{
                color: {theme['button_primary']} !important;
                font-size: 2rem !important;
                font-weight: 700 !important;
                line-height: 1.2 !important;
            }}
            
            .stMetric [data-testid="stMetricDelta"] {{
                color: {theme['text_secondary']} !important;
                font-size: 0.8rem !important;
            }}
            
            [data-testid="stMetricValue"] {{
                color: {theme['button_primary']} !important;
                font-size: 2rem !important;
                font-weight: 700 !important;
            }}
            
            [data-testid="stMetricLabel"] {{
                color: {theme['text_secondary']} !important;
                font-size: 0.85rem !important;
            }}
            
            [data-testid="metric-container"] {{
                background-color: {theme['card_bg']};
                padding: 1rem;
                border-radius: {theme['border_radius_medium']};
                border: 1px solid {theme['border']};
            }}
            
            /* =========================================== */
            /* 标签页样式 */
            /* =========================================== */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.5rem;
                border-bottom: 2px solid {theme['border']};
            }}
            
            .stTabs [data-baseweb="tab"] {{
                background-color: transparent;
                color: {theme['text_secondary']};
                padding: 0.5rem 1rem;
                font-weight: 500;
                border-radius: {theme['border_radius_small']} {theme['border_radius_small']} 0 0;
            }}
            
            .stTabs [data-baseweb="tab"]:hover {{
                color: {theme['button_primary']};
                background-color: {theme['border_light']};
            }}
            
            .stTabs [aria-selected="true"] {{
                color: {theme['button_primary']} !important;
                border-bottom: 2px solid {theme['button_primary']};
            }}
            
            /* =========================================== */
            /* 分割线样式 */
            /* =========================================== */
            hr {{
                border-color: {theme['border']};
                margin: 1rem 0;
            }}
            
            /* =========================================== */
            /* 展开/折叠样式 */
            /* =========================================== */
            .streamlit-expanderHeader {{
                background-color: {theme['block_bg']};
                color: {theme['text_primary']};
                border-radius: {theme['border_radius_small']};
                font-weight: 500;
            }}
            
            .streamlit-expanderHeader:hover {{
                color: {theme['button_primary']};
            }}
            
            /* =========================================== */
            /* 滑块样式 */
            /* =========================================== */
            .stSlider > div > div {{
                color: {theme['button_primary']};
            }}
            
            /* =========================================== */
            /* 复选框样式 */
            /* =========================================== */
            .stCheckbox {{
                color: {theme['text_primary']};
            }}
            
            .stCheckbox label {{
                color: {theme['text_primary']} !important;
            }}
            
            /* =========================================== */
            /* 通知/公告样式 */
            /* =========================================== */
            .announcement-info {{
                background-color: {theme['info_color']}20;
                border-left: 4px solid {theme['info_color']};
                padding: 1rem;
                border-radius: {theme['border_radius_small']};
                margin-bottom: 1rem;
                color: {theme['text_primary']};
            }}
            
            .announcement-warning {{
                background-color: {theme['warning_color']}20;
                border-left: 4px solid {theme['warning_color']};
                padding: 1rem;
                border-radius: {theme['border_radius_small']};
                margin-bottom: 1rem;
                color: {theme['text_primary']};
            }}
            
            .announcement-success {{
                background-color: {theme['success_color']}20;
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
                font-size: 0.85rem;
            }}
            
            .footer a {{
                color: {theme['button_primary']};
                text-decoration: none;
                margin: 0 0.5rem;
            }}
            
            .footer a:hover {{
                text-decoration: underline;
            }}
            
            /* =========================================== */
            /* 加载进度条样式 */
            /* =========================================== */
            .stProgress > div > div {{
                background-color: {theme['button_primary']};
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
            /* 错误/警告/成功消息样式 */
            /* =========================================== */
            .stAlert {{
                border-radius: {theme['border_radius_small']};
            }}
        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)