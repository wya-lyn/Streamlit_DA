"""
图表工厂模块：定义所有图表类型
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class BaseChart:
    """图表基类"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        """创建图表 - 子类必须实现"""
        raise NotImplementedError("子类必须实现 create 方法")
    
    def get_config(self, **kwargs):
        """获取图表配置"""
        return {
            "template": "plotly_dark" if st.session_state.theme_mode == 'dark' else "plotly_white",
            "width": kwargs.get('width'),
            "height": kwargs.get('height', 500),
            "show_values": kwargs.get('show_values', False),
            "title": kwargs.get('title'),
        }


class BarChart(BaseChart):
    """柱状图"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        orientation = kwargs.get('orientation', 'v')
        color_col = kwargs.get('color')
        
        if orientation == 'h':
            fig = px.bar(
                df, y=x_col, x=y_col, color=color_col, orientation='h',
                template=config['template'], text_auto=config['show_values'],
                title=config['title'] or f'{y_col} 分布'
            )
        else:
            fig = px.bar(
                df, x=x_col, y=y_col, color=color_col,
                template=config['template'], text_auto=config['show_values'],
                title=config['title'] or f'{y_col} 分布'
            )
        
        fig.update_layout(
            width=config['width'], height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        
        if config['show_values']:
            fig.update_traces(textposition='outside', textfont_size=10)
        
        return fig


class LineChart(BaseChart):
    """折线图"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        color_col = kwargs.get('color')
        
        fig = px.line(
            df, x=x_col, y=y_col, color=color_col,
            template=config['template'], markers=True,
            title=config['title'] or f'{y_col} 趋势'
        )
        
        if config['show_values']:
            fig.update_traces(
                mode='lines+markers+text',
                text=df[y_col].round(2), textposition='top center'
            )
        
        fig.update_layout(
            width=config['width'], height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class PieChart(BaseChart):
    """饼图"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        pie_data = df.groupby(x_col)[y_col].sum().reset_index()
        hole = kwargs.get('hole', 0)
        
        fig = px.pie(
            pie_data, names=x_col, values=y_col,
            template=config['template'], hole=hole,
            title=config['title'] or f'{x_col} 分布'
        )
        fig.update_traces(
            textposition='inside', 
            textinfo='label+percent',
            textfont_size=12
        )
        
        fig.update_layout(
            width=config['width'], height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class ScatterChart(BaseChart):
    """散点图"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        color_col = kwargs.get('color')
        
        fig = px.scatter(
            df, x=x_col, y=y_col, color=color_col,
            template=config['template'],
            title=config['title'] or f'{x_col} vs {y_col}'
        )
        
        fig.update_layout(
            width=config['width'], height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class BoxChart(BaseChart):
    """箱线图"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        
        fig = px.box(
            df, x=x_col, y=y_col,
            template=config['template'],
            title=config['title'] or f'{y_col} 分布箱线图'
        )
        
        fig.update_layout(
            width=config['width'], height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class HistogramChart(BaseChart):
    """直方图"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        bins = kwargs.get('bins', 30)
        
        fig = px.histogram(
            df, x=x_col, nbins=bins,
            template=config['template'],
            title=config['title'] or f'{x_col} 分布直方图'
        )
        
        fig.update_layout(
            width=config['width'], height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class HeatmapChart(BaseChart):
    """热力图"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        
        # 如果是相关性矩阵，直接使用
        if isinstance(df, pd.DataFrame) and df.select_dtypes(include=['int64', 'float64']).shape[1] == df.shape[1]:
            corr = df
        else:
            # 否则计算相关性
            numeric_df = df.select_dtypes(include=['int64', 'float64'])
            if numeric_df.shape[1] < 2:
                return None
            corr = numeric_df.corr()
        
        show_values = kwargs.get('show_values', True)
        colorscale = kwargs.get('colorscale', 'RdBu_r')
        
        if show_values:
            fig = go.Figure(data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.index,
                colorscale=colorscale,
                text=corr.values.round(4),
                texttemplate='%{text}',
                textfont={"size": 10},
                hoverongaps=False
            ))
        else:
            fig = px.imshow(
                corr,
                text_auto=False,
                title=config['title'] or '相关性热力图',
                color_continuous_scale=colorscale
            )
        
        fig.update_layout(
            width=config['width'],
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class CompositePieChart(BaseChart):
    """复合饼图（包含四种模式）"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        mode = kwargs.get('pie_mode', '子图布局')
        
        try:
            # 获取顶层类别
            top_categories = df[x_col].value_counts().nlargest(4).index.tolist()
            
            if mode == "子图布局":
                return self._subplot_layout(df, x_col, y_col, top_categories, config)
            elif mode == "交互下钻":
                return self._drilldown_layout(df, x_col, y_col, config)
            elif mode == "复合定位":
                return self._composite_layout(df, x_col, y_col, top_categories, config)
            elif mode == "南丁格尔玫瑰图":
                return self._rose_chart(df, x_col, y_col, config)
            else:
                return None
        except Exception as e:
            st.error(f"复合饼图生成失败: {str(e)}")
            return None
    
    def _subplot_layout(self, df, category_col, value_col, top_categories, config):
        """子图布局模式"""
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'domain'}, {'type': 'domain'}],
                   [{'type': 'domain'}, {'type': 'domain'}]],
            subplot_titles=([category_col] + [f"{cat}详情" for cat in top_categories[:3]])
        )
        
        # 主图（左上）
        main_data = df.groupby(category_col)[value_col].sum().reset_index()
        fig.add_trace(
            go.Pie(labels=main_data[category_col], values=main_data[value_col], name="主图"),
            row=1, col=1
        )
        
        # 子图
        for i, category in enumerate(top_categories[:3]):
            row = 1 if i < 1 else 2
            col = 2 if i == 0 else (i % 2 + 1)
            cat_data = df[df[category_col] == category]
            if len(cat_data) > 0:
                sub_categories = cat_data.head(5)
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
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        return fig
    
    def _drilldown_layout(self, df, category_col, value_col, config):
        """交互下钻模式"""
        main_data = df.groupby(category_col)[value_col].sum().reset_index()
        
        fig = px.pie(
            main_data,
            names=category_col,
            values=value_col,
            title="点击主图区块查看详情",
            template=config['template']
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            clickmode='event+select'
        )
        return fig
    
    def _composite_layout(self, df, category_col, value_col, top_categories, config):
        """复合定位模式"""
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
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        return fig
    
    def _rose_chart(self, df, category_col, value_col, config):
        """南丁格尔玫瑰图"""
        # 聚合数据
        pie_data = df.groupby(category_col)[value_col].sum().reset_index()
        pie_data = pie_data.sort_values(value_col, ascending=False)
        
        # 创建极坐标柱状图
        fig = go.Figure()
        
        fig.add_trace(go.Barpolar(
            r=pie_data[value_col],
            theta=pie_data[category_col],
            width=[360 / len(pie_data)] * len(pie_data),
            marker=dict(
                colorscale=config.get('colorscale', 'Viridis'),
                color=pie_data[value_col],
                showscale=True,
                colorbar=dict(title=value_col)
            ),
            text=pie_data[value_col].round(2),
            textposition='outside',
            hoverinfo='theta+r+text'
        ))
        
        fig.update_layout(
            title=config['title'] or f"{value_col} 玫瑰图",
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    tickfont=dict(size=10),
                    title=value_col
                ),
                angularaxis=dict(
                    tickfont=dict(size=10),
                    rotation=90
                )
            ),
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class GroupedBarChart(BaseChart):
    """分组柱状图（支持多级分组）"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        color_col = kwargs.get('color')
        
        if color_col:
            fig = px.bar(
                df, x=x_col, y=y_col, color=color_col,
                barmode='group', template=config['template'],
                text_auto=config['show_values'],
                title=config['title'] or f'{y_col} 按 {x_col} 分组 / {color_col}'
            )
        else:
            fig = px.bar(
                df, x=x_col, y=y_col, barmode='group',
                template=config['template'], text_auto=config['show_values'],
                title=config['title'] or f'{y_col} 按 {x_col} 分组'
            )
        
        fig.update_layout(
            width=config['width'], height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        
        if config['show_values']:
            fig.update_traces(textposition='outside', textfont_size=10)
        
        return fig


class StackedBarChart(BaseChart):
    """堆积柱状图"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        color_col = kwargs.get('color')
        
        fig = px.bar(
            df, x=x_col, y=y_col, color=color_col,
            barmode='stack', template=config['template'],
            text_auto=config['show_values'],
            title=config['title'] or f'{y_col} 按 {x_col} 堆积'
        )
        
        fig.update_layout(
            width=config['width'], height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        
        if config['show_values']:
            fig.update_traces(textposition='inside', textfont_size=10)
        
        return fig


class HorizontalBarChart(BaseChart):
    """条形图（水平柱状图）"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        color_col = kwargs.get('color')
        
        fig = px.bar(
            df, y=x_col, x=y_col, color=color_col, orientation='h',
            template=config['template'], text_auto=config['show_values'],
            title=config['title'] or f'{y_col} 分布'
        )
        
        fig.update_layout(
            width=config['width'], height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        
        if config['show_values']:
            fig.update_traces(textposition='outside', textfont_size=10)
        
        return fig