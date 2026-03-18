"""
图表生成模块：支持多种图表类型和复合饼图
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

class ChartGenerator:
    """图表生成器"""
    
    @staticmethod
    def create_chart(df, chart_type, x_col=None, y_col=None, color_col=None, **kwargs):
        """创建基础图表"""
        try:
            if chart_type == "柱状图":
                return ChartGenerator._create_bar_chart(df, x_col, y_col, color_col, **kwargs)
            elif chart_type == "折线图":
                return ChartGenerator._create_line_chart(df, x_col, y_col, color_col, **kwargs)
            elif chart_type == "散点图":
                return ChartGenerator._create_scatter_chart(df, x_col, y_col, color_col, **kwargs)
            elif chart_type == "热力图":
                return ChartGenerator._create_heatmap(df, **kwargs)
            elif chart_type == "饼图":
                return ChartGenerator._create_pie_chart(df, x_col, y_col, **kwargs)
            elif chart_type == "复合饼图":
                mode = kwargs.get('pie_mode', '子图布局')
                return ChartGenerator._create_composite_pie(df, x_col, y_col, mode, **kwargs)
            elif chart_type == "箱线图":
                return ChartGenerator._create_box_plot(df, x_col, y_col, **kwargs)
            elif chart_type == "直方图":
                return ChartGenerator._create_histogram(df, x_col, **kwargs)
            else:
                return None
        except Exception as e:
            st.error(f"图表生成失败: {str(e)}")
            return None
    
    @staticmethod
    def _create_bar_chart(df, x_col, y_col, color_col=None, **kwargs):
        """创建柱状图"""
        fig = px.bar(
            df, 
            x=x_col, 
            y=y_col,
            color=color_col,
            title=kwargs.get('title', f'{y_col} 分布'),
            template='plotly_dark' if st.session_state.theme_mode == 'dark' else 'plotly_white'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0' if st.session_state.theme_mode == 'dark' else '#333333')
        )
        return fig
    
    @staticmethod
    def _create_line_chart(df, x_col, y_col, color_col=None, **kwargs):
        """创建折线图"""
        fig = px.line(
            df, 
            x=x_col, 
            y=y_col,
            color=color_col,
            title=kwargs.get('title', f'{y_col} 趋势'),
            template='plotly_dark' if st.session_state.theme_mode == 'dark' else 'plotly_white'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0' if st.session_state.theme_mode == 'dark' else '#333333')
        )
        return fig
    
    @staticmethod
    def _create_scatter_chart(df, x_col, y_col, color_col=None, **kwargs):
        """创建散点图"""
        fig = px.scatter(
            df, 
            x=x_col, 
            y=y_col,
            color=color_col,
            title=kwargs.get('title', f'{x_col} vs {y_col}'),
            template='plotly_dark' if st.session_state.theme_mode == 'dark' else 'plotly_white'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0' if st.session_state.theme_mode == 'dark' else '#333333')
        )
        return fig
    
    @staticmethod
    def _create_heatmap(df, **kwargs):
        """创建热力图"""
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        if numeric_df.shape[1] < 2:
            return None
        
        corr = numeric_df.corr()
        fig = px.imshow(
            corr,
            text_auto=True,
            title=kwargs.get('title', '相关性热力图'),
            template='plotly_dark' if st.session_state.theme_mode == 'dark' else 'plotly_white',
            color_continuous_scale='RdBu_r'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0' if st.session_state.theme_mode == 'dark' else '#333333')
        )
        return fig
    
    @staticmethod
    def _create_pie_chart(df, names_col, values_col, **kwargs):
        """创建饼图"""
        # 聚合数据
        pie_data = df.groupby(names_col)[values_col].sum().reset_index()
        
        fig = px.pie(
            pie_data,
            names=names_col,
            values=values_col,
            title=kwargs.get('title', f'{names_col} 分布'),
            template='plotly_dark' if st.session_state.theme_mode == 'dark' else 'plotly_white'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0' if st.session_state.theme_mode == 'dark' else '#333333')
        )
        return fig
    
    @staticmethod
    def _create_box_plot(df, x_col, y_col, **kwargs):
        """创建箱线图"""
        fig = px.box(
            df,
            x=x_col,
            y=y_col,
            title=kwargs.get('title', f'{y_col} 分布箱线图'),
            template='plotly_dark' if st.session_state.theme_mode == 'dark' else 'plotly_white'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0' if st.session_state.theme_mode == 'dark' else '#333333')
        )
        return fig
    
    @staticmethod
    def _create_histogram(df, x_col, **kwargs):
        """创建直方图"""
        bins = kwargs.get('bins', 30)
        fig = px.histogram(
            df,
            x=x_col,
            nbins=bins,
            title=kwargs.get('title', f'{x_col} 分布直方图'),
            template='plotly_dark' if st.session_state.theme_mode == 'dark' else 'plotly_white'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0' if st.session_state.theme_mode == 'dark' else '#333333')
        )
        return fig
    
    @staticmethod
    def _create_composite_pie(df, category_col, value_col, mode="子图布局", **kwargs):
        """创建复合饼图（三种模式）"""
        try:
            # 获取顶层类别
            top_categories = df[category_col].value_counts().nlargest(4).index.tolist()
            
            if mode == "子图布局":
                return ChartGenerator._composite_pie_subplot(df, category_col, value_col, top_categories)
            elif mode == "交互下钻":
                return ChartGenerator._composite_pie_drilldown(df, category_col, value_col, **kwargs)
            elif mode == "复合定位":
                return ChartGenerator._composite_pie_layout(df, category_col, value_col, top_categories)
            else:
                return None
        except Exception as e:
            st.error(f"复合饼图生成失败: {str(e)}")
            return None
    
    @staticmethod
    def _composite_pie_subplot(df, category_col, value_col, top_categories):
        """模式一：子图布局"""
        # 计算主图数据
        main_data = df.groupby(category_col)[value_col].sum().reset_index()
        
        # 创建子图布局（2行2列）
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type':'domain'}, {'type':'domain'}],
                   [{'type':'domain'}, {'type':'domain'}]],
            subplot_titles=([category_col] + [f"{cat}详情" for cat in top_categories[:3]])
        )
        
        # 主图（左上）
        fig.add_trace(
            go.Pie(labels=main_data[category_col], values=main_data[value_col], name="主图"),
            row=1, col=1
        )
        
        # 子图（每个大类的小类构成）
        for i, category in enumerate(top_categories[:3]):
            row = 1 if i < 1 else 2
            col = 2 if i == 0 else (i % 2 + 1)
            
            # 获取该类别下的数据
            cat_data = df[df[category_col] == category]
            if len(cat_data) > 0:
                sub_categories = cat_data.head(5)  # 取前5条作为子类别示例
                fig.add_trace(
                    go.Pie(
                        labels=sub_categories.index.astype(str),
                        values=sub_categories[value_col],
                        name=f"{category}详情"
                    ),
                    row=row, col=col
                )
        
        fig.update_layout(
            title_text="复合饼图 - 子图布局",
            height=800,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0' if st.session_state.theme_mode == 'dark' else '#333333'),
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def _composite_pie_drilldown(df, category_col, value_col, **kwargs):
        """模式二：交互下钻"""
        # 主图
        main_data = df.groupby(category_col)[value_col].sum().reset_index()
        
        fig = px.pie(
            main_data,
            names=category_col,
            values=value_col,
            title="点击主图区块查看详情",
            template='plotly_dark' if st.session_state.theme_mode == 'dark' else 'plotly_white'
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0' if st.session_state.theme_mode == 'dark' else '#333333'),
            clickmode='event+select'
        )
        
        return fig
    
    @staticmethod
    def _composite_pie_layout(df, category_col, value_col, top_categories):
        """模式三：复合定位"""
        fig = go.Figure()
        
        # 主图（居中偏上）
        main_data = df.groupby(category_col)[value_col].sum().reset_index()
        fig.add_trace(go.Pie(
            labels=main_data[category_col],
            values=main_data[value_col],
            domain=dict(x=[0.3, 0.7], y=[0.5, 0.9]),
            name="主图",
            title=dict(text="主图分布", position="top center")
        ))
        
        # 子图环绕
        positions = [
            dict(x=[0, 0.25], y=[0, 0.4]),   # 左下
            dict(x=[0.75, 1], y=[0, 0.4]),   # 右下
            dict(x=[0, 0.25], y=[0.6, 1]),   # 左上
            dict(x=[0.75, 1], y=[0.6, 1])    # 右上
        ]
        
        for i, category in enumerate(top_categories[:4]):
            cat_data = df[df[category_col] == category]
            if len(cat_data) > 0 and i < len(positions):
                sub_categories = cat_data.head(5)
                fig.add_trace(go.Pie(
                    labels=sub_categories.index.astype(str),
                    values=sub_categories[value_col],
                    domain=positions[i],
                    name=f"{category}详情"
                ))
        
        fig.update_layout(
            title_text="复合饼图 - 复合定位",
            height=800,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0' if st.session_state.theme_mode == 'dark' else '#333333'),
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def export_chart(fig, format="png"):
        """导出图表"""
        try:
            if format == "png":
                return fig.to_image(format="png", width=1200, height=800, scale=2)
            elif format == "svg":
                return fig.to_image(format="svg", width=1200, height=800)
            elif format == "pdf":
                return fig.to_image(format="pdf", width=1200, height=800)
            else:
                return None
        except Exception as e:
            st.error(f"图表导出失败: {str(e)}")
            return None