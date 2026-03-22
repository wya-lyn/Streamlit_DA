"""
主题管理模块：处理深色/浅色主题切换
"""

import streamlit as st


class ThemeManager:
    """主题管理器，控制全局配色方案"""

    DARK_THEME = {
        "bg_color": "#0A0C10",
        "block_bg": "#13161C",
        "card_bg": "#1A1F2A",
        "sidebar_bg": "#0C0F14",
        "text_primary": "#E8EDFF",
        "text_secondary": "#9AA7C0",
        "text_emphasis": "#FFFFFF",
        "border": "#2A2F3A",
        "border_light": "#20242E",
        "button_normal": "#2A2F3A",
        "button_hover": "#3A4050",
        "button_primary": "#6A4E9B",
        "button_primary_hover": "#7B5EAC",
        "button_danger": "#8B3A3A",
        "accent_color": "#6A4E9B",
        "font_family": "'Inter', 'Segoe UI', '微软雅黑', sans-serif",
        "code_font": "'Fira Code', Consolas, monospace",
        "border_radius_small": "6px",
        "border_radius_medium": "12px",
        "shadow_small": "0 2px 4px rgba(0,0,0,0.3)",
        "shadow_medium": "0 4px 12px rgba(0,0,0,0.4)",
    }

    LIGHT_THEME = {
        "bg_color": "#F5F7FC",
        "block_bg": "#FFFFFF",
        "card_bg": "#FFFFFF",
        "sidebar_bg": "#F0F2F8",
        "text_primary": "#1A2634",
        "text_secondary": "#6C7A8A",
        "text_emphasis": "#0A1A2A",
        "border": "#E8ECF2",
        "border_light": "#F0F3F8",
        "button_normal": "#F0F2F8",
        "button_hover": "#E8ECF2",
        "button_primary": "#6A4E9B",
        "button_primary_hover": "#7B5EAC",
        "button_danger": "#DC3545",
        "accent_color": "#6A4E9B",
        "font_family": DARK_THEME["font_family"],
        "code_font": DARK_THEME["code_font"],
        "border_radius_small": "6px",
        "border_radius_medium": "12px",
        "shadow_small": "0 2px 8px rgba(0,0,0,0.04)",
        "shadow_medium": "0 4px 16px rgba(0,0,0,0.06)",
    }

    @staticmethod
    def init_theme():
        if 'theme_mode' not in st.session_state:
            st.session_state.theme_mode = 'light'

    @staticmethod
    def get_current_theme():
        mode = st.session_state.get('theme_mode', 'light')
        return ThemeManager.DARK_THEME if mode == 'dark' else ThemeManager.LIGHT_THEME

    @staticmethod
    def toggle_theme():
        st.session_state.theme_mode = 'light' if st.session_state.theme_mode == 'dark' else 'dark'

    @staticmethod
    @staticmethod
    def apply_custom_css():
        theme = ThemeManager.get_current_theme()

        custom_css = f"""
        <style>
            /* ========== 基础样式（安全） ========== */
            .stApp {{
                background-color: {theme['bg_color']};
                font-family: {theme['font_family']};
            }}

            /* 滚动条 */
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
            }}
            ::-webkit-scrollbar-thumb:hover {{
                background: {theme['button_primary']};
            }}

            /* 区块 */
            .block-container {{
                background-color: {theme['block_bg']};
                border-radius: {theme['border_radius_medium']};
                padding: 1.5rem;
                margin-bottom: 1rem;
                border: 1px solid {theme['border']};
                box-shadow: {theme['shadow_small']};
            }}

            /* 文字 */
            .stMarkdown, .stText, p, li, span, div {{
                color: {theme['text_primary']};
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: {theme['text_emphasis']};
                font-weight: 600;
            }}
            h1 {{
                font-size: 2rem;
                background: linear-gradient(135deg, {theme['text_emphasis']}, {theme['accent_color']});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            h2 {{
                font-size: 1.5rem;
                border-left: 4px solid {theme['accent_color']};
                padding-left: 0.75rem;
            }}

            /* 按钮 */
            .stButton > button {{
                background-color: {theme['button_normal']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                border-radius: {theme['border_radius_small']};
                padding: 0.5rem 1rem;
                cursor: pointer;
            }}
            .stButton > button:hover {{
                background-color: {theme['button_hover']};
                border-color: {theme['accent_color']};
            }}
            .stButton > button[kind="primary"] {{
                background: linear-gradient(135deg, {theme['button_primary']}, {theme['button_primary_hover']});
                color: white;
                border: none;
            }}

            /* 侧边栏 */
            [data-testid="stSidebar"] {{
                background-color: {theme['sidebar_bg']};
                border-right: 1px solid {theme['border']};
            }}

            /* 输入框 */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > select,
            .stMultiselect > div > div,
            .stNumberInput > div > div > input {{
                background-color: {theme['card_bg']};
                color: {theme['text_primary']};
                border: 1px solid {theme['border']};
                border-radius: {theme['border_radius_small']};
                padding: 0.5rem 0.75rem;
            }}
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > select:focus {{
                border-color: {theme['accent_color']};
                box-shadow: 0 0 0 2px {theme['accent_color']}40;
            }}

            /* ========== 数据表格 - 最简化版本 ========== */
            .stDataFrame td,
            .stDataFrame th {{
                border: 1px solid {theme['border']};
                padding: 8px 12px;
            }}
            .stDataFrame tbody tr:hover {{
                background-color: {theme['border_light']};
            }}

            /* Metric 卡片 */
            .stMetric {{
                background: linear-gradient(135deg, {theme['card_bg']}, {theme['block_bg']});
                padding: 1rem;
                border-radius: {theme['border_radius_medium']};
                border: 1px solid {theme['border']};
                text-align: center;
            }}
            .stMetric label {{
                color: {theme['text_secondary']};
                font-size: 0.75rem;
                text-transform: uppercase;
            }}
            .stMetric [data-testid="stMetricValue"] {{
                color: {theme['accent_color']};
                font-size: 2rem;
                font-weight: 700;
            }}

            /* 标签页 */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.25rem;
                border-bottom: 2px solid {theme['border']};
                background-color: {theme['block_bg']};
                padding: 0.5rem 0.5rem 0 0.5rem;
            }}
            .stTabs [data-baseweb="tab"] {{
                color: {theme['text_secondary']};
                padding: 0.6rem 1.2rem;
            }}
            .stTabs [aria-selected="true"] {{
                color: {theme['accent_color']};
                border-bottom: 2px solid {theme['accent_color']};
            }}

            /* 主内容区域 */
            .main .block-container {{
                padding: 1rem 2rem 2rem 2rem;
                max-width: 100%;
            }}

            /* 去除顶部留白 */
            .stApp > header {{
                display: none;
            }}

            /* 底部 */
            .footer {{
                text-align: center;
                padding: 2rem;
                color: {theme['text_secondary']};
                border-top: 1px solid {theme['border']};
                font-size: 0.8rem;
            }}
            /* 隐藏所有悬停链接图标 */
            a[title*="Link"] {{
                display: none !important;
            }}

            /* 或隐藏特定区域的 */
            .stMarkdown a {{
                display: none !important;
            }}
        </style>
        """

        st.markdown(custom_css, unsafe_allow_html=True)