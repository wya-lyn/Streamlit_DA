"""
主题管理模块：处理深色/浅色主题切换
"""

import streamlit as st

class ThemeManager:
    """主题管理器，控制全局配色方案"""
    
    # 深色主题配色
    DARK_THEME = {
        "bg_color": "#0A0A0A",  # 纯黑背景
        "block_bg": "#1E1E1E",  # 区块背景
        "card_bg": "#2D2D2D",   # 卡片背景
        "text_primary": "#E0E0E0",  # 主文字
        "text_emphasis": "#FFFFFF",  # 强调文字
        "border": "#3D3D3D",     # 边框/分割线
        "button_normal": "#3D3D3D",  # 普通按钮
        "button_hover": "#4D4D4D",   # 按钮悬停
        "button_primary": "#6A4E9B", # 主要按钮(神秘紫)
        "button_danger": "#8B3A3A",  # 危险操作(暗红)
        "menu_bg": "#151515",        # 菜单背景
        "menu_selected": "#6A4E9B",  # 菜单选中
        "icon_color": "#B0B0B0",     # 图标色
        "ai_color": "#4A6A8B",       # AI功能(科技蓝)
        "font_family": """
            '微软雅黑', 'Microsoft YaHei', 
            -apple-system, BlinkMacSystemFont, 
            sans-serif
        """,
        "code_font": "Consolas, 'Courier New', monospace"
    }
    
    # 浅色主题配色
    LIGHT_THEME = {
        "bg_color": "#F5F5F5",      # 浅灰背景
        "block_bg": "#FFFFFF",       # 区块背景(白)
        "card_bg": "#FAFAFA",        # 卡片背景
        "text_primary": "yellow",   # 主文字(黄色)
        "text_emphasis": "#000000",  # 强调文字(黑)
        "border": "#E0E0E0",         # 边框/分割线
        "button_normal": "#E0E0E0",  # 普通按钮
        "button_hover": "#D0D0D0",   # 按钮悬停
        "button_primary": "#8A6EBB", # 主要按钮(浅紫)
        "button_danger": "#B55A5A",  # 危险操作(浅红)
        "menu_bg": "#EEEEEE",        # 菜单背景
        "menu_selected": "#8A6EBB",  # 菜单选中
        "icon_color": "#666666",     # 图标色
        "ai_color": "#5A7A9B",       # AI功能(科技蓝)
        "font_family": DARK_THEME["font_family"],
        "code_font": DARK_THEME["code_font"]
    }
    
    @staticmethod
    def init_theme():
        """初始化主题设置"""
        if 'theme_mode' not in st.session_state:
            st.session_state.theme_mode = 'dark'  # 默认深色
    
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
            /* 全局样式 */
            .stApp {{
                background-color: {theme['bg_color']};
                font-family: {theme['font_family']};
            }}
            
            /* 区块样式 */
            .block-container {{
                background-color: {theme['block_bg']};
                border-radius: 8px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                border: 1px solid {theme['border']};
            }}
            
            /* 卡片样式 */
            .card {{
                background-color: {theme['card_bg']};
                border-radius: 8px;
                padding: 1rem;
                border: 1px solid {theme['border']};
                margin-bottom: 0.5rem;
            }}
            
            /* 文字颜色 */
            .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {{
                color: {theme['text_primary']} !important;
            }}
            
            h1, h2, h3 {{
                color: {theme['text_emphasis']} !important;
                font-weight: bold;
            }}
            
            /* 按钮样式 */
            .stButton > button {{
                background-color: {theme['button_normal']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                padding: 0.5rem 1rem;
                font-family: {theme['font_family']};
            }}
            
            .stButton > button:hover {{
                background-color: {theme['button_hover']};
                color: {theme['text_emphasis']};
                border-color: {theme['button_primary']};
            }}
            
            /* 主要按钮 */
            .primary-button > button {{
                background-color: {theme['button_primary']};
                color: white;
                font-weight: bold;
            }}
            
            .primary-button > button:hover {{
                background-color: {theme['button_primary']}dd;
            }}
            
            /* 危险按钮 */
            .danger-button > button {{
                background-color: {theme['button_danger']};
                color: white;
            }}
            
            /* AI功能按钮 */
            .ai-button > button {{
                background-color: {theme['ai_color']};
                color: white;
            }}
            
            /* 菜单样式 */
            .sidebar .sidebar-content {{
                background-color: {theme['menu_bg']};
            }}
            
            /* 选中菜单项 */
            .menu-item-selected {{
                background-color: {theme['menu_selected']};
                color: white;
                padding: 0.5rem;
                border-radius: 4px;
            }}
            
            /* 图标颜色 */
            .stIcon {{
                color: {theme['icon_color']};
            }}
            
            /* 代码/数据样式 */
            .stDataFrame, .stTable {{
                font-family: {theme['code_font']};
            }}
            
            code, pre {{
                font-family: {theme['code_font']};
                background-color: {theme['block_bg']};
                border: 1px solid {theme['border']};
            }}
            
            /* 分割线 */
            hr {{
                border-color: {theme['border']};
            }}
            
            /* 输入框样式 */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > select,
            .stMultiselect > div > div {{
                background-color: {theme['card_bg']};
                color: {theme['text_primary']};
                border-color: {theme['border']};
            }}
            
            /* 滑块样式 */
            .stSlider > div > div {{
                color: {theme['button_primary']};
            }}
            
            /* 开关样式 */
            .stCheckbox {{
                color: {theme['text_primary']};
            }}
            
            /* 通知/公告样式 */
            .announcement-info {{
                background-color: {theme['ai_color']}20;
                border-left: 4px solid {theme['ai_color']};
                padding: 1rem;
                border-radius: 4px;
                margin-bottom: 1rem;
                color: {theme['text_primary']};
            }}
            
            .announcement-warning {{
                background-color: {theme['button_danger']}20;
                border-left: 4px solid {theme['button_danger']};
                padding: 1rem;
                border-radius: 4px;
                margin-bottom: 1rem;
            }}
            
            .announcement-success {{
                background-color: #2A5A3A20;
                border-left: 4px solid #2A5A3A;
                padding: 1rem;
                border-radius: 4px;
                margin-bottom: 1rem;
            }}
            
            /* 底部样式 */
            .footer {{
                text-align: center;
                padding: 2rem;
                color: {theme['text_primary']};
                border-top: 1px solid {theme['border']};
                margin-top: 2rem;
                font-size: 0.9rem;
            }}
            
            .footer a {{
                color: {theme['button_primary']};
                text-decoration: none;
                margin: 0 0.5rem;
            }}
            
            .footer a:hover {{
                text-decoration: underline;
            }}
            
            /* 加载进度 */
            .stProgress > div > div {{
                background-color: {theme['button_primary']};
            }}
            
            /* 可折叠菜单 */
            .collapsible {{
                background-color: {theme['menu_bg']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                margin-bottom: 0.5rem;
            }}
            
            .collapsible-header {{
                padding: 0.75rem;
                cursor: pointer;
                color: {theme['text_primary']};
                font-weight: bold;
            }}
            
            .collapsible-content {{
                padding: 1rem;
                background-color: {theme['block_bg']};
            }}
            
            /* ===== 新增：Metric 数字颜色修复 ===== */
            /* Metric 容器样式 */
            .stMetric {{
                background-color: {theme['card_bg']};
                padding: 1rem;
                border-radius: 8px;
                border: 1px solid {theme['border']};
                margin-bottom: 0.5rem;
            }}
            
            /* Metric 标签 */
            .stMetric label {{
                color: {theme['text_primary']} !important;
                font-size: 0.9rem !important;
            }}
            
            /* Metric 数值 - 亮橙色 */
            .stMetric [data-testid="stMetricValue"] {{
                color: #FFA500 !important;
                font-size: 2rem !important;
                font-weight: bold !important;
            }}
            
            /* Metric 增量/变化值 */
            .stMetric [data-testid="stMetricDelta"] {{
                color: {theme['text_primary']} !important;
            }}
            
            /* 备用选择器（确保覆盖） */
            [data-testid="stMetricValue"] {{
                color: #FFA500 !important;
                font-size: 2rem !important;
                font-weight: bold !important;
            }}
            
            [data-testid="stMetricLabel"] {{
                color: {theme['text_primary']} !important;
                font-size: 0.9rem !important;
            }}
            
            /* Metric 容器 */
            [data-testid="metric-container"] {{
                background-color: {theme['card_bg']};
                padding: 1rem;
                border-radius: 8px;
                border: 1px solid {theme['border']};
            }}
            
            /* 鼠标悬停效果 */
            [data-testid="metric-container"]:hover [data-testid="stMetricValue"] {{
                color: #FF8C00 !important;
            }}
            
            /* 确保其他数字也清晰可见 */
            .stDataFrame td {{
                color: {theme['text_primary']} !important;
            }}
            
            .stDataFrame th {{
                color: {theme['text_emphasis']} !important;
                background-color: {theme['block_bg']} !important;
            }}
            
            /* 统计信息中的数字 */
            .stMarkdown p strong {{
                color: #FFA500 !important;
            }}
        </style>
        """
        
        st.markdown(custom_css, unsafe_allow_html=True)
        