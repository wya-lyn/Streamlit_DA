"""
分析选项模块：包含分析选项标签页的所有功能
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def render_analysis_options_tab():
    """分析选项标签页（整合统计和图表）"""
    if st.session_state.df is None:
        st.info("请先上传数据")
        return
    
    # 使用tabs组织不同类型的分析
    analysis_tabs = st.tabs([
        "📈 描述性统计", 
        "🔗 相关性分析", 
        "📊 分组统计", 
        "⏱️ 时间序列", 
        "📐 数据透视表",
        "🥧 复合饼图"
    ])
    
    with analysis_tabs[0]:
        render_descriptive_stats_with_chart()
    
    with analysis_tabs[1]:
        render_correlation_with_heatmap()
    
    with analysis_tabs[2]:
        render_group_stats_with_chart()
    
    with analysis_tabs[3]:
        render_time_series_with_chart()
    
    with analysis_tabs[4]:
        render_pivot_with_chart()
    
    with analysis_tabs[5]:
        render_composite_pie_chart()


def render_descriptive_stats_with_chart():
    """数据概览（整合 df.info 和 df.describe）"""
    st.markdown("#### 📊 数据概览")
    
    df = st.session_state.df
    
    # ===========================================
    # 第一部分：基本信息
    # ===========================================
    st.markdown("##### 基本信息")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总行数", f"{len(df):,}")
    with col2:
        st.metric("总列数", len(df.columns))
    with col3:
        missing_count = df.isna().sum().sum()
        missing_pct = (missing_count / (len(df) * len(df.columns))) * 100
        st.metric("缺失值", f"{missing_count} ({missing_pct:.1f}%)")
    with col4:
        memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("内存占用", f"{memory_usage:.2f} MB")
    
    st.markdown("---")
    
    # ===========================================
    # 第二部分：列信息
    # ===========================================
    st.markdown("##### 列信息")
    
    col_info = []
    for i, col in enumerate(df.columns):
        col_info.append({
            "列名": col,
            "数据类型": str(df[col].dtype),
            "非空值数": df[col].count(),
            "缺失值数": df[col].isna().sum(),
            "缺失率": f"{df[col].isna().sum() / len(df) * 100:.1f}%",
            "唯一值数": df[col].nunique()
        })
    
    col_info_df = pd.DataFrame(col_info)
    col_info_df = col_info_df.reset_index(drop=True)
    st.dataframe(col_info_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # ===========================================
    # 第三部分：数值列统计摘要
    # ===========================================
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if numeric_cols:
        st.markdown("##### 数值列统计摘要")
        
        desc_df = df[numeric_cols].describe(percentiles=[.25, .5, .75]).round(2)
        desc_df = desc_df.reset_index()
        desc_df = desc_df.rename(columns={"index": "统计指标"})
        desc_df = desc_df.reset_index(drop=True)
        
        st.dataframe(desc_df, use_container_width=True, hide_index=True)
        
        with st.expander("查看高级统计指标（方差/偏度/峰度）"):
            advanced_stats = []
            for col in numeric_cols:
                advanced_stats.append({
                    "统计指标": "方差",
                    col: round(df[col].var(), 2)
                })
                advanced_stats.append({
                    "统计指标": "偏度",
                    col: round(df[col].skew(), 2)
                })
                advanced_stats.append({
                    "统计指标": "峰度",
                    col: round(df[col].kurtosis(), 2)
                })
            adv_df = pd.DataFrame(advanced_stats)
            adv_df = adv_df.reset_index(drop=True)
            st.dataframe(adv_df, use_container_width=True, hide_index=True)
    else:
        st.info("没有数值类型的列")
    
    st.markdown("---")
    
    # ===========================================
    # 第四部分：文本列统计摘要
    # ===========================================
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    if text_cols:
        st.markdown("##### 文本列统计摘要")
        
        text_stats = []
        for col in text_cols:
            text_stats.append({
                "列名": col,
                "总记录数": len(df[col]),
                "唯一值数": df[col].nunique(),
                "最频繁值": df[col].mode().iloc[0] if not df[col].mode().empty else "N/A",
                "最频繁值出现次数": df[col].value_counts().iloc[0] if len(df[col].value_counts()) > 0 else 0,
                "缺失值": df[col].isna().sum()
            })
        
        text_stats_df = pd.DataFrame(text_stats)
        text_stats_df = text_stats_df.reset_index(drop=True)
        st.dataframe(text_stats_df, use_container_width=True, hide_index=True)
        
        with st.expander("查看各列频数分布"):
            for col in text_cols[:3]:
                st.markdown(f"**{col}**")
                freq = df[col].value_counts().head(10).reset_index()
                freq.columns = [col, "频数"]
                freq = freq.reset_index(drop=True)
                st.dataframe(freq, use_container_width=True, hide_index=True)
                st.markdown("---")
            
            if len(text_cols) > 3:
                st.info(f"还有 {len(text_cols) - 3} 列未显示，可导出完整统计")
    else:
        st.info("没有文本类型的列")
    
    st.markdown("---")
    
    # ===========================================
    # 第五部分：数据导出
    # ===========================================
    st.markdown("##### 导出统计结果")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 导出完整统计报告", key="export_full_stats", use_container_width=True):
            with pd.ExcelWriter('data_overview.xlsx') as writer:
                basic_info = pd.DataFrame({
                    "指标": ["总行数", "总列数", "缺失值总数", "内存占用(MB)"],
                    "值": [len(df), len(df.columns), missing_count, f"{memory_usage:.2f}"]
                })
                basic_info.to_excel(writer, sheet_name='基本信息', index=False)
                col_info_df.to_excel(writer, sheet_name='列信息', index=False)
                if numeric_cols:
                    desc_df.to_excel(writer, sheet_name='数值统计', index=False)
                if text_cols:
                    text_stats_df.to_excel(writer, sheet_name='文本统计', index=False)
            
            with open('data_overview.xlsx', 'rb') as f:
                st.download_button(
                    label="点击下载Excel报告",
                    data=f,
                    file_name=f"data_overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_full_stats"
                )
    
    with col2:
        if st.button("📥 导出为CSV", key="export_stats_csv", use_container_width=True):
            all_stats = []
            for col in numeric_cols:
                row = {"列名": col, "类型": "数值"}
                for stat in desc_df["统计指标"]:
                    if stat in df[col].describe().index:
                        row[stat] = round(df[col].describe()[stat], 2)
                all_stats.append(row)
            
            for col in text_cols:
                row = {
                    "列名": col,
                    "类型": "文本",
                    "总记录数": len(df[col]),
                    "唯一值数": df[col].nunique(),
                    "最频繁值": df[col].mode().iloc[0] if not df[col].mode().empty else "N/A",
                    "缺失值": df[col].isna().sum()
                }
                all_stats.append(row)
            
            stats_df = pd.DataFrame(all_stats)
            csv = stats_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="点击下载CSV",
                data=csv,
                file_name=f"data_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_stats_csv"
            )


def render_correlation_with_heatmap():
    """相关性分析 + 热力图"""
    st.markdown("#### 相关性分析")
    
    numeric_cols = st.session_state.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("需要至少2个数值列才能进行相关性分析")
        with st.expander("💡 如何准备数据？"):
            st.markdown("""
            **相关性分析要求**：
            - 只能分析**数值列**（int64, float64类型）
            - 文本列需要先转换为数值才能分析
            - 可以使用 **转换** 功能将文本转为数值
            
            **当前数值列**：
            """ + (", ".join(numeric_cols) if numeric_cols else "无数值列"))
        return
    
    # 调试信息
    with st.expander("🔍 调试信息（点击展开）", expanded=False):
        st.write(f"所有列名: {st.session_state.df.columns.tolist()}")
        st.write(f"数据类型: {st.session_state.df.dtypes.to_dict()}")
        st.write(f"检测到的数值列数: {len(numeric_cols)}")
        st.write(f"数值列名: {numeric_cols}")
    
    # 列选择
    selected_cols = st.multiselect(
        "选择要分析的数值列（至少2列）",
        numeric_cols,
        key="corr_cols_chart",
        placeholder="请选择要分析的数值列"
    )
    
    if len(selected_cols) < 2:
        st.info("请至少选择2个数值列进行分析")
        return
    
    # 方法选择
    method = st.selectbox(
        "选择分析方法",
        ["pearson", "spearman", "kendall"],
        key="corr_method_chart",
        format_func=lambda x: {
            "pearson": "皮尔逊 (Pearson) - 线性相关，适用于连续数值",
            "spearman": "斯皮尔曼 (Spearman) - 秩相关，适用于单调关系",
            "kendall": "肯德尔 (Kendall) - 一致性，适用于小样本"
        }[x]
    )
    
    # 图表选项
    col1, col2 = st.columns(2)
    with col1:
        show_values = st.checkbox("显示相关系数", value=True, key="corr_show_values")
    with col2:
        color_scale = st.selectbox(
            "色阶",
            ["RdBu_r", "Viridis", "Plasma", "Inferno", "Blues", "Reds"],
            key="corr_colorscale"
        )
    
    # 显示已选择列的信息
    st.caption(f"已选择 {len(selected_cols)} 列: {', '.join(selected_cols[:5])}{'...' if len(selected_cols) > 5 else ''}")
    
    # 操作按钮
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 生成相关性矩阵", key="btn_corr_matrix", use_container_width=True):
            with st.spinner("正在计算相关性..."):
                try:
                    from utils.stats_analyzer import StatsAnalyzer
                    analyzer = StatsAnalyzer()
                    
                    corr_df = analyzer.correlation_analysis(
                        st.session_state.df[selected_cols], method
                    )
                    
                    if corr_df is not None and not corr_df.empty:
                        corr_df = corr_df.round(4)
                        st.session_state.preview_manager.update_stats_preview(
                            corr_df, 
                            f"{method.upper()}相关性矩阵"
                        )
                        st.success("相关性矩阵已生成，请查看主内容区")
                        st.rerun()
                    else:
                        st.error("相关性矩阵生成失败")
                except Exception as e:
                    st.error(f"计算失败: {str(e)}")
    
    with col2:
        if st.button("🔥 生成热力图", key="btn_corr_heatmap", use_container_width=True):
            with st.spinner("正在生成热力图..."):
                try:
                    from utils.chart_generator import ChartGenerator
                    
                    corr_df = st.session_state.df[selected_cols].corr(method=method)
                    
                    fig = ChartGenerator.create_chart(
                        corr_df, 
                        "热力图",
                        show_values=show_values,
                        colorscale=color_scale
                    )
                    
                    if fig:
                        st.session_state.preview_manager.update_chart_preview(
                            fig, 
                            f"{method.upper()}相关性热力图"
                        )
                        st.success("热力图已生成，请查看主内容区")
                        st.rerun()
                    else:
                        st.error("热力图生成失败")
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")


def render_group_stats_with_chart():
    """分组统计 + 聚合图表"""
    st.markdown("#### 分组统计")
    
    from components.group_stats_chart import GroupStatsChart
    
    category_cols = st.session_state.df.select_dtypes(include=['object']).columns.tolist()
    numeric_cols = st.session_state.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if not category_cols:
        st.warning("没有分类列可用于分组")
        return
    
    if not numeric_cols:
        st.warning("没有数值列可用于聚合")
        return
    
    # 左右两列布局
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("##### 分组设置")
        
        group_cols = st.multiselect(
            "选择分组字段（支持多级分组）",
            category_cols,
            key="group_cols_chart",
            placeholder="请选择分组字段（可按顺序选择多个）"
        )
        
        value_cols = st.multiselect(
            "选择数值字段",
            numeric_cols,
            key="group_values_chart",
            placeholder="请选择数值字段"
        )
        
        agg_options = ["请选择聚合函数", "mean", "sum", "count", "min", "max"]
        agg_func = st.selectbox(
            "选择聚合函数",
            agg_options,
            key="group_agg_chart",
            format_func=lambda x: {
                "请选择聚合函数": "请选择聚合函数",
                "mean": "平均值", 
                "sum": "求和", 
                "count": "计数",
                "min": "最小值", 
                "max": "最大值"
            }.get(x, x),
            index=0
        )
    
    with col_right:
        if group_cols and value_cols and agg_func != "请选择聚合函数":
            st.markdown("##### 图表设置")
            
            chart_options = ["请选择图表类型", "柱状图", "折线图", "饼图", "条形图", "分组柱状图", "堆积柱状图"]
            chart_type = st.selectbox(
                "选择图表类型",
                chart_options,
                key="group_chart_type",
                index=0
            )
            
            if chart_type != "请选择图表类型":
                col_a, col_b = st.columns(2)
                with col_a:
                    sort_by = st.checkbox("排序显示", value=True, key="group_sort")
                with col_b:
                    show_values = st.checkbox("显示数值标签", value=True, key="group_show_values")
                
                if len(group_cols) > 1:
                    st.info(f"📊 将使用第一级分组 '{group_cols[0]}' 作为X轴，第二级分组 '{group_cols[1]}' 作为颜色分组")
    
    # 按钮区域
    if group_cols and value_cols and agg_func != "请选择聚合函数":
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("📊 执行分组统计", key="btn_group_calc", use_container_width=True):
                with st.spinner("正在计算分组统计..."):
                    try:
                        chart = GroupStatsChart(
                            st.session_state.df,
                            group_cols,
                            value_cols,
                            agg_func
                        )
                        
                        result_df = chart.agg_df
                        result_df = result_df.round(2)
                        
                        st.session_state.preview_manager.update_stats_preview(
                            result_df,
                            f"分组统计: {' → '.join(group_cols)}"
                        )
                        st.success("分组统计已生成，请查看主内容区")
                        st.rerun()
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
        
        with col_btn2:
            if chart_type != "请选择图表类型" and st.button("📈 生成分组图表", key="btn_group_chart", use_container_width=True):
                with st.spinner("正在生成图表..."):
                    try:
                        chart = GroupStatsChart(
                            st.session_state.df,
                            group_cols,
                            value_cols,
                            agg_func
                        )
                        
                        fig = chart.render(show_values=show_values, sort_by=sort_by)
                        
                        if fig:
                            st.session_state.preview_manager.update_chart_preview(
                                fig,
                                f"{value_cols[0]} 按 {' → '.join(group_cols)} 分组"
                            )
                            st.session_state.preview_mode = 'chart'
                        else:
                            st.error("图表生成失败")
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
        
        with col_btn3:
            st.caption(f"已选择: {len(group_cols)}个分组, {len(value_cols)}个数值")
            if len(group_cols) > 1:
                st.caption(f"分组层级: {' → '.join(group_cols)}")
    else:
        st.info("请依次选择：分组字段 → 数值字段 → 聚合函数")


def render_time_series_with_chart():
    """时间序列分析 + 趋势图"""
    st.markdown("#### 时间序列分析")
    
    df = st.session_state.df
    
    # 检测日期列
    date_cols = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_cols.append(col)
    
    if not date_cols:
        st.warning("没有日期类型的列，请先转换日期格式")
        return
    
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if not numeric_cols:
        st.warning("没有数值列可用于分析")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        date_col = st.selectbox("日期列", date_cols, key="ts_date")
        value_col = st.selectbox("数值列", numeric_cols, key="ts_value")
        
        freq = st.selectbox(
            "重采样频率",
            ["D", "W", "M", "Q", "Y"],
            key="ts_freq",
            format_func=lambda x: {"D": "日", "W": "周", "M": "月", "Q": "季", "Y": "年"}[x]
        )
    
    with col2:
        st.markdown("##### 分析选项")
        show_ma = st.checkbox("移动平均线", value=True, key="ts_ma")
        if show_ma:
            ma_window = st.slider("移动平均窗口", 3, 30, 7, key="ts_ma_window")
        
        show_trend = st.checkbox("趋势线", value=False, key="ts_trend")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 时间序列表", key="btn_ts_table", use_container_width=True):
            with st.spinner("正在分析..."):
                try:
                    from utils.stats_analyzer import StatsAnalyzer
                    analyzer = StatsAnalyzer()
                    
                    ts_df = analyzer.time_series_analysis(
                        st.session_state.df, date_col, value_col, freq
                    )
                    if ts_df is not None:
                        st.session_state.preview_manager.update_stats_preview(
                            ts_df.head(100),
                            f"{value_col}时间序列 ({freq})"
                        )
                        st.success("时间序列表已生成")
                        st.rerun()
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    with col2:
        if st.button("📈 生成趋势图", key="btn_ts_chart", use_container_width=True):
            with st.spinner("正在生成图表..."):
                try:
                    from utils.chart_generator import ChartGenerator
                    
                    # 准备时间序列数据
                    ts_data = st.session_state.df[[date_col, value_col]].copy()
                    ts_data[date_col] = pd.to_datetime(ts_data[date_col])
                    ts_data = ts_data.set_index(date_col).resample(freq).mean().reset_index()
                    
                    fig = ChartGenerator.create_chart(
                        ts_data, "折线图", date_col, value_col,
                        show_values=False
                    )
                    
                    if fig and show_ma:
                        ts_data['MA'] = ts_data[value_col].rolling(window=ma_window).mean()
                        fig.add_scatter(
                            x=ts_data[date_col], 
                            y=ts_data['MA'], 
                            mode='lines', 
                            name=f'MA{ma_window}',
                            line=dict(dash='dot')
                        )
                    
                    if fig:
                        st.session_state.preview_manager.update_chart_preview(
                            fig, f"{value_col}趋势图"
                        )
                        st.success("趋势图已生成")
                        st.rerun()
                except Exception as e:
                    st.error(f"生成失败: {str(e)}")
    
    with col3:
        st.caption(f"频率: {freq}")


def render_pivot_with_chart():
    """数据透视表 + 透视图"""
    st.markdown("#### 数据透视表")
    
    df = st.session_state.df
    all_cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        index_cols = st.multiselect(
            "选择行字段",
            all_cols,
            key="pivot_index",
            placeholder="请选择行字段"
        )
        
        columns_cols = st.multiselect(
            "选择列字段（可选）",
            all_cols,
            key="pivot_columns",
            placeholder="请选择列字段"
        )
        
        values_cols = st.multiselect(
            "选择值字段",
            numeric_cols,
            key="pivot_values",
            placeholder="请选择值字段"
        )
        
        agg_options = ["请选择聚合函数", "mean", "sum", "count", "min", "max", "std"]
        agg_func = st.selectbox(
            "选择聚合函数",
            agg_options,
            key="pivot_agg",
            format_func=lambda x: {
                "请选择聚合函数": "请选择聚合函数",
                "mean": "平均值",
                "sum": "求和",
                "count": "计数",
                "min": "最小值",
                "max": "最大值",
                "std": "标准差"
            }.get(x, x),
            index=0
        )
    
    with col2:
        if index_cols and values_cols and agg_func != "请选择聚合函数":
            st.markdown("##### 图表设置")
            chart_options = ["请选择图表类型", "柱状图", "热力图", "饼图"]
            chart_type = st.selectbox(
                "选择图表类型",
                chart_options,
                key="pivot_chart_type",
                index=0
            )
            
            if chart_type != "请选择图表类型":
                if chart_type == "热力图":
                    show_values = st.checkbox("显示数值", value=True, key="pivot_show_values")
    
    if index_cols and values_cols and agg_func != "请选择聚合函数":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 生成透视表", key="btn_pivot_table", use_container_width=True):
                with st.spinner("正在生成透视表..."):
                    try:
                        pivot_df = pd.pivot_table(
                            df,
                            index=index_cols[0] if len(index_cols) == 1 else index_cols,
                            columns=columns_cols[0] if columns_cols else None,
                            values=values_cols[0] if len(values_cols) == 1 else values_cols,
                            aggfunc=agg_func,
                            fill_value=0
                        )
                        
                        st.session_state.preview_manager.update_stats_preview(
                            pivot_df,
                            "数据透视表"
                        )
                        st.success("透视表已生成，请查看主内容区")
                        st.rerun()
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
        
        with col2:
            if chart_type != "请选择图表类型" and st.button("📈 生成透视图", key="btn_pivot_chart", use_container_width=True):
                with st.spinner("正在生成图表..."):
                    try:
                        from utils.chart_generator import ChartGenerator
                        
                        pivot_data = pd.pivot_table(
                            df,
                            index=index_cols[0],
                            columns=columns_cols[0] if columns_cols else None,
                            values=values_cols[0],
                            aggfunc=agg_func,
                            fill_value=0
                        ).reset_index()
                        
                        if chart_type == "热力图":
                            fig = ChartGenerator.create_chart(
                                pivot_data, 
                                "热力图",
                                show_values=show_values
                            )
                        elif chart_type == "饼图":
                            fig = ChartGenerator.create_chart(
                                pivot_data, 
                                "饼图",
                                index_cols[0],
                                values_cols[0]
                            )
                        else:
                            fig = ChartGenerator.create_chart(
                                pivot_data, 
                                "柱状图",
                                index_cols[0],
                                values_cols[0]
                            )
                        
                        if fig:
                            st.session_state.preview_manager.update_chart_preview(
                                fig,
                                f"透视图-{chart_type}"
                            )
                            st.success("透视图已生成")
                            st.rerun()
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
        
        with col3:
            st.caption(f"聚合: {agg_func}")
    else:
        st.info("请依次选择：行字段 → 值字段 → 聚合函数")


def render_composite_pie_chart():
    """复合饼图（四种模式）"""
    st.markdown("#### 🥧 复合饼图")
    
    df = st.session_state.df
    
    category_cols = df.select_dtypes(include=['object']).columns.tolist()
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if not category_cols:
        st.warning("需要分类列才能生成复合饼图")
        return
    
    if not numeric_cols:
        st.warning("需要数值列才能生成复合饼图")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        category_col = st.selectbox(
            "选择分类列（主类别）",
            category_cols,
            key="composite_cat_col"
        )
    
    with col2:
        value_col = st.selectbox(
            "选择数值列",
            numeric_cols,
            key="composite_val_col"
        )
    
    st.markdown("##### 选择模式")
    pie_mode = st.radio(
        "复合饼图模式",
        ["子图布局", "交互下钻", "复合定位", "南丁格尔玫瑰图"],
        key="composite_pie_mode",
        horizontal=True,
        help="""
        - 子图布局：网格展示主图和子图
        - 交互下钻：点击主图区块查看详情
        - 复合定位：预设模板布局
        - 南丁格尔玫瑰图：极坐标柱状图，半径表示数值大小
        """
    )
    
    # 模式说明
    if pie_mode == "子图布局":
        st.info("📊 子图布局模式：主图在左上角，其他子图按网格排列，适合对比分析多个类别")
    elif pie_mode == "交互下钻":
        st.info("🖱️ 交互下钻模式：点击主图区块，下方显示该区块的详细构成，适合层级探索")
    elif pie_mode == "复合定位":
        st.info("🎯 复合定位模式：主图居中，子图按预设位置环绕，适合报告展示")
    else:
        st.info("🌸 南丁格尔玫瑰图：极坐标柱状图，半径表示数值大小，适合周期性数据展示")
    
    # 高级选项
    with st.expander("高级选项"):
        max_categories = st.slider(
            "最大显示类别数",
            min_value=3,
            max_value=10,
            value=5,
            key="composite_max_cat"
        )
        show_title = st.checkbox("显示图表标题", value=True, key="composite_title")
    
    # 生成图表按钮
    if st.button("🎨 生成复合饼图", key="btn_composite_pie", use_container_width=True, type="primary"):
        with st.spinner(f"正在生成{pie_mode}复合饼图..."):
            try:
                from utils.chart_generator import ChartGenerator
                
                fig = ChartGenerator.create_chart(
                    df=st.session_state.df,
                    chart_type="复合饼图",
                    x_col=category_col,
                    y_col=value_col,
                    pie_mode=pie_mode,
                    max_categories=max_categories,
                    title=f"{category_col}分布" if show_title else None
                )
                
                if fig:
                    st.session_state.preview_manager.update_chart_preview(
                        fig,
                        f"复合饼图-{pie_mode}"
                    )
                    st.success(f"{pie_mode}复合饼图已生成，请查看主内容区")
                    st.rerun()
                else:
                    st.error("图表生成失败，请检查数据")
            except Exception as e:
                st.error(f"生成失败: {str(e)}")
    
    # 数据预览
    with st.expander("查看数据分布"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 类别分布")
            category_counts = df[category_col].value_counts().head(max_categories)
            st.dataframe(category_counts.reset_index(), use_container_width=True)
        with col2:
            st.markdown("##### 数值汇总")
            category_sums = df.groupby(category_col)[value_col].sum().sort_values(ascending=False).head(max_categories)
            st.dataframe(category_sums.reset_index(), use_container_width=True)