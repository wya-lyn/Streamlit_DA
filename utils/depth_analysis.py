"""
深度分析模块：支持下钻的多种图表类型
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class ChartRenderer:
    """图表渲染器基类"""
    
    def __init__(self, chart_type):
        self.chart_type = chart_type
    
    def render(self, df, x_col, y_col, title, config):
        """渲染图表 - 子类实现"""
        raise NotImplementedError


class PieChartRenderer(ChartRenderer):
    """饼图渲染器"""
        
    def render(self, df, x_col, y_col, title, config):
        # 获取主题颜色
        theme_mode = st.session_state.theme_mode
        text_color = "#1A2634" if theme_mode == 'light' else "#E8EDFF"
        
        # 计算百分比
        total = df[y_col].sum()
        percentages = (df[y_col] / total * 100).round(1)
        
        # 格式化数值
        if config.get('format_numbers', True):
            formatted_values = df[y_col].apply(self._format_number)
        else:
            formatted_values = df[y_col].round(2)
        
        # 扇区标签：类别名称 + 数值 + 百分比
        sector_labels = [f"{name}<br>{val}<br>({pct}%)" 
                         for name, val, pct in zip(df[x_col], formatted_values, percentages)]
        
        fig = go.Figure(data=[go.Pie(
            labels=sector_labels,           # 扇区显示完整信息
            values=df[y_col],
            hole=0.3,
            textinfo='none',                # 使用自定义labels
            hoverinfo='label+percent+value',
            marker=dict(line=dict(color='#000000', width=1))
        )])
        
        # 图例：只显示类别名称
        fig.update_layout(
            showlegend=True,
            legend=dict(
                title=x_col,
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color=text_color)
            )
        )
        
        return fig
    
    def _format_number(self, num):
        if num >= 1e8:
            return f"{num/1e8:.2f}亿"
        elif num >= 1e4:
            return f"{num/1e4:.2f}万"
        else:
            return f"{num:.2f}"


class BarChartRenderer(ChartRenderer):
    """柱状图渲染器"""
    
    def render(self, df, x_col, y_col, title, config):
        # 获取主题颜色
        theme_mode = st.session_state.theme_mode
        text_color = "#1A2634" if theme_mode == 'light' else "#E8EDFF"
        
        # 区分正负值颜色
        df['color'] = df[y_col].apply(lambda x: '#FF6B6B' if x < 0 else '#6A4E9B')
        
        fig = go.Figure(data=[go.Bar(
            x=df[x_col],
            y=df[y_col],
            marker_color=df['color'],
            text=df[y_col].round(2),
            textposition='outside',
            textfont=dict(size=10, color=text_color)
        )])
        
        fig.update_layout(
            xaxis=dict(tickangle=-45),
            yaxis=dict(title=y_col)
        )
        
        return fig


class HorizontalBarChartRenderer(ChartRenderer):
    """条形图渲染器（水平柱状图）"""
    
    def render(self, df, x_col, y_col, title, config):
        theme_mode = st.session_state.theme_mode
        text_color = "#1A2634" if theme_mode == 'light' else "#E8EDFF"
        
        df['color'] = df[y_col].apply(lambda x: '#FF6B6B' if x < 0 else '#6A4E9B')
        
        fig = go.Figure(data=[go.Bar(
            y=df[x_col],
            x=df[y_col],
            orientation='h',
            marker_color=df['color'],
            text=df[y_col].round(2),
            textposition='outside',
            textfont=dict(size=10, color=text_color)
        )])
        
        fig.update_layout(
            xaxis=dict(title=y_col),
            yaxis=dict(title=x_col)
        )
        
        return fig


class LineChartRenderer(ChartRenderer):
    """折线图渲染器"""
    
    def render(self, df, x_col, y_col, title, config):
        theme_mode = st.session_state.theme_mode
        text_color = "#1A2634" if theme_mode == 'light' else "#E8EDFF"
        
        fig = go.Figure(data=[go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='lines+markers+text',
            text=df[y_col].round(2),
            textposition='top center',
            textfont=dict(size=10, color=text_color),
            line=dict(color='#6A4E9B', width=2),
            marker=dict(size=8, color='#6A4E9B')
        )])
        
        fig.update_layout(
            xaxis=dict(tickangle=-45),
            yaxis=dict(title=y_col)
        )
        
        return fig


class DepthAnalysisEngine:
    """深度分析引擎 - 支持下钻的图表"""
    
    def __init__(self):
        # 注册图表渲染器
        self.renderers = {
            "饼图": PieChartRenderer("饼图"),
            "柱状图": BarChartRenderer("柱状图"),
            "条形图": HorizontalBarChartRenderer("条形图"),
            "折线图": LineChartRenderer("折线图"),
        }
    
    def render(self, df, level_cols, value_col, chart_type, config):
    
        # 获取主题颜色
        theme_mode = st.session_state.theme_mode
        text_color = "#1A2634" if theme_mode == 'light' else "#E8EDFF"
        title_color = "#0A1A2A" if theme_mode == 'light' else "#FFFFFF"
        
        # 初始化下钻状态
        if 'depth_path' not in st.session_state:
            st.session_state.depth_path = []
        if 'depth_selected' not in st.session_state:
            st.session_state.depth_selected = None
        
        current_path = st.session_state.depth_path
        current_level = len(current_path)
        
        # 筛选数据
        filtered_df = df.copy()
        for i, value in enumerate(current_path):
            if i < len(level_cols):
                filtered_df = filtered_df[filtered_df[level_cols[i]] == value]
        
        # 到达最深层，显示详细数据
        if current_level >= len(level_cols):
            self._show_detail_table(filtered_df, value_col, current_path, level_cols, config)
            self._add_controls(current_path, level_cols)
            return
        
        current_col = level_cols[current_level]
        next_col = level_cols[current_level + 1] if current_level + 1 < len(level_cols) else None
        max_categories = config.get('max_categories', 10)
        
        # 聚合当前层级数据
        current_data = filtered_df.groupby(current_col)[value_col].sum().reset_index()
        current_data = current_data.sort_values(value_col, ascending=False)
        
        # 限制显示数量
        if len(current_data) > max_categories:
            other_sum = current_data.iloc[max_categories:][value_col].sum()
            current_data = current_data.head(max_categories)
            if other_sum != 0:
                current_data = pd.concat([
                    current_data,
                    pd.DataFrame({current_col: ['其他'], value_col: [other_sum]})
                ], ignore_index=True)
        
        # 确定选中的类别
        if st.session_state.depth_selected is None or st.session_state.depth_selected not in current_data[current_col].tolist():
            st.session_state.depth_selected = current_data.iloc[0][current_col]
        
        selected = st.session_state.depth_selected
        
        # 左右布局
        col1, col2 = st.columns(2)
        
        # 左侧：当前层级图表
        with col1:
            st.markdown(f"### 📊 当前层级：{current_col}")
            
            # 构建标题
            path_values = " → ".join(current_path) if current_path else ""
            if current_path:
                main_title = f"{path_values} 的 {current_col} {value_col}"
            else:
                main_title = f"{current_col} {value_col}"
            
            # ========== 根据图表类型选择显示方式 ==========
            if chart_type == "饼图":
                # 直接使用旧版本的饼图代码（已验证可用）
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
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                # 其他图表类型使用渲染器
                renderer = self.renderers.get(chart_type)
                if renderer is None:
                    st.error(f"不支持的图表类型: {chart_type}")
                    return
                
                fig = renderer.render(current_data, current_col, value_col, main_title, config)
                
                fig.update_layout(
                    title={
                        'text': main_title,
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': dict(size=16, color=title_color)
                    },
                    font=dict(size=12, color=text_color),
                    height=450,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # 类别选择按钮
            st.markdown("**选择类别查看下级分布：**")
            cols = st.columns(min(len(current_data), 4))
            for i, cat in enumerate(current_data[current_col].tolist()):
                with cols[i % len(cols)]:
                    if st.button(cat, key=f"depth_select_{cat}_{current_level}"):
                        st.session_state.depth_selected = cat
                        st.rerun()
        
        # 右侧：下一层级预览
        with col2:
            if next_col is not None:
                st.markdown(f"### 🔽 下级预览：{selected} 的 {next_col}")
                
                next_df = filtered_df[filtered_df[current_col] == selected]
                next_data = next_df.groupby(next_col)[value_col].sum().reset_index()
                next_data = next_data.sort_values(value_col, ascending=False)
                
                if len(next_data) > max_categories:
                    other_sum = next_data.iloc[max_categories:][value_col].sum()
                    next_data = next_data.head(max_categories)
                    if other_sum != 0:
                        next_data = pd.concat([
                            next_data,
                            pd.DataFrame({next_col: ['其他'], value_col: [other_sum]})
                        ], ignore_index=True)
                
                if len(next_data) > 0:
                    # 构建子图标题
                    sub_title = f"{path_values} → {selected} 的 {next_col} {value_col}" if current_path else f"{selected} 的 {next_col} {value_col}"
                    
                    # 根据图表类型选择显示方式
                    if chart_type == "饼图":
                        # 饼图使用旧版本代码
                        legend_labels = next_data[next_col].tolist()
                        
                        sub_fig = go.Figure(data=[go.Pie(
                            labels=legend_labels,
                            values=next_data[value_col].tolist(),
                            hole=0.3,
                            textinfo='none',
                            hoverinfo='label+percent+value',
                            marker=dict(line=dict(color='#000000', width=1))
                        )])
                        
                        sub_fig.update_traces(
                            textinfo='label+value+percent',
                            textposition='inside',
                            textfont=dict(size=11, color=text_color)
                        )
                        
                    else:
                        # 其他图表类型使用渲染器
                        renderer = self.renderers.get(chart_type)
                        if renderer:
                            sub_fig = renderer.render(next_data, next_col, value_col, sub_title, config)
                        else:
                            sub_fig = None
                    
                    if sub_fig:
                        sub_fig.update_layout(
                            title={
                                'text': sub_title,
                                'x': 0.5,
                                'xanchor': 'center',
                                'font': dict(size=16, color=title_color)
                            },
                            font=dict(size=12, color=text_color),
                            height=450,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=20, r=20, t=50, b=20)
                        )
                        
                        st.plotly_chart(sub_fig, use_container_width=True)
                    
                    # ========== 下钻按钮（缩进正确：在 if len(next_data) > 0 内，与 if sub_fig 同级）==========
                    st.markdown("---")

                    if st.button(f"🔽 下钻到 {selected}"):
                        st.session_state.depth_path.append(selected)
                        st.session_state.depth_selected = None
                        st.rerun()
                else:
                    st.info(f"{selected} 没有下级数据")
            else:
                st.info("已到达最深层，无法继续下钻")
                
                # 添加返回控件
                self._add_controls(current_path, level_cols)
                

    
    def _show_detail_table(self, df, value_col, path, level_cols, config):
        """显示详细数据表（最深层）"""
        if df.empty:
            st.info("无数据")
            return
        
        current_level = len(path)
        if current_level < len(level_cols):
            category_col = level_cols[current_level]
        else:
            category_col = level_cols[-1] if level_cols else "分类"
        
        detail_data = df.groupby(category_col)[value_col].sum().reset_index()
        detail_data = detail_data.sort_values(value_col, ascending=False)
        
        max_categories = config.get('max_categories', 10)
        if len(detail_data) > max_categories:
            other_sum = detail_data.iloc[max_categories:][value_col].sum()
            detail_data = detail_data.head(max_categories)
            if other_sum != 0:
                detail_data = pd.concat([
                    detail_data,
                    pd.DataFrame({category_col: ['其他'], value_col: [other_sum]})
                ], ignore_index=True)
        
        total = detail_data[value_col].sum()
        
        # 格式化数值
        if config.get('format_numbers', True):
            detail_data['formatted'] = detail_data[value_col].apply(self._format_number)
        else:
            detail_data['formatted'] = detail_data[value_col].round(2)
        
        detail_data['百分比'] = (detail_data[value_col] / total * 100).round(1)
        
        st.markdown(f"### 📋 详细数据：{' > '.join(path)}")
        st.dataframe(
            detail_data[[category_col, 'formatted', '百分比']].rename(
                columns={category_col: "类别", "formatted": "数值"}
            ),
            use_container_width=True,
            hide_index=True
        )
    
    def _add_controls(self, path, level_cols):
        """添加返回控件"""
        if path:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔙 返回上一级", key="depth_back_btn", use_container_width=True):
                    st.session_state.depth_path.pop()
                    st.session_state.depth_selected = None
                    st.rerun()
            
            # 面包屑导航
            breadcrumb = self._get_breadcrumb(path, level_cols)
            st.caption(f"📍 当前位置：{breadcrumb}")
    
    def _get_breadcrumb(self, path, level_cols):
        """获取面包屑导航"""
        if not path:
            return "当前：顶层"
        breadcrumb = []
        for i, val in enumerate(path):
            if i < len(level_cols):
                breadcrumb.append(f"{level_cols[i]}: {val}")
        return " → ".join(breadcrumb)
    
    def _format_number(self, num):
        """格式化数值"""
        if num >= 1e8:
            return f"{num/1e8:.2f}亿"
        elif num >= 1e4:
            return f"{num/1e4:.2f}万"
        else:
            return f"{num:.2f}"