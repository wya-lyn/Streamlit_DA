"""
底部信息组件：从JSON读取版权信息并显示
"""

import streamlit as st
import json
import os
from utils.theme_manager import ThemeManager

class FooterManager:
    """底部信息管理器"""
    
    def __init__(self, config_path="configs/site_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """加载站点配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "site": {
                        "name": "数据洞察助手",
                        "version": "1.0.0",
                        "copyright": "© 2024",
                        "icp": "",
                        "company": ""
                    },
                    "footer": {
                        "showVersion": True,
                        "showICP": False,
                        "links": []
                    }
                }
        except Exception as e:
            st.error(f"加载站点配置失败: {e}")
            return {}
    
    def show_footer(self):
        """显示底部信息"""
        theme = ThemeManager.get_current_theme()
        site = self.config.get("site", {})
        footer = self.config.get("footer", {})
        
        footer_html = '<div class="footer">'
        
        # 版权信息
        copyright_text = site.get("copyright", "")
        company = site.get("company", "")
        if company:
            copyright_text += f" {company}"
        footer_html += f'<span>{copyright_text}</span>'
        
        # 版本信息
        if footer.get("showVersion", True):
            version = site.get("version", "1.0.0")
            footer_html += f' <span>v{version}</span>'
        
        # ICP备案
        if footer.get("showICP", False):
            icp = site.get("icp", "")
            if icp:
                footer_html += f' <span>{icp}</span>'
        
        # 链接
        links = footer.get("links", [])
        if links:
            footer_html += ' <span>|</span> '
            link_htmls = []
            for link in links:
                text = link.get("text", "")
                url = link.get("url", "#")
                link_htmls.append(f'<a href="{url}" target="_blank">{text}</a>')
            footer_html += ' <span>|</span> '.join(link_htmls)
        
        footer_html += '</div>'
        
        st.markdown(footer_html, unsafe_allow_html=True)