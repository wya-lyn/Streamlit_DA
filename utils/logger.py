"""
调试日志模块
"""
from datetime import datetime

class Logger:
    """简单的调试日志器"""
    
    _logs = []
    
    @staticmethod
    def info(message):
        """记录信息日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"✅ [{timestamp}] {message}"
        Logger._logs.append(log_entry)
        print(log_entry)  # 输出到控制台
    
    @staticmethod
    def error(message):
        """记录错误日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"❌ [{timestamp}] {message}"
        Logger._logs.append(log_entry)
        print(log_entry)
    
    @staticmethod
    def get_logs():
        """获取日志"""
        return Logger._logs
    
    @staticmethod
    def clear():
        """清空日志"""
        Logger._logs = []