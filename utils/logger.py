# utils/logger.py
"""
调试日志模块
"""
from datetime import datetime
import streamlit as st

class Logger:
    """简单的调试日志器"""
    
    _logs = []
    
    @staticmethod
    def info(message):
        """记录信息日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"✅ [{timestamp}] {message}"
        Logger._logs.append(log_entry)
        print(log_entry)
    
    @staticmethod
    def error(message):
        """记录错误日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"❌ [{timestamp}] {message}"
        Logger._logs.append(log_entry)
        print(log_entry)
    
    @staticmethod
    def show_logs():
        """显示日志面板（需要在有 streamlit 的环境调用）"""
        
        if Logger._logs:
            with st.expander("📋 调试日志", expanded=False):
                for log in Logger._logs[-10:]:
                    st.text(log)