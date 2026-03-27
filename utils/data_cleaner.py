# utils/data_cleaner.py
"""
数据处理模块：去重/替换/转换/分列/合并等
"""

import streamlit as st
import pandas as pd
import re
import numpy as np
from utils.logger import Logger

class DataCleaner:
    """数据清洗处理器"""
    
    @staticmethod
    def deduplicate(df, subset=None, keep='first'):
        """去重"""
        try:
            Logger.info(f"执行去重操作: subset={subset}, keep={keep}")
            before_count = len(df)
            
            if subset:
                result_df = df.drop_duplicates(subset=subset, keep=keep)
            else:
                result_df = df.drop_duplicates(keep=keep)
            
            after_count = len(result_df)
            Logger.info(f"去重完成: {before_count} -> {after_count} 行")
            
            return result_df
        except Exception as e:
            Logger.error(f"去重失败: {str(e)}")
            st.error(f"去重失败: {str(e)}")
            return df
    
    @staticmethod
    def text_replace(df, column, old, new, regex=False):
        """文本替换"""
        try:
            Logger.info(f"执行文本替换: 列={column}, old='{old}', new='{new}', regex={regex}")
            
            # 确保列存在
            if column not in df.columns:
                Logger.error(f"列 {column} 不存在")
                return df
            
            # 创建副本避免警告
            result_df = df.copy()
            
            if regex:
                result_df[column] = result_df[column].astype(str).str.replace(old, new, regex=True)
            else:
                result_df[column] = result_df[column].astype(str).str.replace(old, new, regex=False)
            
            # 验证是否真的有替换
            sample_before = df[column].head(3).tolist()
            sample_after = result_df[column].head(3).tolist()
            Logger.info(f"替换示例 - 前: {sample_before}, 后: {sample_after}")
            
            return result_df
        except Exception as e:
            Logger.error(f"替换失败: {str(e)}")
            st.error(f"替换失败: {str(e)}")
            return df
    
    @staticmethod
    def null_replace(df, column, value=""):
        """空值替换"""
        try:
            Logger.info(f"执行空值替换: 列={column}, 填充值='{value}'")
            
            if column not in df.columns:
                Logger.error(f"列 {column} 不存在")
                return df
            
            result_df = df.copy()
            null_count = result_df[column].isna().sum()
            result_df[column] = result_df[column].fillna(value)
            
            Logger.info(f"空值替换完成: 替换了 {null_count} 个空值")
            return result_df
        except Exception as e:
            Logger.error(f"空值替换失败: {str(e)}")
            st.error(f"空值替换失败: {str(e)}")
            return df
    
    @staticmethod
    def convert_type(df, column, target_type):
        """类型转换"""
        try:
            Logger.info(f"执行类型转换: 列={column}, 目标类型={target_type}")
            
            if column not in df.columns:
                Logger.error(f"列 {column} 不存在")
                return df
            
            result_df = df.copy()
            
            if target_type == "转换为文本" or target_type == "str":
                result_df[column] = result_df[column].astype(str)
                Logger.info(f"转换为文本完成")
                
            elif target_type == "转换为数值" or target_type == "float":
                # 清理非打印字符
                result_df[column] = result_df[column].astype(str).apply(
                    lambda x: re.sub(r'[^\x20-\x7E]', '', str(x))
                )
                # 处理千分位
                result_df[column] = result_df[column].str.replace(',', '', regex=False)
                # 处理负号
                result_df[column] = result_df[column].str.strip()
                
                # 尝试转换
                def safe_convert(val):
                    try:
                        if val == "null" or val == "" or pd.isna(val):
                            return np.nan
                        # 处理负号位置
                        val = str(val).strip()
                        if val.startswith('(') and val.endswith(')'):
                            val = '-' + val[1:-1].replace(',', '')
                        return float(val)
                    except:
                        return np.nan
                
                result_df[column] = result_df[column].apply(safe_convert)
                Logger.info(f"转换为数值完成")
            
            return result_df
            
        except Exception as e:
            Logger.error(f"类型转换失败: {str(e)}")
            st.error(f"类型转换失败: {str(e)}")
            return df
    
    @staticmethod
    def split_column(df, column, separator, mode="最左分隔符"):
        """分列（一次）"""
        try:
            Logger.info(f"执行分列: 列={column}, 分隔符='{separator}', 模式={mode}")
            
            if column not in df.columns:
                Logger.error(f"列 {column} 不存在")
                return df
            
            result_df = df.copy()
            
            if mode == "最左分隔符":
                # 只分割第一次出现
                split_result = result_df[column].astype(str).str.split(separator, n=1, expand=True)
            else:  # 最右分隔符
                # 从右向左分割第一次
                split_result = result_df[column].astype(str).str.rsplit(separator, n=1, expand=True)
            
            # 生成新列名
            new_columns = []
            for i in range(split_result.shape[1]):
                new_col = f"{column}_{i+1}"
                # 避免重名
                base_col = new_col
                counter = 1
                while new_col in result_df.columns:
                    new_col = f"{base_col}_{counter}"
                    counter += 1
                result_df[new_col] = split_result[i]
                new_columns.append(new_col)
            
            Logger.info(f"分列完成: 新增列 {new_columns}")
            return result_df
            
        except Exception as e:
            Logger.error(f"分列失败: {str(e)}")
            st.error(f"分列失败: {str(e)}")
            return df
    
    @staticmethod
    def merge_columns(df, columns, new_col_name, separator=" "):
        """合并多列"""
        try:
            Logger.info(f"执行合并列: 列={columns}, 分隔符='{separator}', 新列名={new_col_name}")
            
            # 验证所有列都存在
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                Logger.error(f"列不存在: {missing_cols}")
                return df
            
            result_df = df.copy()
            
            # 确保所有列都是字符串类型
            for col in columns:
                result_df[col] = result_df[col].astype(str)
            
            # 合并列
            result_df[new_col_name] = result_df[columns].agg(separator.join, axis=1)
            
            Logger.info(f"合并列完成: 新增列 {new_col_name}")
            return result_df
        except Exception as e:
            Logger.error(f"合并列失败: {str(e)}")
            st.error(f"合并列失败: {str(e)}")
            return df
    
    @staticmethod
    def delete_columns(df, columns):
        """删除列"""
        try:
            Logger.info(f"执行删除列: {columns}")
            
            # 验证所有列都存在
            existing_cols = [col for col in columns if col in df.columns]
            if not existing_cols:
                Logger.error("没有要删除的有效列")
                return df
            
            result_df = df.drop(columns=existing_cols)
            Logger.info(f"删除列完成: 删除了 {len(existing_cols)} 列")
            
            return result_df
        except Exception as e:
            Logger.error(f"删除列失败: {str(e)}")
            st.error(f"删除列失败: {str(e)}")
            return df
    @staticmethod
    def is_empty_column(series):
        """判断列是否全为空值"""
        # 检查 NaN/None
        if series.isna().all():
            return True
        # 只对 object 类型检查字符串空值
        if series.dtype == 'object':
            # 检查是否全部为空字符串
            if (series == '').all():
                return True
            # 检查是否全部为字符串 "null"
            if (series == 'null').all():
                return True
            # 检查是否全部为字符串 "None"
            if (series == 'None').all():
                return True
        return False