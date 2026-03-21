"""
统计分析模块：描述统计/分组统计/相关性/时间序列
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

class StatsAnalyzer:
    """统计分析器"""
    
    @staticmethod
    def descriptive_stats(df):
        """描述性统计"""
        try:
            numeric_df = df.select_dtypes(include=['int64', 'float64'])
            if numeric_df.empty:
                return pd.DataFrame()
            
            stats_df = pd.DataFrame()
            for col in numeric_df.columns:
                col_data = numeric_df[col].dropna()
                if len(col_data) > 0:
                    stats_df[col] = {
                        '均值': col_data.mean(),
                        '中位数': col_data.median(),
                        '众数': col_data.mode().iloc[0] if not col_data.mode().empty else np.nan,
                        '标准差': col_data.std(),
                        '方差': col_data.var(),
                        '最小值': col_data.min(),
                        '最大值': col_data.max(),
                        '极差': col_data.max() - col_data.min(),
                        '偏度': col_data.skew(),
                        '峰度': col_data.kurtosis(),
                        '25%分位数': col_data.quantile(0.25),
                        '50%分位数': col_data.quantile(0.5),
                        '75%分位数': col_data.quantile(0.75),
                        '非空计数': col_data.count(),
                        '缺失值': df[col].isna().sum()
                    }
            
            return stats_df.T
        except Exception as e:
            st.error(f"描述性统计失败: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def group_stats(df, group_cols, value_cols, agg_funcs=None):
        """分组统计"""
        try:
            if agg_funcs is None:
                agg_funcs = ['count', 'mean', 'sum', 'min', 'max', 'std']
            
            return df.groupby(group_cols)[value_cols].agg(agg_funcs).reset_index()
        except Exception as e:
            st.error(f"分组统计失败: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def correlation_analysis(df, method='pearson'):
        """相关性分析"""
        try:
            numeric_df = df.select_dtypes(include=['int64', 'float64'])
            if numeric_df.shape[1] < 2:
                return pd.DataFrame()
            
            if method == 'pearson':
                return numeric_df.corr(method='pearson')
            elif method == 'spearman':
                return numeric_df.corr(method='spearman')
            elif method == 'kendall':
                return numeric_df.corr(method='kendall')
            else:
                return numeric_df.corr()
        except Exception as e:
            st.error(f"相关性分析失败: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def time_series_analysis(df, date_col, value_col, freq='D'):
        """时间序列分析"""
        try:
            # 确保日期列是datetime类型
            df[date_col] = pd.to_datetime(df[date_col])
            
            # 按日期排序
            df = df.sort_values(date_col)
            
            # 设置日期为索引
            ts_df = df.set_index(date_col)[value_col]
            
            # 重采样
            if freq == 'D':
                resampled = ts_df.resample('D').mean()
            elif freq == 'W':
                resampled = ts_df.resample('W').mean()
            elif freq == 'M':
                resampled = ts_df.resample('M').mean()
            elif freq == 'Q':
                resampled = ts_df.resample('Q').mean()
            elif freq == 'Y':
                resampled = ts_df.resample('Y').mean()
            else:
                resampled = ts_df
            
            # 计算移动平均
            ma_7 = ts_df.rolling(window=7).mean()
            ma_30 = ts_df.rolling(window=30).mean()
            
            # 计算增长率
            growth_rate = ts_df.pct_change() * 100
            
            # 同比环比
            if freq == 'M':
                yoy = ts_df / ts_df.shift(12) - 1  # 同比增长率
                mom = ts_df / ts_df.shift(1) - 1   # 环比增长率
            else:
                yoy = pd.Series()
                mom = pd.Series()
            
            result = pd.DataFrame({
                '原始值': ts_df,
                '移动平均7日': ma_7,
                '移动平均30日': ma_30,
                '增长率%': growth_rate,
                '同比增长': yoy if not yoy.empty else None,
                '环比增长': mom if not mom.empty else None
            })
            
            return result
        except Exception as e:
            st.error(f"时间序列分析失败: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def pivot_table(df, index=None, columns=None, values=None, aggfunc='mean'):
        """数据透视表"""
        try:
            return pd.pivot_table(
                df,
                index=index,
                columns=columns,
                values=values,
                aggfunc=aggfunc,
                fill_value=0
            )
        except Exception as e:
            st.error(f"透视表生成失败: {str(e)}")
            return pd.DataFrame()
    