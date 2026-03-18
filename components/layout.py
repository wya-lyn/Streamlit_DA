"""
布局管理模块：双菜单可折叠布局
"""

import streamlit as st
from utils.theme_manager import ThemeManager

class LayoutManager:
    """布局管理器"""
    
    def __init__(self):
        self.init_session_state()
    
    def init_session_state(self):
        """初始化会话状态"""
        if 'left_menu_collapsed' not in st.session_state:
            st.session_state.left_menu_collapsed = False
        if 'right_panel_collapsed' not in st.session_state:
            st.session_state.right_panel_collapsed = False
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "首页"
    
    def create_left_menu(self):
        """创建左侧主菜单"""
        theme = ThemeManager.get_current_theme()
        
        # 菜单折叠/展开按钮
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("☰" if st.session_state.left_menu_collapsed else "◀", 
                        key="toggle_left_menu"):
                st.session_state.left_menu_collapsed = not st.session_state.left_menu_collapsed
                st.rerun()
        
        with col2:
            if not st.session_state.left_menu_collapsed:
                st.markdown("### 主菜单")
        
        st.divider()
        
        # 菜单项
        if not st.session_state.left_menu_collapsed:
            menu_items = {
                "🏠 首页": "首页",
                "📁 数据管理": "数据管理",
                "📊 数据分析": "数据分析",
                "📈 可视化": "可视化",
                "🤖 AI分析": "AI分析",
                "⚙️ 设置": "设置"
            }
            
            for display, page in menu_items.items():
                if st.button(display, key=f"menu_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()
                
                # 显示当前页面的指示器
                if st.session_state.current_page == page:
                    st.markdown(f"""
                    <div style="
                        height: 2px;
                        background-color: {theme['menu_selected']};
                        margin: 0 1rem;
                    "></div>
                    """, unsafe_allow_html=True)
        else:
            # 折叠时只显示图标
            menu_icons = {
                "🏠": "首页",
                "📁": "数据管理", 
                "📊": "数据分析",
                "📈": "可视化",
                "🤖": "AI分析",
                "⚙️": "设置"
            }
            
            cols = st.columns(1)
            for icon, page in menu_icons.items():
                if st.button(icon, key=f"icon_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()
    
    def create_right_panel(self):
        """创建右侧功能面板"""
        theme = ThemeManager.get_current_theme()
        
        # 面板折叠/展开按钮
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("▶" if st.session_state.right_panel_collapsed else "◀", 
                        key="toggle_right_panel"):
                st.session_state.right_panel_collapsed = not st.session_state.right_panel_collapsed
                st.rerun()
        
        with col1:
            if not st.session_state.right_panel_collapsed:
                st.markdown("### 功能面板")
        
        st.divider()
        
        return not st.session_state.right_panel_collapsed
    
    def get_current_page(self):
        """获取当前页面"""
        return st.session_state.current_page
    
    def create_breadcrumb(self):
        """创建面包屑导航"""
        page = self.get_current_page()
        st.markdown(f"""
        <div style="
            padding: 0.5rem 0;
            margin-bottom: 1rem;
            border-bottom: 1px solid #3D3D3D;
            color: #B0B0B0;
            font-size: 0.9rem;
        ">
            当前位置：{page}
        </div>
        """, unsafe_allow_html=True)