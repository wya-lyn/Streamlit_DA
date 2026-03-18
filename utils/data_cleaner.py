"""
数据处理模块：去重/替换/转换/分列/合并等
"""

import streamlit as st
import pandas as pd
import re
import numpy as np

class DataCleaner:
    """数据清洗处理器"""
    
    @staticmethod
    def deduplicate(df, subset=None, keep='first'):
        """去重"""
        try:
            if subset:
                return df.drop_duplicates(subset=subset, keep=keep)
            else:
                return df.drop_duplicates(keep=keep)
        except Exception as e:
            st.error(f"去重失败: {str(e)}")
            return df
    
    @staticmethod
    def text_replace(df, column, old, new, regex=False):
        """文本替换"""
        try:
            if regex:
                df[column] = df[column].astype(str).str.replace(old, new, regex=True)
            else:
                df[column] = df[column].astype(str).str.replace(old, new, regex=False)
            return df
        except Exception as e:
            st.error(f"替换失败: {str(e)}")
            return df
    
    @staticmethod
    def null_replace(df, column, value=""):
        """空值替换"""
        try:
            df[column] = df[column].fillna(value)
            return df
        except Exception as e:
            st.error(f"空值替换失败: {str(e)}")
            return df
    
    @staticmethod
    def convert_type(df, column, target_type):
        """类型转换"""
        try:
            if target_type == "转换为文本":
                df[column] = df[column].astype(str)
                return df
            
            elif target_type == "转换为数值":
                # 清理非打印字符
                df[column] = df[column].astype(str).apply(
                    lambda x: re.sub(r'[^\x20-\x7E]', '', str(x))
                )
                # 处理千分位
                df[column] = df[column].str.replace(',', '', regex=False)
                # 处理负号
                df[column] = df[column].str.strip()
                
                # 尝试转换
                def safe_convert(val):
                    try:
                        if val == "null" or val == "":
                            return np.nan
                        # 处理负号位置
                        val = str(val).strip()
                        if val.startswith('(') and val.endswith(')'):
                            val = '-' + val[1:-1].replace(',', '')
                        return float(val)
                    except:
                        return "转换错误"
                
                df[column] = df[column].apply(safe_convert)
                return df
            
            return df
            
        except Exception as e:
            st.error(f"类型转换失败: {str(e)}")
            return df
    
    @staticmethod
    def split_column(df, column, separator, mode="最左分隔符"):
        """分列（一次）"""
        try:
            if mode == "最左分隔符":
                # 只分割第一次出现
                split_result = df[column].astype(str).str.split(separator, n=1, expand=True)
            else:  # 最右分隔符
                # 从右向左分割第一次
                split_result = df[column].astype(str).str.rsplit(separator, n=1, expand=True)
            
            # 生成新列名
            for i in range(split_result.shape[1]):
                new_col = f"{column}_{i+1}"
                # 避免重名
                base_col = new_col
                counter = 1
                while new_col in df.columns:
                    new_col = f"{base_col}_{counter}"
                    counter += 1
                df[new_col] = split_result[i]
            
            return df
            
        except Exception as e:
            st.error(f"分列失败: {str(e)}")
            return df
    
    @staticmethod
    def merge_columns(df, columns, new_col_name, separator=" "):
        """合并多列"""
        try:
            df[new_col_name] = df[columns].astype(str).agg(separator.join, axis=1)
            return df
        except Exception as e:
            st.error(f"合并列失败: {str(e)}")
            return df
    
    @staticmethod
    def rename_column(df, old_name, new_name):
        """修改表头"""
        try:
            return df.rename(columns={old_name: new_name})
        except Exception as e:
            st.error(f"修改表头失败: {str(e)}")
            return df
    
    @staticmethod
    def delete_columns(df, columns):
        """删除列"""
        try:
            return df.drop(columns=columns)
        except Exception as e:
            st.error(f"删除列失败: {str(e)}")
            return df
    
    @staticmethod
    def preview_operation(df, operation_func, *args, **kwargs):
        """预览操作效果"""
        try:
            preview_df = df.head(10).copy()
            result_df = operation_func(preview_df, *args, **kwargs)
            return result_df
        except Exception as e:
            st.error(f"预览失败: {str(e)}")
            return df.head(10)