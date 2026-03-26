"""
顶部公告组件：从JSON读取公告信息并显示
"""

import streamlit as st
import json
import os
from datetime import datetime
import time
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
        """显示第一条有效公告"""
        if not self.announcements.get("enabled", False):
            return
        
        # 获取有效公告
        valid_announcements = []
        for ann in self.announcements.get("announcements", []):
            if self._is_valid(ann):
                valid_announcements.append(ann)
        
        if not valid_announcements:
            return
        
        # 只取第一条公告
        current = valid_announcements[0]
        
        ann_type = current.get("type", "info")
        content = current.get("content", "")
        
        # 显示公告
        if ann_type == "info":
            st.info(f"📢 {content}")
        elif ann_type == "warning":
            st.warning(f"⚠️ {content}")
        elif ann_type == "success":
            st.success(f"✅ {content}")