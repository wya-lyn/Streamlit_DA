"""
分组统计图表模块
支持2级、3级分组的图表生成
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class GroupStatsChart:
    """分组统计图表生成器"""
    
    def __init__(self, df, group_cols, value_cols, agg_func):
        """
        初始化
        
        Parameters:
        -----------
        df : DataFrame
            原始数据
        group_cols : list
            分组字段列表
        value_cols : list
            数值字段列表
        agg_func : str
            聚合函数 (mean/sum/count/min/max)
        """
        self.df = df
        self.group_cols = group_cols
        self.value_cols = value_cols
        self.agg_func = agg_func
        self.y_col = value_cols[0] if value_cols else None
        
        # 聚合数据
        self.agg_df = self._aggregate_data()
    
    def _aggregate_data(self):
        """聚合数据"""
        df_clean = self.df.copy()
        for col in self.group_cols:
            df_clean[col] = df_clean[col].fillna("(空值)").astype(str)
        
        agg_df = df_clean.groupby(self.group_cols)[self.y_col].agg(self.agg_func).reset_index()
        agg_df = agg_df.dropna()
        
        return agg_df
    
    def _create_single_level_chart(self, show_values, sort_by):
        """单级分组图表"""
        x_col = self.group_cols[0]
        
        if sort_by:
            self.agg_df = self.agg_df.sort_values(self.y_col, ascending=False)
        
        fig = px.bar(
            self.agg_df,
            x=x_col,
            y=self.y_col,
            text_auto=show_values,
            title=f"{self.y_col} 按 {x_col} 分组"
        )
        
        fig.update_layout(
            xaxis=dict(tickangle=-45),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500
        )
        
        if show_values:
            fig.update_traces(textposition='outside', textfont_size=10)
        
        return fig
    
    def _create_two_level_chart(self, show_values, sort_by):
        """二级分组图表（子图方式）"""
        x_col = self.group_cols[0]
        color_col = self.group_cols[1]
        
        brands = self.agg_df[x_col].unique().tolist()
        
        # 显示层级提示
        st.info(f"""
        📊 **分组层级说明**
        - 第1级分组（X轴）：{x_col}
        - 第2级分组（颜色）：{color_col}
        - 数值列：{self.y_col}
        
        💡 **图表说明**：每个子图代表一个第1级分组，内部显示第2级分组的数值对比。
        """)
        
        # 显示数据矩阵（调试用）
        with st.expander("🔍 查看数据矩阵"):
            data_matrix = {}
            for brand in brands:
                brand_data = self.agg_df[self.agg_df[x_col] == brand]
                data_matrix[brand] = dict(zip(brand_data[color_col], brand_data[self.y_col]))
            matrix_df = pd.DataFrame(data_matrix).T.fillna(0)
            st.dataframe(matrix_df)
        
        # 确定子图布局
        if len(brands) <= 4:
            rows, cols = 1, len(brands)
        else:
            cols = 3
            rows = (len(brands) + cols - 1) // cols
        
        # 创建子图
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=brands,
            shared_yaxes=True,
            shared_xaxes=False,
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # 收集所有需要显示的图例（所有会员等级）
        all_levels = self.agg_df[color_col].unique().tolist()
        
        # 为每个品牌创建子图
        for idx, brand in enumerate(brands):
            row = idx // cols + 1
            col = idx % cols + 1
            
            brand_data = self.agg_df[self.agg_df[x_col] == brand]
            if sort_by:
                brand_data = brand_data.sort_values(self.y_col, ascending=False)
            
            # 为每个会员等级添加柱子
            for level in all_levels:
                level_data = brand_data[brand_data[color_col] == level]
                if level_data.empty:
                    value = 0
                else:
                    value = level_data[self.y_col].iloc[0]
                
                fig.add_trace(
                    go.Bar(
                        x=[level],
                        y=[value],
                        name=str(level),  # 图例名称
                        text=[f"{value:.2f}" if show_values and value > 0 else ""],
                        textposition='outside' if show_values else None,
                        legendgroup=str(level),  # 同一等级的图例合并
                        showlegend=(idx == 0)    # 只在第一个子图显示图例
                    ),
                    row=row,
                    col=col
                )
            
            fig.update_xaxes(title_text=color_col, row=row, col=col, tickangle=-45)
            if col == 1:
                fig.update_yaxes(title_text=self.y_col, row=row, col=col)
        
        # 设置整体布局
        fig.update_layout(
            title_text=f"{self.y_col} 按 {x_col} → {color_col} 分组",
            height=400 * rows,
            showlegend=True,
            legend=dict(
                title=color_col,
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color="#FFFFFF"),
                title_font=dict(size=11, color="#FFFFFF")
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            bargap=0.2,
            bargroupgap=0.1
        )
        
        # 统一Y轴范围
        all_values = self.agg_df[self.y_col].values
        if len(all_values) > 0:
            fig.update_yaxes(range=[0, all_values.max() * 1.1])
        
        if show_values:
            fig.update_traces(textposition='outside', textfont_size=10)
        
        return fig
    
    def _create_three_level_chart(self, show_values, sort_by):
        """三级分组图表"""
        first_col = self.group_cols[0]
        second_col = self.group_cols[1]
        third_col = self.group_cols[2]
        
        # 显示层级提示
        st.info(f"""
        📊 **三级分组说明**
        - 第1级分组：{first_col}（使用下拉菜单选择）
        - 第2级分组：{second_col}（子图X轴）
        - 第3级分组：{third_col}（颜色分组）
        - 数值列：{self.y_col}
        
        💡 **操作提示**：请先选择第1级分组的值，查看对应数据
        """)
        
        # 获取第1级分组的所有值
        first_values = self.agg_df[first_col].unique().tolist()
        selected_first = st.selectbox(
            f"选择 {first_col}",
            first_values,
            key="first_level_select"
        )
        
        # 筛选数据
        filtered_df = self.agg_df[self.agg_df[first_col] == selected_first]
        
        if filtered_df.empty:
            st.warning(f"{first_col} = {selected_first} 没有数据")
            return None
        
        # 获取第二级分组的值
        second_values = filtered_df[second_col].unique().tolist()
        
        # 收集所有第三级分组的值（用于图例）
        all_third_levels = filtered_df[third_col].unique().tolist()
        
        # 确定子图布局
        if len(second_values) <= 4:
            rows, cols = 1, len(second_values)
        else:
            cols = 3
            rows = (len(second_values) + cols - 1) // cols
        
        # 创建子图
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=second_values,
            shared_yaxes=True,
            shared_xaxes=False,
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # 为每个第二级分组创建子图
        for idx, second_val in enumerate(second_values):
            row = idx // cols + 1
            col = idx % cols + 1
            
            sub_data = filtered_df[filtered_df[second_col] == second_val]
            if sort_by:
                sub_data = sub_data.sort_values(self.y_col, ascending=False)
            
            # 为每个第三级分组添加柱子（遍历所有等级，确保图例完整）
            for level in all_third_levels:
                level_data = sub_data[sub_data[third_col] == level]
                if level_data.empty:
                    value = 0
                else:
                    value = level_data[self.y_col].iloc[0]
                
                fig.add_trace(
                    go.Bar(
                        x=[level],
                        y=[value],
                        name=str(level),                    # 图例名称
                        text=[f"{value:.2f}" if show_values and value > 0 else ""],
                        textposition='outside' if show_values else None,
                        legendgroup=str(level),             # 同一等级的图例合并
                        showlegend=(idx == 0)               # 只在第一个子图显示图例
                    ),
                    row=row,
                    col=col
                )
            
            fig.update_xaxes(title_text=third_col, row=row, col=col, tickangle=-45)
            if col == 1:
                fig.update_yaxes(title_text=self.y_col, row=row, col=col)
        
        # 设置整体布局
        fig.update_layout(
            title_text=f"{self.y_col} 按 {first_col}={selected_first} → {second_col} → {third_col}",
            height=400 * rows,
            showlegend=True,
            legend=dict(
                title=third_col,
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color="#FFFFFF"),
                title_font=dict(size=11, color="#FFFFFF")
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # 统一Y轴范围
        all_values = filtered_df[self.y_col].values
        if len(all_values) > 0:
            fig.update_yaxes(range=[0, all_values.max() * 1.1])
        
        if show_values:
            fig.update_traces(textposition='outside', textfont_size=10)
        
        return fig
    
    def render(self, show_values=True, sort_by=True):
        """
        渲染图表
        
        Parameters:
        -----------
        show_values : bool
            是否显示数值标签
        sort_by : bool
            是否按数值排序
        """
        level = len(self.group_cols)
        
        if level == 1:
            fig = self._create_single_level_chart(show_values, sort_by)
        elif level == 2:
            fig = self._create_two_level_chart(show_values, sort_by)
        elif level >= 3:
            fig = self._create_three_level_chart(show_values, sort_by)
        else:
            st.warning("请至少选择1个分组字段")
            return None
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            return fig
        
        return None