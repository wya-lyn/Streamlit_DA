"""
顶部公告组件：从JSON读取公告信息并显示
"""

import streamlit as st
import json
import os
from datetime import datetime
from utils.theme_manager import ThemeManager

class AnnouncementManager:
    """公告管理器"""
    
    def __init__(self, config_path="configs/announcements.json"):
        self.config_path = config_path
        self.announcements = self._load_announcements()
    
    def _load_announcements(self):
        """加载公告配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"enabled": False, "announcements": []}
        except Exception as e:
            st.error(f"加载公告配置失败: {e}")
            return {"enabled": False, "announcements": []}
    
    def _is_valid(self, announcement):
        """检查公告是否在有效期内"""
        if not announcement.get("enabled", True):
            return False
        
        try:
            start_date = announcement.get("startDate")
            end_date = announcement.get("endDate")
            today = datetime.now().date()
            
            if start_date:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                if today < start:
                    return False
            
            if end_date:
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                if today > end:
                    return False
            
            return True
        except:
            return True
    
    def show_announcements(self):
        """显示公告"""
        if not self.announcements.get("enabled", False):
            return
        
        theme = ThemeManager.get_current_theme()
        
        for ann in self.announcements.get("announcements", []):
            if self._is_valid(ann):
                ann_type = ann.get("type", "info")
                content = ann.get("content", "")
                ann_id = ann.get("id", "")
                dismissible = ann.get("dismissible", True)
                
                # 检查是否已关闭
                if dismissible and f"announcement_closed_{ann_id}" in st.session_state:
                    continue
                
                # 根据类型显示不同样式
                if ann_type == "info":
                    st.markdown(f"""
                    <div class="announcement-info">
                        ℹ️ {content}
                    </div>
                    """, unsafe_allow_html=True)
                elif ann_type == "warning":
                    st.markdown(f"""
                    <div class="announcement-warning">
                        ⚠️ {content}
                    </div>
                    """, unsafe_allow_html=True)
                elif ann_type == "success":
                    st.markdown(f"""
                    <div class="announcement-success">
                        ✅ {content}
                    </div>
                    """, unsafe_allow_html=True)
                
                # 可关闭按钮
                if dismissible:
                    col1, col2 = st.columns([10, 1])
                    with col2:
                        if st.button("✕", key=f"close_{ann_id}"):
                            st.session_state[f"announcement_closed_{ann_id}"] = True
                            st.rerun()