"""
数据筛选模块：文本/数值/日期筛选
"""

import streamlit as st
import pandas as pd
import re

class DataFilter:
    """数据筛选器"""
    
    @staticmethod
    def text_filter(df, column, condition, value):
        """文本筛选"""
        try:
            if condition == "包含":
                return df[df[column].astype(str).str.contains(value, na=False)]
            elif condition == "等于":
                return df[df[column].astype(str) == value]
            elif condition == "开头为":
                return df[df[column].astype(str).str.startswith(value, na=False)]
            elif condition == "结尾为":
                return df[df[column].astype(str).str.endswith(value, na=False)]
            elif condition == "不包含":
                return df[~df[column].astype(str).str.contains(value, na=False)]
            elif condition == "不为空":
                return df[df[column].notna() & (df[column] != "null")]
            elif condition == "为空":
                return df[df[column].isna() | (df[column] == "null")]
            return df
        except Exception as e:
            st.error(f"文本筛选失败: {str(e)}")
            return df
    
    @staticmethod
    def numeric_filter(df, column, condition, value):
        """数值筛选"""
        try:
            # 确保列是数值类型
            df[column] = pd.to_numeric(df[column], errors='coerce')
            
            if condition == "大于":
                return df[df[column] > value]
            elif condition == "小于":
                return df[df[column] < value]
            elif condition == "等于":
                return df[df[column] == value]
            elif condition == "大于等于":
                return df[df[column] >= value]
            elif condition == "小于等于":
                return df[df[column] <= value]
            elif condition == "介于":
                min_val, max_val = value
                return df[(df[column] >= min_val) & (df[column] <= max_val)]
            elif condition == "不介于":
                min_val, max_val = value
                return df[(df[column] < min_val) | (df[column] > max_val)]
            elif condition == "为空":
                return df[df[column].isna()]
            elif condition == "不为空":
                return df[df[column].notna()]
            return df
        except Exception as e:
            st.error(f"数值筛选失败: {str(e)}")
            return df
    
    @staticmethod
    def date_filter(df, column, condition, value):
        """日期筛选"""
        try:
            # 尝试转换为日期
            df[column] = pd.to_datetime(df[column], errors='coerce')
            
            if condition == "等于":
                return df[df[column].dt.date == value]
            elif condition == "早于":
                return df[df[column].dt.date < value]
            elif condition == "晚于":
                return df[df[column].dt.date > value]
            elif condition == "介于":
                start_date, end_date = value
                return df[(df[column].dt.date >= start_date) & 
                         (df[column].dt.date <= end_date)]
            elif condition == "今天":
                today = pd.Timestamp.now().date()
                return df[df[column].dt.date == today]
            elif condition == "本周":
                today = pd.Timestamp.now()
                start = today - pd.Timedelta(days=today.weekday())
                end = start + pd.Timedelta(days=6)
                return df[(df[column] >= start) & (df[column] <= end)]
            elif condition == "本月":
                today = pd.Timestamp.now()
                start = today.replace(day=1)
                end = (start + pd.offsets.MonthEnd(0))
                return df[(df[column] >= start) & (df[column] <= end)]
            elif condition == "为空":
                return df[df[column].isna()]
            elif condition == "不为空":
                return df[df[column].notna()]
            return df
        except Exception as e:
            st.error(f"日期筛选失败: {str(e)}")
            return df
    
    @staticmethod
    def combine_filters(df, filters, logic="AND"):
        """组合多个筛选条件"""
        try:
            if not filters:
                return df
            
            if logic == "AND":
                for filter_func in filters:
                    df = filter_func(df)
                return df
            else:  # OR
                results = []
                for filter_func in filters:
                    results.append(filter_func(df))
                return pd.concat(results).drop_duplicates()
        except Exception as e:
            st.error(f"组合筛选失败: {str(e)}")
            return df