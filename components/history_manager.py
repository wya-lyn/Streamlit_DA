"""
历史记录模块：操作历史/本地存储
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import hashlib

class HistoryManager:
    """历史记录管理器"""
    
    def __init__(self, storage_days=7):
        self.storage_days = storage_days
        self.history_key = 'operation_history'
        self.init_history()
    
    def init_history(self):
        """初始化历史记录"""
        if self.history_key not in st.session_state:
            st.session_state[self.history_key] = []
        
        # 清理过期记录
        self._clean_expired()
    
    def add_to_history(self, operation_name, df, metadata=None):
        """添加操作到历史记录"""
        try:
            # 生成操作记录
            record = {
                'id': self._generate_id(),
                'timestamp': datetime.now().isoformat(),
                'operation': operation_name,
                'rows': len(df) if df is not None else 0,
                'columns': len(df.columns) if df is not None else 0,
                'metadata': metadata or {},
                'preview': df.head(3).to_dict('records') if df is not None else []
            }
            
            # 添加到session_state
            st.session_state[self.history_key].append(record)
            
            # 保存到本地存储（可选）
            self._save_to_local_storage()
            
        except Exception as e:
            st.error(f"保存历史记录失败: {str(e)}")
    
    def get_history(self, limit=50):
        """获取历史记录"""
        history = st.session_state.get(self.history_key, [])
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def clear_history(self):
        """清空历史记录"""
        st.session_state[self.history_key] = []
        self._save_to_local_storage()
    
    def show_history(self):
        """显示历史记录"""
        history = self.get_history()
        
        if not history:
            st.info("暂无历史记录")
            return
        
        for record in history:
            with st.expander(f"{record['timestamp'][:19]} - {record['operation']}"):
                st.json({
                    '操作': record['operation'],
                    '时间': record['timestamp'][:19],
                    '数据行数': record['rows'],
                    '数据列数': record['columns'],
                    '预览': record['preview'][:1] if record['preview'] else []
                })
    
    def _generate_id(self):
        """生成唯一ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    def _clean_expired(self):
        """清理过期记录"""
        if self.history_key not in st.session_state:
            return
        
        cutoff = datetime.now() - timedelta(days=self.storage_days)
        valid_records = []
        
        for record in st.session_state[self.history_key]:
            try:
                record_time = datetime.fromisoformat(record['timestamp'])
                if record_time > cutoff:
                    valid_records.append(record)
            except:
                continue
        
        st.session_state[self.history_key] = valid_records
    
    def _save_to_local_storage(self):
        """保存到本地存储（浏览器）"""
        try:
            # 这里预留本地存储代码
            # 可以使用st.experimental_set_query_params等
            pass
        except:
            pass
    
    def undo(self, df):
        """撤销操作"""
        # 这里需要结合具体的数据状态管理
        # 简单返回原数据
        return df
    
    def redo(self, df):
        """重做操作"""
        return df
    
    def export_history(self, format="json"):
        """导出历史记录"""
        history = self.get_history()
        
        if format == "json":
            return json.dumps(history, ensure_ascii=False, indent=2)
        elif format == "csv":
            # 转换为DataFrame导出
            df_history = pd.DataFrame(history)
            return df_history.to_csv(index=False)
        else:
            return None

class LocalStorage:
    """本地存储管理（浏览器）"""
    
    @staticmethod
    def save(key, value):
        """保存到本地存储"""
        try:
            # 使用query params模拟本地存储
            st.query_params[key] = json.dumps(value, ensure_ascii=False)
            return True
        except:
            return False
    
    @staticmethod
    def load(key, default=None):
        """从本地存储加载"""
        try:
            if key in st.query_params:
                return json.loads(st.query_params[key])
            return default
        except:
            return default
    
    @staticmethod
    def clear(key=None):
        """清除本地存储"""
        if key:
            if key in st.query_params:
                del st.query_params[key]
        else:
            st.query_params.clear()