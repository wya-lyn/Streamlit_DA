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
    
    def get_config(self, **kwargs):
        """获取图表配置，包含主题颜色"""
        theme_mode = st.session_state.theme_mode
        
        # 根据主题动态设置颜色
        if theme_mode == 'dark':
            text_color = "#E8EDFF"      # 柔和白蓝
            title_color = "#FFFFFF"     # 纯白
            axis_color = "#9AA7C0"      # 灰蓝
            grid_color = "#2A2F3A"      # 深灰
            legend_color = "#E8EDFF"    # 柔和白蓝
        else:
            text_color = "#1A2634"      # 深灰蓝
            title_color = "#0A1A2A"     # 深黑蓝
            axis_color = "#6C7A8A"      # 中灰
            grid_color = "#E8ECF2"      # 浅灰
            legend_color = "#1A2634"    # 深灰蓝
        
        return {
            "template": "plotly_dark" if theme_mode == 'dark' else "plotly_white",
            "width": kwargs.get('width'),
            "height": kwargs.get('height', 500),
            "show_values": kwargs.get('show_values', False),
            "title": kwargs.get('title'),
            # 颜色配置
            "text_color": text_color,
            "title_color": title_color,
            "axis_color": axis_color,
            "grid_color": grid_color,
            "legend_color": legend_color,
        }
    
    def apply_theme(self, fig, config):
        """应用主题样式到图表"""
        fig.update_layout(
            # 标题样式
            title_font=dict(
                size=16,
                family="Inter, '微软雅黑', sans-serif",
                color=config['title_color']
            ),
            # 全局字体
            font=dict(
                family="Inter, '微软雅黑', sans-serif",
                size=12,
                color=config['text_color']
            ),
            # 图例样式
            legend=dict(
                font=dict(
                    size=11,
                    color=config['legend_color']
                ),
                title_font=dict(
                    size=12,
                    color=config['title_color']
                )
            ),
            # X轴样式
            xaxis=dict(
                title_font=dict(size=12, color=config['title_color']),
                tickfont=dict(size=11, color=config['axis_color']),
                gridcolor=config['grid_color'],
                gridwidth=1,
                showgrid=True
            ),
            # Y轴样式
            yaxis=dict(
                title_font=dict(size=12, color=config['title_color']),
                tickfont=dict(size=11, color=config['axis_color']),
                gridcolor=config['grid_color'],
                gridwidth=1,
                showgrid=True
            ),
            # 背景透明
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # 数据标签样式
        if config.get('show_values', False):
            fig.update_traces(
                textfont=dict(
                    size=11,
                    color=config['text_color'],
                    family="Inter, '微软雅黑', sans-serif"
                ),
                textposition='outside'
            )
        
        return fig


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
        
        # 应用统一样式
        fig = self.apply_theme(fig, config)
        
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
        
        # 应用统一样式
        fig = self.apply_theme(fig, config)
        
        if config['show_values']:
            fig.update_traces(
                mode='lines+markers+text',
                text=df[y_col].round(2),
                textposition='top center'
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
        
        # 应用统一样式
        fig = self.apply_theme(fig, config)
        
        fig.update_traces(
            textposition='inside',
            textinfo='label+percent',
            textfont_size=12
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
        
        fig = self.apply_theme(fig, config)
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
        
        fig = self.apply_theme(fig, config)
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
        
        fig = self.apply_theme(fig, config)
        return fig


class HeatmapChart(BaseChart):
    """热力图"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
        config = self.get_config(**kwargs)
        
        # 如果是相关性矩阵，直接使用
        if isinstance(df, pd.DataFrame) and df.select_dtypes(include=['int64', 'float64']).shape[1] == df.shape[1]:
            corr = df
        else:
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
        
        fig = self.apply_theme(fig, config)
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
        
        fig = self.apply_theme(fig, config)
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
        
        fig = self.apply_theme(fig, config)
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
        
        fig = self.apply_theme(fig, config)
        return fig


class CompositePieChart(BaseChart):
    """复合饼图（包含四种模式）"""
    
    def create(self, df, x_col=None, y_col=None, **kwargs):
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
        """子图布局模式"""
        if len(level_cols) < 2:
            st.warning("子图布局模式需要至少2个分类列")
            return None
        
        level1_col = level_cols[0]
        
        main_data = df.groupby(level1_col)[value_col].sum().reset_index()
        main_data = main_data.sort_values(value_col, ascending=False)
        
        fig = px.pie(
            main_data,
            names=level1_col,
            values=value_col,
            title=f"{level1_col} 分布",
            hole=0.3
        )
        
        fig = self.apply_theme(fig, config)
        print(fig.title.text + "------------------测试------------------")
        return fig
    
    def _drilldown_layout(self, df, level_cols, value_col, config):
        """交互下钻模式 - 左右布局"""
        import plotly.graph_objects as go
        
        # 获取主题颜色
        theme_mode = st.session_state.theme_mode
        text_color = "#1A2634" if theme_mode == 'light' else "#E8EDFF"
        title_color = "#0A1A2A" if theme_mode == 'light' else "#FFFFFF"
        
        # 初始化下钻状态
        if 'drilldown_path' not in st.session_state:
            st.session_state.drilldown_path = []
        if 'selected_category' not in st.session_state:
            st.session_state.selected_category = None
        
        current_path = st.session_state.drilldown_path
        current_level = len(current_path)
        
        # 根据当前路径筛选数据
        filtered_df = df.copy()
        for i, value in enumerate(current_path):
            if i < len(level_cols):
                filtered_df = filtered_df[filtered_df[level_cols[i]] == value]
        
        # 如果已经到达最深层，显示柱状图
        if current_level >= len(level_cols):
            fig = self._create_value_chart(filtered_df, value_col, current_path, level_cols, config)
            st.plotly_chart(fig, use_container_width=True)
            self._add_drilldown_controls(current_path, level_cols)
            return go.Figure()
        
        current_col = level_cols[current_level]
        next_col = level_cols[current_level + 1] if current_level + 1 < len(level_cols) else None
        max_categories = config.get('max_categories', 10)
        
        # 聚合当前层级数据
        current_data = filtered_df.groupby(current_col)[value_col].sum().reset_index()
        current_data = current_data.sort_values(value_col, ascending=False)
        
        if len(current_data) > max_categories:
            other_sum = current_data.iloc[max_categories:][value_col].sum()
            current_data = current_data.head(max_categories)
            if other_sum > 0:
                current_data = pd.concat([
                    current_data,
                    pd.DataFrame({current_col: ['其他'], value_col: [other_sum]})
                ], ignore_index=True)
        
        # 格式化当前层级数值
        total_current = current_data[value_col].sum()
        current_data['percent'] = (current_data[value_col] / total_current * 100).round(1)
        if config.get('format_numbers', True):
            current_data['formatted'] = current_data[value_col].apply(self._format_number)
        else:
            current_data['formatted'] = current_data[value_col].round(2)
        
        # 确定选中的类别
        if st.session_state.selected_category is None or st.session_state.selected_category not in current_data[current_col].tolist():
            st.session_state.selected_category = current_data.iloc[0][current_col]
        
        selected = st.session_state.selected_category
        
        # 左右布局
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### 📊 当前层级：{current_col}")
            
            if len(current_data) == 1:
                st.info(f"📊 {current_col} 只有一项：{current_data[current_col].iloc[0]} ({current_data['formatted'].iloc[0]})")
            else:
                legend_labels = current_data[current_col].tolist()
                
                
                fig = go.Figure(data=[go.Pie(
                    labels=legend_labels,
                    values=current_data[value_col].tolist(),
                    hole=0.3,
                    textinfo='none',
                    hoverinfo='label+percent+value',
                    marker=dict(line=dict(color='#000000', width=1))
                )])
                
                fig.update_traces(
                    textinfo='label+value+percent',
                    textposition='inside',
                    textfont=dict(size=11, color=text_color)
                )
                # 构建路径字符串（只显示具体值，不显示字段名）
                path_values = " → ".join(current_path) if current_path else ""

                # 主图标题
                if current_path:
                    main_title = f"{path_values} 的 {current_col} {value_col}"
                else:
                    main_title = f"{current_col} {value_col}"
                
                fig.update_layout(
                    title={
                    'text': main_title,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': dict(size=16, color=title_color)
                },
                    font=dict(size=12, color=text_color),
                    legend=dict(font=dict(size=11, color=text_color)),
                    height=450,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=50, b=20)  # 顶部留出标题空间
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("**选择类别查看下级分布：**")
            cols = st.columns(min(len(current_data), 4))
            for i, cat in enumerate(current_data[current_col].tolist()):
                with cols[i % len(cols)]:
                    if st.button(cat, key=f"select_{cat}_{current_level}"):
                        print(f"【调试】current_col: {current_col}")
                        print(f"【调试】current_col 类型: {type(current_col)}")
                        print(f"【调试】current_col 是否为 None: {current_col is None}")
                        st.session_state.selected_category = cat
                        st.rerun()
        
        with col2:
            if next_col is not None:
                st.markdown(f"### 🔽 下级预览：{selected} 的 {next_col}")
                
                next_df = filtered_df[filtered_df[current_col] == selected]
                next_data = next_df.groupby(next_col)[value_col].sum().reset_index()
                next_data = next_data.sort_values(value_col, ascending=False)
                
                if len(next_data) > max_categories:
                    other_sum = next_data.iloc[max_categories:][value_col].sum()
                    next_data = next_data.head(max_categories)
                    if other_sum > 0:
                        next_data = pd.concat([
                            next_data,
                            pd.DataFrame({next_col: ['其他'], value_col: [other_sum]})
                        ], ignore_index=True)
                
                if len(next_data) > 0:
                    total_next = next_data[value_col].sum()
                    percentages = (next_data[value_col] / total_next * 100).round(1)
                    if config.get('format_numbers', True):
                        formatted_values = next_data[value_col].apply(self._format_number)
                    else:
                        formatted_values = next_data[value_col].round(2)
                    
                    if len(next_data) == 1:
                        st.info(f"📊 {next_col} 只有一项：{next_data[next_col].iloc[0]} ({formatted_values.iloc[0]})")
                    else:
                        legend_labels = next_data[next_col].tolist()
                        
                        fig = go.Figure(data=[go.Pie(
                            labels=legend_labels,
                            values=next_data[value_col].tolist(),
                            hole=0.3,
                            textinfo='none',
                            hoverinfo='label+percent+value',
                            marker=dict(line=dict(color='#000000', width=1))
                        )])
                        
                        fig.update_traces(
                            textinfo='label+value+percent',
                            textposition='inside',
                            textfont=dict(size=11, color=text_color)
                        )
                        # 子图标题
                        sub_title = f"{path_values} → {selected} 的 {next_col} {value_col}" if current_path else f"{selected} 的 {next_col} {value_col}"
                        
                        fig.update_layout(
                             title={
                                'text':sub_title,
                                'x': 0.5,
                                'xanchor': 'center',
                                'font': dict(size=16, color=title_color)
                            },
                            font=dict(size=12, color=text_color),
                            legend=dict(font=dict(size=11, color=text_color)),
                            height=450,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=20, r=20, t=50, b=20)  # 顶部留出标题空间
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    if st.button(f"🔽 下钻到 {selected}", key=f"drilldown_{selected}"):
                        st.session_state.drilldown_path.append(selected)
                        st.session_state.selected_category = None
                        st.rerun()
                else:
                    st.info(f"{selected} 没有下级数据")
            else:
                st.info("已到达最深层，无法继续下钻")
        
        self._add_drilldown_controls(current_path, level_cols)
        return go.Figure()
    
    def _composite_layout(self, df, level_cols, value_col, config):
        """复合定位模式"""
        if len(level_cols) < 2:
            st.warning("复合定位模式需要至少2个分类列")
            return None
        
        level1_col = level_cols[0]
        
        main_data = df.groupby(level1_col)[value_col].sum().reset_index()
        main_data = main_data.sort_values(value_col, ascending=False)
        
        fig = px.pie(
            main_data,
            names=level1_col,
            values=value_col,
            title=f"{level1_col} 分布",
            hole=0.3
        )
        
        fig = self.apply_theme(fig, config)
        return fig
    
    def _rose_chart(self, df, category_col, value_col, config):
        """南丁格尔玫瑰图"""
        pie_data = df.groupby(category_col)[value_col].sum().reset_index()
        pie_data = pie_data.sort_values(value_col, ascending=False)
        
        max_categories = config.get('max_categories', 10)
        if len(pie_data) > max_categories:
            other_sum = pie_data.iloc[max_categories:][value_col].sum()
            pie_data = pie_data.head(max_categories)
            if other_sum > 0:
                pie_data = pd.concat([
                    pie_data,
                    pd.DataFrame({category_col: ['其他'], value_col: [other_sum]})
                ], ignore_index=True)
        
        fig = px.bar_polar(
            pie_data,
            r=value_col,
            theta=category_col,
            color=value_col,
            color_continuous_scale=config.get('colorscale', 'Viridis'),
            title=config['title'] or f"{value_col} 玫瑰图"
        )
        
        fig = self.apply_theme(fig, config)
        return fig
    
    def _create_value_chart(self, df, value_col, path, level_cols, config):
        """最终层：显示数值分布柱状图"""
        import plotly.graph_objects as go
        
        # 获取主题颜色
        theme_mode = st.session_state.theme_mode
        text_color = "#1A2634" if theme_mode == 'light' else "#E8EDFF"
        title_color = "#0A1A2A" if theme_mode == 'light' else "#FFFFFF"
        axis_color = "#6C7A8A" if theme_mode == 'light' else "#9AA7C0"
        grid_color = "#E8ECF2" if theme_mode == 'light' else "#2A2F3A"
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(text="无数据", x=0.5, y=0.5, showarrow=False)
        else:
            current_level = len(path)
            if current_level < len(level_cols):
                category_col = level_cols[current_level]
            else:
                category_col = level_cols[-1] if level_cols else "分类"
            
            chart_data = df.groupby(category_col)[value_col].sum().reset_index()
            chart_data = chart_data.sort_values(value_col, ascending=False)
            
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
            
            if config.get('format_numbers', True):
                formatted_values = chart_data[value_col].apply(self._format_number)
            else:
                formatted_values = chart_data[value_col].round(2)
            
            percentages = (chart_data[value_col] / total * 100).round(1)
            
            labels = [f"{val}<br>({pct}%)" for val, pct in zip(formatted_values, percentages)]
            
            fig = go.Figure(data=[go.Bar(
                x=chart_data[category_col],
                y=chart_data[value_col],
                text=labels,
                textposition='outside',
                textfont=dict(size=10, color=text_color)
            )])
            
            fig.update_layout(
                title=f"{' > '.join(path)} 的详细分布 (总计: {self._format_number(total)})",
                title_font=dict(size=16, color=title_color),
                font=dict(size=12, color=text_color),
                xaxis=dict(
                    title=category_col,
                    title_font=dict(size=12, color=title_color),
                    tickfont=dict(size=11, color=axis_color),
                    tickangle=-45,
                    gridcolor=grid_color
                ),
                yaxis=dict(
                    title=value_col,
                    title_font=dict(size=12, color=title_color),
                    tickfont=dict(size=11, color=axis_color),
                    gridcolor=grid_color,
                    showgrid=True
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=450
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
    
    def _get_breadcrumb(self, path, level_cols):
        """获取面包屑导航"""
        print(f"【调试】_get_breadcrumb 被调用")
        print(f"【调试】path: {path}")
        print(f"【调试】level_cols: {level_cols}")
        
        if not path:
            result = "当前：顶层"
            print(f"【调试】返回: {result}")
            return result
        
        breadcrumb = []
        for i, val in enumerate(path):
            if i < len(level_cols):
                breadcrumb.append(f"{level_cols[i]}: {val}")
        
        result = " → ".join(breadcrumb)
        print(f"【调试】返回: {result}")
        return result
    
    def _add_drilldown_controls(self, path, level_cols):
        """添加下钻控制按钮"""
        if path:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔙 返回上一级", key="drillback_btn", use_container_width=True):
                    st.session_state.drilldown_path.pop()
                    st.session_state.selected_category = None
                    st.rerun()
            st.caption(f"📍 当前位置：{self._get_breadcrumb(path, level_cols)}")
            print(f"📍 当前位置：{self._get_breadcrumb(path, level_cols)}")