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
        """创建复合饼图"""
        config = self.get_config(**kwargs)
        mode = kwargs.get('pie_mode', '子图布局')
        
        # 获取参数
        level_cols = kwargs.get('level_cols', [])
        value_col = kwargs.get('value_col')
        
        # 兼容旧接口
        if not level_cols and x_col and y_col:
            level_cols = [x_col, y_col]
        
        if value_col is None:
            st.error("请指定数值列")
            return None
        
        if not level_cols:
            st.error("请至少指定一个分类列")
            return None
        
        try:
            if mode == "子图布局":
                return self._subplot_layout(df, level_cols, value_col, config)
            elif mode == "交互下钻":
                return self._drilldown_layout(df, level_cols, value_col, config)
            elif mode == "复合定位":
                return self._composite_layout(df, level_cols, value_col, config)
            elif mode == "南丁格尔玫瑰图":
                return self._rose_chart(df, level_cols[0], value_col, config)
            else:
                return None
        except Exception as e:
            st.error(f"复合饼图生成失败: {str(e)}")
            return None
    
    def _subplot_layout(self, df, level_cols, value_col, config):
        """子图布局模式（支持2级）"""
        from plotly.subplots import make_subplots
        import plotly.graph_objects as go
        
        if len(level_cols) < 2:
            st.warning("子图布局模式需要至少2个分类列")
            return None
        
        level1_col = level_cols[0]
        level2_col = level_cols[1]
        
        # 获取第一级顶层类别
        top_categories = df[level1_col].value_counts().nlargest(4).index.tolist()
        
        # 主图：第一级分布
        main_data = df.groupby(level1_col)[value_col].sum().reset_index()
        
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'domain'}, {'type': 'domain'}],
                   [{'type': 'domain'}, {'type': 'domain'}]],
            subplot_titles=([level1_col] + [f"{cat} - {level2_col}" for cat in top_categories[:3]])
        )
        
        # 主图（左上）
        fig.add_trace(
            go.Pie(labels=main_data[level1_col], values=main_data[value_col], name="主图"),
            row=1, col=1
        )
        
        # 子图：每个第一级类别下的第二级分布
        for i, category in enumerate(top_categories[:3]):
            row = 1 if i < 1 else 2
            col = 2 if i == 0 else (i % 2 + 1)
            cat_data = df[df[level1_col] == category]
            if len(cat_data) > 0:
                sub_data = cat_data.groupby(level2_col)[value_col].sum().reset_index()
                fig.add_trace(
                    go.Pie(
                        labels=sub_data[level2_col],
                        values=sub_data[value_col],
                        name=f"{category}详情"
                    ),
                    row=row, col=col
                )
        
        fig.update_layout(
            title_text=f"复合饼图 - {level1_col} → {level2_col}",
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        return fig
    
    def _drilldown_layout(self, df, level_cols, value_col, config):
        """交互下钻模式 - 支持无限级递归下钻"""
        import plotly.graph_objects as go
        
        # 调试信息
        print(f"【调试】_drilldown_layout 被调用")
        print(f"【调试】level_cols: {level_cols}")
        print(f"【调试】value_col: {value_col}")
        
        # 初始化下钻状态
        if 'drilldown_path' not in st.session_state:
            st.session_state.drilldown_path = []
            print("【调试】初始化 drilldown_path")
        
        current_path = st.session_state.drilldown_path
        current_level = len(current_path)
        
        print(f"【调试】current_path: {current_path}")
        print(f"【调试】current_level: {current_level}")
        print(f"【调试】总层级数: {len(level_cols)}")
        
        # 根据当前路径筛选数据
        filtered_df = df.copy()
        for i, value in enumerate(current_path):
            if i < len(level_cols):
                filtered_df = filtered_df[filtered_df[level_cols[i]] == value]
                print(f"【调试】筛选后行数: {len(filtered_df)}")
        
        # 当前要显示的层级
        if current_level >= len(level_cols):
            print("【调试】没有更多层级，显示数值分布")
            fig = self._create_value_chart(filtered_df, value_col, current_path, level_cols, config)
            self._add_drilldown_controls(current_path, level_cols)
            return fig
        
        current_col = level_cols[current_level]
        print(f"【调试】当前层级列: {current_col}")
        
        # 聚合当前层级数据
        chart_data = filtered_df.groupby(current_col)[value_col].sum().reset_index()
        chart_data = chart_data.sort_values(value_col, ascending=False)
        print(f"【调试】聚合后行数: {len(chart_data)}")
        
        # 限制显示数量
        max_categories = config.get('max_categories', 10)
        if len(chart_data) > max_categories:
            other_sum = chart_data.iloc[max_categories:][value_col].sum()
            chart_data = chart_data.head(max_categories)
            if other_sum > 0:
                chart_data = pd.concat([
                    chart_data,
                    pd.DataFrame({current_col: ['其他'], value_col: [other_sum]})
                ], ignore_index=True)
        
        # 格式化数值
        if config.get('format_numbers', True):
            chart_data['formatted'] = chart_data[value_col].apply(self._format_number)
        else:
            chart_data['formatted'] = chart_data[value_col].round(2)
        
        # 计算百分比
        total = chart_data[value_col].sum()
        chart_data['percent'] = (chart_data[value_col] / total * 100).round(1)
        
        # 创建饼图标签
        labels = [f"{name}<br>{val}<br>({pct}%)" 
                for name, val, pct in zip(chart_data[current_col], chart_data['formatted'], chart_data['percent'])]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=chart_data[value_col],
            hole=0.3 if current_path else 0,
            textinfo='none',
            hoverinfo='label+percent+value'
        )])
        
        fig.update_layout(
            title=self._get_title(current_path, current_col, total, config),
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        # 添加下钻控件
        self._add_drilldown_controls(current_path, level_cols)
        
        # 添加下钻选择器（如果有下级）
        if len(chart_data) > 0 and current_level + 1 < len(level_cols):
            st.markdown("---")
            st.markdown("### 🔽 下钻操作")
            
            # 使用 unique key
            selected = st.selectbox(
                "选择要下钻的类别：",
                chart_data[current_col].tolist(),
                key=f"drilldown_select_{current_level}_{len(current_path)}"
            )
            
            if st.button("下钻查看详情", key=f"drilldown_btn_{current_level}_{len(current_path)}", use_container_width=True):
                st.session_state.drilldown_path.append(selected)
                st.rerun()
        
        return fig
    
    def _composite_layout(self, df, level_cols, value_col, config):
        """复合定位模式（支持2级）"""
        import plotly.graph_objects as go
        
        if len(level_cols) < 2:
            st.warning("复合定位模式需要至少2个分类列")
            return None
        
        level1_col = level_cols[0]
        level2_col = level_cols[1]
        
        # 获取第一级顶层类别
        top_categories = df[level1_col].value_counts().nlargest(4).index.tolist()
        
        # 主图（居中偏上）
        main_data = df.groupby(level1_col)[value_col].sum().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=main_data[level1_col],
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
            cat_data = df[df[level1_col] == category]
            if len(cat_data) > 0 and i < len(positions):
                sub_data = cat_data.groupby(level2_col)[value_col].sum().reset_index()
                fig.add_trace(go.Pie(
                    labels=sub_data[level2_col],
                    values=sub_data[value_col],
                    domain=positions[i],
                    name=f"{category}详情"
                ))
        
        fig.update_layout(
            title_text=f"复合饼图 - {level1_col} → {level2_col}",
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        return fig
    
    def _rose_chart(self, df, category_col, value_col, config):
        """南丁格尔玫瑰图"""
        import plotly.graph_objects as go
        
        # 聚合数据
        pie_data = df.groupby(category_col)[value_col].sum().reset_index()
        pie_data = pie_data.sort_values(value_col, ascending=False)
        
        # 限制显示数量
        max_categories = config.get('max_categories', 10)
        if len(pie_data) > max_categories:
            other_sum = pie_data.iloc[max_categories:][value_col].sum()
            pie_data = pie_data.head(max_categories)
            if other_sum > 0:
                pie_data = pd.concat([
                    pie_data,
                    pd.DataFrame({category_col: ['其他'], value_col: [other_sum]})
                ], ignore_index=True)
        
        # 格式化数值
        if config.get('format_numbers', True):
            formatted_values = pie_data[value_col].apply(self._format_number)
        else:
            formatted_values = pie_data[value_col].round(2)
        
        # 计算百分比
        total = pie_data[value_col].sum()
        percentages = (pie_data[value_col] / total * 100).round(1)
        
        # 创建极坐标柱状图（移除 textposition）
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
            text=[f"{val}<br>({pct}%)" for val, pct in zip(formatted_values, percentages)],
            hoverinfo='theta+r+text',
            hovertemplate='%{theta}<br>数值: %{r}<br>占比: %{text}<extra></extra>'
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

    def _create_value_chart(self, df, value_col, path, level_cols, config):
        """最终层：显示数值分布柱状图"""
        import plotly.graph_objects as go
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(text="无数据", x=0.5, y=0.5, showarrow=False)
        else:
            # 当前层级的分类列
            current_level = len(path)
            if current_level < len(level_cols):
                category_col = level_cols[current_level]
            else:
                category_col = level_cols[-1] if level_cols else "分类"
            
            # 聚合数据
            chart_data = df.groupby(category_col)[value_col].sum().reset_index()
            chart_data = chart_data.sort_values(value_col, ascending=False)
            
            # 限制显示数量
            max_categories = config.get('max_categories', 10)
            if len(chart_data) > max_categories:
                other_sum = chart_data.iloc[max_categories:][value_col].sum()
                chart_data = chart_data.head(max_categories)
                if other_sum > 0:
                    chart_data = pd.concat([
                        chart_data,
                        pd.DataFrame({category_col: ['其他'], value_col: [other_sum]})
                    ], ignore_index=True)
            
            total = chart_data[value_col].sum()
            
            # 格式化数值
            if config.get('format_numbers', True):
                formatted_values = chart_data[value_col].apply(self._format_number)
            else:
                formatted_values = chart_data[value_col].round(2)
            
            # 计算百分比
            percentages = (chart_data[value_col] / total * 100).round(1)
            
            # 构建标签
            labels = [f"{val}<br>({pct}%)" for val, pct in zip(formatted_values, percentages)]
            
            fig = go.Figure(data=[go.Bar(
                x=chart_data[category_col],
                y=chart_data[value_col],
                text=labels,
                textposition='outside',
                textfont=dict(size=10)
            )])
            
            fig.update_layout(
                title=f"{' > '.join(path)} 的详细分布 (总计: {self._format_number(total)})",
                xaxis_title=category_col,
                yaxis_title=value_col,
                xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
                yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
            )
        
        fig.update_layout(
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def _format_number(self, num):
        """格式化数值（万/亿）"""
        if num >= 1e8:
            return f"{num/1e8:.2f}亿"
        elif num >= 1e4:
            return f"{num/1e4:.2f}万"
        else:
            return f"{num:.2f}"
    
    def _get_title(self, path, current_col, total, config):
        """获取图表标题"""
        if path:
            path_str = " > ".join(path)
            return f"{path_str} 的 {current_col} 分布 (总计: {self._format_number(total)})"
        else:
            return f"{current_col} 分布 (总计: {self._format_number(total)})"
    
    def _get_breadcrumb(self, path, level_cols):
        """获取面包屑导航"""
        if not path:
            return "当前：顶层"
        breadcrumb = []
        for i, val in enumerate(path):
            if i < len(level_cols):
                breadcrumb.append(f"{level_cols[i]}: {val}")
        return " → ".join(breadcrumb)
    
    def _add_drilldown_controls(self, path, level_cols):
        """添加下钻控制按钮"""
        if path:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔙 返回上一级", key="drillback_btn", use_container_width=True):
                    st.session_state.drilldown_path.pop()
                    st.rerun()
            st.caption(f"📍 当前位置：{self._get_breadcrumb(path, level_cols)}")
            
    
    def _create_value_chart(self, df, value_col, path, level_cols, config):
        """最终层：显示数值分布柱状图"""
        import plotly.graph_objects as go
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(text="无数据", x=0.5, y=0.5, showarrow=False)
        else:
            # 当前层级的分类列
            current_level = len(path)
            if current_level < len(level_cols):
                category_col = level_cols[current_level]
            else:
                category_col = level_cols[-1] if level_cols else "分类"
            
            # 聚合数据
            chart_data = df.groupby(category_col)[value_col].sum().reset_index()
            chart_data = chart_data.sort_values(value_col, ascending=False)
            
            # 限制显示数量
            max_categories = config.get('max_categories', 10)
            if len(chart_data) > max_categories:
                other_sum = chart_data.iloc[max_categories:][value_col].sum()
                chart_data = chart_data.head(max_categories)
                if other_sum > 0:
                    chart_data = pd.concat([
                        chart_data,
                        pd.DataFrame({category_col: ['其他'], value_col: [other_sum]})
                    ], ignore_index=True)
            
            total = chart_data[value_col].sum()
            
            # 格式化数值
            if config.get('format_numbers', True):
                formatted_values = chart_data[value_col].apply(self._format_number)
            else:
                formatted_values = chart_data[value_col].round(2)
            
            # 计算百分比
            percentages = (chart_data[value_col] / total * 100).round(1)
            
            # 构建标签
            labels = [f"{val}<br>({pct}%)" for val, pct in zip(formatted_values, percentages)]
            
            fig = go.Figure(data=[go.Bar(
                x=chart_data[category_col],
                y=chart_data[value_col],
                text=labels,
                textposition='outside',
                textfont=dict(size=10)
            )])
            
            fig.update_layout(
                title=f"{' > '.join(path)} 的详细分布 (总计: {self._format_number(total)})",
                xaxis_title=category_col,
                yaxis_title=value_col,
                xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
                yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)')
            )
        
        fig.update_layout(
            height=config['height'],
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def _format_number(self, num):
        """格式化数值（万/亿）"""
        if num >= 1e8:
            return f"{num/1e8:.2f}亿"
        elif num >= 1e4:
            return f"{num/1e4:.2f}万"
        else:
            return f"{num:.2f}"
    
    def _get_title(self, path, current_col, total, config):
        """获取图表标题"""
        if path:
            path_str = " > ".join(path)
            return f"{path_str} 的 {current_col} 分布 (总计: {self._format_number(total)})"
        else:
            return f"{current_col} 分布 (总计: {self._format_number(total)})"
    
    def _get_breadcrumb(self, path, level_cols):
        """获取面包屑导航"""
        if not path:
            return "当前：顶层"
        breadcrumb = []
        for i, val in enumerate(path):
            if i < len(level_cols):
                breadcrumb.append(f"{level_cols[i]}: {val}")
        return " → ".join(breadcrumb)
    
    def _add_drilldown_controls(self, path, level_cols):
        """添加下钻控制按钮"""
        if path:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔙 返回上一级", key="drillback_btn", use_container_width=True):
                    st.session_state.drilldown_path.pop()
                    st.rerun()
            st.caption(f"📍 当前位置：{self._get_breadcrumb(path, level_cols)}")


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