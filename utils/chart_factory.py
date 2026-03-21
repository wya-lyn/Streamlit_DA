"""
图表工厂模块：统一管理所有图表类型的生成
支持动态添加新的图表类型
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class ChartFactory:
    """图表工厂类 - 统一管理图表生成"""
    
    def __init__(self):
        """初始化图表工厂，注册所有图表类型"""
        self._charts = {}  # 注册表
        self._register_default_charts()
    
    def _register_default_charts(self):
        """注册默认图表类型"""
        self.register("柱状图", BarChart())
        self.register("折线图", LineChart())
        self.register("饼图", PieChart())
        self.register("条形图", HorizontalBarChart())
        self.register("分组柱状图", GroupedBarChart())
        self.register("堆积柱状图", StackedBarChart())
        self.register("散点图", ScatterChart())
        self.register("箱线图", BoxChart())
        self.register("直方图", HistogramChart())
        self.register("热力图", HeatmapChart())
    
    def register(self, chart_type, chart_instance):
        """注册新的图表类型"""
        self._charts[chart_type] = chart_instance
        print(f"【注册】图表类型已注册: {chart_type}")
    
    def get_available_charts(self):
        """获取所有可用的图表类型"""
        return list(self._charts.keys())
    
    def create_chart(self, chart_type, df, x_col=None, y_col=None, **kwargs):
        """创建图表"""
        print(f"【调试-ChartFactory】create_chart 被调用")
        print(f"【调试-ChartFactory】chart_type: {chart_type}")
        print(f"【调试-ChartFactory】x_col: {x_col}")
        print(f"【调试-ChartFactory】y_col: {y_col}")
        print(f"【调试-ChartFactory】color: {kwargs.get('color')}")
        print(f"【调试-ChartFactory】数据形状: {df.shape}")
        print(f"【调试-ChartFactory】数据列名: {df.columns.tolist()}")
        print(f"【调试-ChartFactory】数据前5行:\n{df.head()}")
        if chart_type not in self._charts:
            st.error(f"不支持的图表类型: {chart_type}")
            return None
        
        try:
            chart = self._charts[chart_type]
            return chart.create(df, x_col, y_col, **kwargs)
        except Exception as e:
            st.error(f"图表生成失败 [{chart_type}]: {str(e)}")
            return None


class BaseChart:
    """图表基类"""
    
    def __init__(self, name="基础图表"):
        self.name = name
    
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
    
    def __init__(self):
        super().__init__("柱状图")
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        color_col = kwargs.get('color')
        
        fig = px.bar(
            df, 
            x=x_col, 
            y=y_col,
            color=color_col,
            template=config['template'],
            text_auto=config['show_values'],
            title=config['title'] or f'{y_col} 分布'
        )
        
        # 确保X轴标签显示完整
        if color_col:
            fig.update_layout(
                xaxis=dict(
                    tickangle=-45,
                    title=x_col,
                    tickfont=dict(size=10)
                ),
                legend=dict(
                    title=color_col,
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
        
        # 添加数值标签
        if config['show_values']:
            fig.update_traces(
                textposition='outside',
                textfont_size=10
            )
        
        fig.update_layout(
            width=config['width'],
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class LineChart(BaseChart):
    """折线图"""
    
    def __init__(self):
        super().__init__("折线图")
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        color_col = kwargs.get('color')
        
        fig = px.line(
            df, 
            x=x_col, 
            y=y_col,
            color=color_col,
            template=config['template'],
            markers=True,
            title=config['title'] or f'{y_col} 趋势'
        )
        
        # 确保X轴标签显示完整
        if color_col:
            fig.update_layout(
                xaxis=dict(
                    tickangle=-45,
                    title=x_col,
                    tickfont=dict(size=10)
                ),
                legend=dict(
                    title=color_col,
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
        
        if config['show_values']:
            fig.update_traces(
                mode='lines+markers+text',
                text=df[y_col].round(2),
                textposition='top center'
            )
        
        fig.update_layout(
            width=config['width'],
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class PieChart(BaseChart):
    """饼图"""
    
    def __init__(self):
        super().__init__("饼图")
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        
        # 聚合数据
        pie_data = df.groupby(x_col)[y_col].sum().reset_index()
        
        fig = px.pie(
            pie_data,
            names=x_col,
            values=y_col,
            title=config['title'] or f'{x_col} 分布',
            template=config['template'],
            hole=kwargs.get('hole', 0)
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='label+percent',
            textfont_size=12
        )
        
        fig.update_layout(
            width=config['width'],
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class HorizontalBarChart(BaseChart):
    """条形图（水平柱状图）"""
    
    def __init__(self):
        super().__init__("条形图")
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        color_col = kwargs.get('color')
        
        if color_col:
            # 多级分组条形图
            fig = px.bar(
                df,
                y=x_col,
                x=y_col,
                color=color_col,
                orientation='h',
                template=config['template'],
                text_auto=config['show_values'],
                title=config['title'] or f'{y_col} 按 {x_col} 分组 / {color_col}'
            )
            
            # 调整Y轴标签
            fig.update_layout(
                yaxis=dict(
                    title=x_col,
                    tickfont=dict(size=10)
                ),
                legend=dict(
                    title=color_col,
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
        else:
            fig = px.bar(
                df,
                y=x_col,
                x=y_col,
                orientation='h',
                template=config['template'],
                text_auto=config['show_values'],
                title=config['title'] or f'{y_col} 分布'
            )
        
        if config['show_values']:
            fig.update_traces(
                textposition='outside',
                textfont_size=10
            )
        
        fig.update_layout(
            width=config['width'],
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class GroupedBarChart(BaseChart):
    """分组柱状图（支持多级分组）"""
    
    def __init__(self):
        super().__init__("分组柱状图")
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        color_col = kwargs.get('color')
        
        # 调试信息
        print(f"【调试-GroupedBarChart】df形状: {df.shape}")
        print(f"【调试-GroupedBarChart】x_col: {x_col}")
        print(f"【调试-GroupedBarChart】y_col: {y_col}")
        print(f"【调试-GroupedBarChart】color_col: {color_col}")
        print(f"【调试-GroupedBarChart】df列名: {df.columns.tolist()}")
        
        if color_col and color_col in df.columns:
            # 确保 color_col 存在
            print(f"【调试-GroupedBarChart】color_col '{color_col}' 的值: {df[color_col].unique()[:5]}")
            
            fig = px.bar(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                barmode='group',
                template=config['template'],
                text_auto=config['show_values'] if config['show_values'] else None,
                title=config['title'] or f'{y_col} 按 {x_col} 分组 / {color_col}'
            )
            
            # 设置图例标题为第二级分组名
            fig.update_layout(
                legend_title_text=color_col,
                xaxis=dict(
                    tickangle=-45,
                    title=x_col,
                    tickfont=dict(size=10)
                )
            )
        else:
            # 单级分组或颜色列不存在
            fig = px.bar(
                df,
                x=x_col,
                y=y_col,
                barmode='group',
                template=config['template'],
                text_auto=config['show_values'] if config['show_values'] else None,
                title=config['title'] or f'{y_col} 按 {x_col} 分组'
            )
        
        # 添加数值标签
        if config['show_values']:
            fig.update_traces(
                textposition='outside',
                textfont_size=10
            )
        
        fig.update_layout(
            width=config['width'],
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
class StackedBarChart(BaseChart):
    """堆积柱状图"""
    
    def __init__(self):
        super().__init__("堆积柱状图")
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        color_col = kwargs.get('color')
        
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            barmode='stack',
            template=config['template'],
            text_auto=config['show_values'],
            title=config['title'] or f'{y_col} 按 {x_col} 堆积'
        )
        
        # 确保X轴标签显示完整
        if color_col:
            fig.update_layout(
                xaxis=dict(
                    tickangle=-45,
                    title=x_col,
                    tickfont=dict(size=10)
                ),
                legend=dict(
                    title=color_col,
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
        
        # 添加数值标签
        if config['show_values']:
            fig.update_traces(
                textposition='inside',
                textfont_size=10
            )
        
        fig.update_layout(
            width=config['width'],
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class ScatterChart(BaseChart):
    """散点图"""
    
    def __init__(self):
        super().__init__("散点图")
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=kwargs.get('color'),
            template=config['template'],
            title=config['title'] or f'{x_col} vs {y_col}'
        )
        
        fig.update_layout(
            width=config['width'],
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class BoxChart(BaseChart):
    """箱线图"""
    
    def __init__(self):
        super().__init__("箱线图")
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        
        fig = px.box(
            df,
            x=x_col,
            y=y_col,
            template=config['template'],
            title=config['title'] or f'{y_col} 分布箱线图'
        )
        
        fig.update_layout(
            width=config['width'],
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class HistogramChart(BaseChart):
    """直方图"""
    
    def __init__(self):
        super().__init__("直方图")
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        bins = kwargs.get('bins', 30)
        
        fig = px.histogram(
            df,
            x=x_col,
            nbins=bins,
            template=config['template'],
            title=config['title'] or f'{x_col} 分布直方图'
        )
        
        fig.update_layout(
            width=config['width'],
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig


class HeatmapChart(BaseChart):
    """热力图"""
    
    def __init__(self):
        super().__init__("热力图")
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
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