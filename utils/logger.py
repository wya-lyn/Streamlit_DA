"""
调试日志模块 - 支持文件记录
"""

import streamlit as st
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 日志文件路径
LOG_FILE = "app.log"
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT = 1  # 保留1个备份


class Logger:
    """日志记录器"""
    
    _logger = None
    
    @classmethod
    def _get_logger(cls):
        """获取或创建日志器"""
        if cls._logger is None:
            cls._logger = logging.getLogger("DataInsight")
            cls._logger.setLevel(logging.INFO)
            
            # 避免重复添加handler
            if not cls._logger.handlers:
                # 文件处理器（自动轮转）
                file_handler = RotatingFileHandler(
                    LOG_FILE,
                    maxBytes=LOG_MAX_SIZE,
                    backupCount=LOG_BACKUP_COUNT,
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.INFO)
                
                # 格式
                formatter = logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(formatter)
                
                cls._logger.addHandler(file_handler)
        
        return cls._logger
    
    @classmethod
    def info(cls, message):
        """记录信息日志"""
        logger = cls._get_logger()
        logger.info(message)
    
    @classmethod
    def error(cls, message):
        """记录错误日志"""
        logger = cls._get_logger()
        logger.error(message)
    
    @classmethod
    def warning(cls, message):
        """记录警告日志"""
        logger = cls._get_logger()
        logger.warning(message)
  
    
    @classmethod
    def exception(cls, message):
        """记录异常日志（包含堆栈）"""
        logger = cls._get_logger()
        logger.exception(message)

    
    @classmethod
    def show_logs(cls, lines=50):
        """显示最近的日志"""
        if not os.path.exists(LOG_FILE):
            st.info("暂无日志文件")
            return
        
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                st.text_area("日志内容", "".join(recent), height=300)
                
                # 下载按钮
                csv = "".join(all_lines).encode('utf-8')
                st.download_button(
                    label="📥 下载完整日志",
                    data=csv,
                    file_name=f"app_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"读取日志失败: {e}")
    
    @classmethod
    def clear_logs(cls):
        """清空日志文件"""
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'w', encoding='utf-8') as f:
                    f.write("")
                st.success("日志已清空")
        except Exception as e:
            st.error(f"清空日志失败: {e}")