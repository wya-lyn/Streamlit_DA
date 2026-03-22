"""
图表生成模块：统一图表生成入口
"""

import streamlit as st
import pandas as pd
from utils.chart_factory import (
    BarChart, LineChart, PieChart, ScatterChart, BoxChart,
    HistogramChart, HeatmapChart, CompositePieChart,
    GroupedBarChart, StackedBarChart, HorizontalBarChart
)


class ChartGenerator:
    """图表生成器 - 统一调用入口"""
    
    # 图表类型映射
    _CHART_MAP = {
        "柱状图": BarChart(),
        "折线图": LineChart(),
        "饼图": PieChart(),
        "散点图": ScatterChart(),
        "箱线图": BoxChart(),
        "直方图": HistogramChart(),
        "热力图": HeatmapChart(),
        "复合饼图": CompositePieChart(),
        "分组柱状图": GroupedBarChart(),
        "堆积柱状图": StackedBarChart(),
        "条形图": HorizontalBarChart(),
    }
    
    @staticmethod
    def create_chart(df, chart_type, x_col=None, y_col=None, **kwargs):
        """
        创建图表
        
        Parameters:
        -----------
        df : DataFrame
            数据源
        chart_type : str
            图表类型
        x_col : str
            X轴列名
        y_col : str
            Y轴列名
        **kwargs : dict
            其他参数（show_values, colorscale, pie_mode, color等）
        
        Returns:
        --------
        plotly.graph_objects.Figure 或 None
        """
        try:
            # 验证数据
            if df is None or df.empty:
                st.error("数据为空，无法生成图表")
                return None
            
            # 获取对应的图表类
            chart_class = ChartGenerator._CHART_MAP.get(chart_type)
            if chart_class is None:
                st.error(f"不支持的图表类型: {chart_type}")
                return None
            
            # 创建图表
            fig = chart_class.create(df, x_col, y_col, **kwargs)
            
            if fig is None:
                st.error(f"图表生成失败: {chart_type}")
                return None
            
            return fig
            
        except Exception as e:
            st.error(f"图表生成失败 [{chart_type}]: {str(e)}")
            return None
    
    @staticmethod
    def get_available_charts():
        """获取所有可用的图表类型"""
        return list(ChartGenerator._CHART_MAP.keys())