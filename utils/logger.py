"""
调试日志模块
"""
import streamlit as st
from datetime import datetime

class Logger:
    """简单的调试日志器"""
    
    @staticmethod
    def info(message):
        """记录信息日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"✅ [{timestamp}] {message}"
        
        # 保存到 session_state
        if 'debug_logs' not in st.session_state:
            st.session_state.debug_logs = []
        
        st.session_state.debug_logs.append(log_entry)
        print(log_entry)  # 同时在控制台输出
    
    @staticmethod
    def error(message):
        """记录错误日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"❌ [{timestamp}] {message}"
        
        if 'debug_logs' not in st.session_state:
            st.session_state.debug_logs = []
        
        st.session_state.debug_logs.append(log_entry)
        print(log_entry)
    
    @staticmethod
    def show_logs():
        """显示日志面板"""
        if st.session_state.get('debug_logs'):
            with st.expander("📋 调试日志", expanded=False):
                for log in st.session_state.debug_logs[-10:]:  # 显示最近10条
                    st.text(log)