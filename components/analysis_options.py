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
        "🥧 深度分析"
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
def render_data_quality_analysis():
    """数据质量分析（异常检测）"""
    st.markdown("##### ⚠️ 数据质量分析")
    st.caption("通过频度分布检测数据是否可能存在异常（如机器操作、数据倾斜等）")
    
    df = st.session_state.df
    import numpy as np
    
    quality_stats = []
    
    # ========== 文本列分析 ==========
    text_cols = df.select_dtypes(include=['object']).columns.tolist()

    for col in text_cols:
        total = len(df[col])
        unique = df[col].nunique()
        missing = df[col].isna().sum()
        missing_pct = missing / total * 100 if total > 0 else 0
        
        if total == 0:
            quality_stats.append({
                "列名": col,
                "类型": "文本",
                "风险等级": "高风险",
                "唯一值数": 0,
                "唯一值占比": "0%",
                "最频繁值": "无",
                "最频繁值占比": "0%",
                "前3值占比": "0%",
                "缺失率": "100%",
                "信息熵": "0.00",
                "熵归一化": "0.00",
                "异常说明": "无数据"
            })
            continue
        
        if unique > 0:
            value_counts = df[col].value_counts(dropna=False)
            top1_count = value_counts.iloc[0] if len(value_counts) > 0 else 0
            top1_pct = top1_count / total * 100 if total > 0 else 0
            
            top3_count = value_counts.head(3).sum() if len(value_counts) >= 3 else value_counts.sum()
            top3_pct = top3_count / total * 100 if total > 0 else 0
            
            unique_pct = unique / total * 100 if total > 0 else 0
            
            # 计算信息熵
            probs = value_counts / total
            entropy = -np.sum(probs * np.log2(probs + 1e-10))
            max_entropy = np.log2(unique) if unique > 1 else 1
            entropy_normalized = entropy / max_entropy if max_entropy > 0 else 0
            
            # 异常判定规则
            anomalies = []
            risk_level = "正常"
            
            if unique == 1:
                anomalies.append("唯一值只有1个")
                risk_level = "高风险"
            elif unique == 0:
                anomalies.append("无数据")
                risk_level = "高风险"
            elif top1_pct > 95:
                anomalies.append(f"最频繁值占比过高 ({top1_pct:.1f}%)")
                risk_level = "高风险"
            elif top1_pct > 80:
                anomalies.append(f"最频繁值占比较高 ({top1_pct:.1f}%)")
                risk_level = "中风险"
            elif top3_pct > 98:
                anomalies.append(f"前3个值占比过高 ({top3_pct:.1f}%)")
                risk_level = "中风险"
            elif unique_pct < 5 and unique > 1:
                anomalies.append(f"唯一值占比较低 ({unique_pct:.1f}%)")
                risk_level = "低风险"
            elif missing_pct > 50:
                anomalies.append(f"缺失值过高 ({missing_pct:.1f}%)")
                risk_level = "中风险"
            elif missing_pct > 20:
                anomalies.append(f"缺失值较高 ({missing_pct:.1f}%)")
                risk_level = "低风险"
            
            if not anomalies:
                anomalies.append("分布正常")
            
            quality_stats.append({
                "列名": col,
                "类型": "文本",
                "风险等级": risk_level,
                "唯一值数": unique,
                "唯一值占比": f"{unique_pct:.1f}%",
                "最频繁值": str(value_counts.index[0])[:30] if len(value_counts) > 0 else "无",
                "最频繁值占比": f"{top1_pct:.1f}%",
                "前3值占比": f"{top3_pct:.1f}%",
                "缺失率": f"{missing_pct:.1f}%",
                "信息熵": f"{entropy:.2f}",
                "熵归一化": f"{entropy_normalized:.2f}",
                "异常说明": "、".join(anomalies)
            })
        else:
            quality_stats.append({
                "列名": col,
                "类型": "文本",
                "风险等级": "高风险",
                "唯一值数": 0,
                "唯一值占比": "0%",
                "最频繁值": "无",
                "最频繁值占比": "0%",
                "前3值占比": "0%",
                "缺失率": f"{missing_pct:.1f}%",
                "信息熵": "0.00",
                "熵归一化": "0.00",
                "异常说明": "无有效数据"
            })
    
    # ========== 数值列分析 ==========
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    for col in numeric_cols:
        total = len(df[col])
        data = df[col].dropna()
        valid_count = len(data)
        missing = total - valid_count
        missing_pct = missing / total * 100 if total > 0 else 0
        
        # 处理空数据列
        if total == 0:
            quality_stats.append({
                "列名": col,
                "类型": "数值",
                "风险等级": "高风险",
                "有效值数": 0,
                "缺失率": "100%",
                "均值": "N/A",
                "标准差": "N/A",
                "最小值": "N/A",
                "最大值": "N/A",
                "异常值数": 0,
                "异常值占比": "0%",
                "零值占比": "0%",
                "负值占比": "0%",
                "重复值占比": "0%",
                "变异系数": "N/A",
                "异常说明": "无数据"
            })
            continue
        
        # 处理有数据但全是缺失值的情况
        if valid_count == 0:
            quality_stats.append({
                "列名": col,
                "类型": "数值",
                "风险等级": "高风险",
                "有效值数": 0,
                "缺失率": f"{missing_pct:.1f}%",
                "均值": "N/A",
                "标准差": "N/A",
                "最小值": "N/A",
                "最大值": "N/A",
                "异常值数": 0,
                "异常值占比": "0%",
                "零值占比": "0%",
                "负值占比": "0%",
                "重复值占比": "0%",
                "变异系数": "N/A",
                "异常说明": "全为缺失值"
            })
            continue
        
        # 有有效数据时进行统计分析
        # 基础统计
        mean_val = data.mean()
        std_val = data.std()
        min_val = data.min()
        max_val = data.max()
        
        # 异常值检测（基于 IQR）
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = data[(data < lower_bound) | (data > upper_bound)].count()
        outlier_pct = outliers / valid_count * 100
        
        # 零值占比
        zero_count = (data == 0).sum()
        zero_pct = zero_count / valid_count * 100
        
        # 负值占比
        negative_count = (data < 0).sum()
        negative_pct = negative_count / valid_count * 100
        
        # 重复值占比（数值完全相同）
        duplicate_count = data.duplicated().sum()
        duplicate_pct = duplicate_count / valid_count * 100
        
        # 变异系数
        cv = std_val / mean_val if mean_val != 0 else None
        
        # 异常判定规则
        anomalies = []
        risk_level = "正常"
        
        # 缺失值检查
        if missing_pct > 50:
            anomalies.append(f"缺失值过高 ({missing_pct:.1f}%)")
            risk_level = "高风险"
        elif missing_pct > 20:
            anomalies.append(f"缺失值较高 ({missing_pct:.1f}%)")
            risk_level = "中风险" if risk_level == "正常" else risk_level
        
        # 异常值检查
        if outlier_pct > 20:
            anomalies.append(f"异常值过高 ({outlier_pct:.1f}%)")
            risk_level = "高风险"
        elif outlier_pct > 10:
            anomalies.append(f"异常值较高 ({outlier_pct:.1f}%)")
            risk_level = "中风险" if risk_level == "正常" else risk_level
        
        # 零值检查
        if zero_pct > 90:
            anomalies.append(f"零值占比过高 ({zero_pct:.1f}%)")
            risk_level = "高风险"
        elif zero_pct > 50:
            anomalies.append(f"零值占比较高 ({zero_pct:.1f}%)")
            risk_level = "中风险" if risk_level == "正常" else risk_level
        
        # 负值检查（如果业务上不应该有负数）
        if negative_pct > 10:
            anomalies.append(f"负值占比较高 ({negative_pct:.1f}%)")
            risk_level = "中风险" if risk_level == "正常" else risk_level
        
        # 重复值检查
        if duplicate_pct > 90:
            anomalies.append(f"重复值过高 ({duplicate_pct:.1f}%)")
            risk_level = "高风险"
        elif duplicate_pct > 50:
            anomalies.append(f"重复值较高 ({duplicate_pct:.1f}%)")
            risk_level = "中风险" if risk_level == "正常" else risk_level
        
        # 常数列检查
        if std_val == 0:
            anomalies.append("常数列（所有值相同）")
            risk_level = "高风险"
        
        # 变异系数异常
        if cv is not None and cv > 10:
            anomalies.append(f"变异系数过高 ({cv:.2f})")
            risk_level = "中风险" if risk_level == "正常" else risk_level
        
        if not anomalies:
            anomalies.append("分布正常")
        
        quality_stats.append({
            "列名": col,
            "类型": "数值",
            "风险等级": risk_level,
            "有效值数": valid_count,
            "缺失率": f"{missing_pct:.1f}%",
            "均值": f"{mean_val:.2f}",
            "标准差": f"{std_val:.2f}",
            "最小值": f"{min_val:.2f}",
            "最大值": f"{max_val:.2f}",
            "异常值数": outliers,
            "异常值占比": f"{outlier_pct:.1f}%",
            "零值占比": f"{zero_pct:.1f}%",
            "负值占比": f"{negative_pct:.1f}%",
            "重复值占比": f"{duplicate_pct:.1f}%",
            "变异系数": f"{cv:.2f}" if cv else "N/A",
            "异常说明": "、".join(anomalies)
        })
    
    # 显示结果
    quality_df = pd.DataFrame(quality_stats)
    
    # 风险等级着色
    def color_risk(val):
        if val == "高风险":
            return 'background-color: #ffcccc'
        elif val == "中风险":
            return 'background-color: #fff3cd'
        elif val == "低风险":
            return 'background-color: #d1ecf1'
        return ''
    
    st.dataframe(
        quality_df.style.applymap(color_risk, subset=['风险等级']),
        use_container_width=True,
        hide_index=True
    )
    
    # 风险汇总
    high_risk = quality_df[quality_df["风险等级"] == "高风险"]
    mid_risk = quality_df[quality_df["风险等级"] == "中风险"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("高风险列", len(high_risk), delta=None)
    with col2:
        st.metric("中风险列", len(mid_risk), delta=None)
    with col3:
        st.metric("正常列", len(quality_df) - len(high_risk) - len(mid_risk), delta=None)
    
    if len(high_risk) > 0:
        st.warning(f"⚠️ 发现 {len(high_risk)} 个高风险列，建议检查数据质量")
        with st.expander("查看高风险列详情"):
            st.dataframe(high_risk[["列名", "类型", "异常说明"]], use_container_width=True, hide_index=True)
    elif len(mid_risk) > 0:
        st.info(f"📊 发现 {len(mid_risk)} 个中风险列，可能存在数据倾斜或异常")
    else:
        st.success("✅ 所有列分布正常")
        

def render_descriptive_stats_with_chart():
    """数据概览（增强版）"""
    st.markdown("#### 📊 数据概览")
    
    df = st.session_state.df
    
    # ========== 基本信息 ==========
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
    
    # ========== 列信息 ==========
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
    
    # ========== 数值列统计 ==========
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if numeric_cols:
        # 基础统计
        st.markdown("##### 数值列统计摘要")
        desc_df = df[numeric_cols].describe(percentiles=[.25, .5, .75]).round(2)
        desc_df = desc_df.reset_index()
        desc_df = desc_df.rename(columns={"index": "统计指标"})
        desc_df = desc_df.reset_index(drop=True)
        st.dataframe(desc_df, use_container_width=True, hide_index=True)
        
        # 高级统计（偏度、峰度、变异系数、标准误、异常值）
        with st.expander("📈 高级统计指标（偏度/峰度/变异系数/标准误/异常值）"):
            advanced_stats = []
            for col in numeric_cols:
                data = df[col].dropna()
                if len(data) > 0:
                    q1 = data.quantile(0.25)
                    q3 = data.quantile(0.75)
                    iqr = q3 - q1
                    cv = data.std() / data.mean() if data.mean() != 0 else None
                    sem = data.std() / (len(data) ** 0.5)
                    
                    # 异常值检测（基于 IQR）
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    outliers = data[(data < lower_bound) | (data > upper_bound)].count()
                    
                    advanced_stats.append({
                        "列名": col,
                        "偏度": round(data.skew(), 4),
                        "峰度": round(data.kurtosis(), 4),
                        "变异系数(CV)": round(cv, 4) if cv else None,
                        "标准误(SEM)": round(sem, 4),
                        "四分位距(IQR)": round(iqr, 2),
                        "异常值数": outliers,
                        "异常值占比": f"{outliers/len(data)*100:.1f}%"
                    })
            adv_df = pd.DataFrame(advanced_stats)
            st.dataframe(adv_df, use_container_width=True, hide_index=True)
        
        # 分段统计（等频分段）
        with st.expander("📊 分段统计（等频分段）"):
            st.caption("将数据按数值大小等分为5段，统计每段的数量和占比")
            
            segment_stats = []
            for col in numeric_cols:
                data = df[col].dropna()
                if len(data) > 0:
                    labels = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]
                    try:
                        segments = pd.qcut(data, q=5, labels=labels, duplicates='drop')
                        segment_counts = segments.value_counts().sort_index()
                        bounds = pd.qcut(data, q=5, retbins=True, duplicates='drop')[1]
                        
                        cumulative = 0
                        for i, label in enumerate(labels[:len(segment_counts)]):
                            if i < len(bounds) - 1:
                                range_str = f"[{bounds[i]:.2f}, {bounds[i+1]:.2f}]"
                            else:
                                range_str = f">{bounds[-2]:.2f}"
                            
                            count = segment_counts.get(label, 0)
                            cumulative += count
                            segment_stats.append({
                                "列名": col,
                                "分段": label,
                                "数值范围": range_str,
                                "数量": count,
                                "占比": f"{count/len(data)*100:.1f}%",
                                "累计占比": f"{cumulative/len(data)*100:.1f}%"
                            })
                    except Exception as e:
                        segment_stats.append({
                            "列名": col,
                            "分段": "分段失败",
                            "数值范围": str(e),
                            "数量": 0,
                            "占比": "0%",
                            "累计占比": "0%"
                        })
            
            if segment_stats:
                segment_df = pd.DataFrame(segment_stats)
                st.dataframe(segment_df, use_container_width=True, hide_index=True)
                
                # 可视化分段分布
                st.markdown("##### 分段分布可视化")
                for col in numeric_cols[:3]:
                    col_data = segment_df[segment_df["列名"] == col]
                    if not col_data.empty:
                        import plotly.express as px
                        fig = px.bar(
                            col_data,
                            x="分段",
                            y="数量",
                            title=f"{col} 分段分布",
                            text="占比",
                            color="分段"
                        )
                        fig.update_traces(textposition='outside')
                        fig.update_layout(showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("没有数值类型的列")
    
    st.markdown("---")
    
    # ========== 文本列统计 ==========
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    if text_cols:
        st.markdown("##### 文本列统计摘要")
        
        text_stats = []
        for col in text_cols:
            unique_count = df[col].nunique()
            total_count = len(df[col])
            mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
            mode_count = df[col].value_counts().iloc[0] if len(df[col].value_counts()) > 0 else 0
            
            text_stats.append({
                "列名": col,
                "总记录数": total_count,
                "唯一值数": unique_count,
                "唯一值占比": f"{unique_count / total_count * 100:.1f}%",
                "最频繁值": mode_val,
                "最频繁值出现次数": mode_count,
                "最频繁值占比": f"{mode_count / total_count * 100:.1f}%" if mode_count > 0 else "0%",
                "缺失值": df[col].isna().sum()
            })
        
        text_stats_df = pd.DataFrame(text_stats)
        text_stats_df = text_stats_df.reset_index(drop=True)
        st.dataframe(text_stats_df, use_container_width=True, hide_index=True)
        
        # 文本长度统计
        with st.expander("📏 文本长度统计"):
            length_stats = []
            for col in text_cols:
                lengths = df[col].astype(str).str.len()
                length_stats.append({
                    "列名": col,
                    "最小长度": int(lengths.min()),
                    "最大长度": int(lengths.max()),
                    "平均长度": round(lengths.mean(), 1),
                    "中位长度": int(lengths.median()),
                    "空字符串数": (df[col].astype(str) == "").sum()
                })
            length_df = pd.DataFrame(length_stats)
            st.dataframe(length_df, use_container_width=True, hide_index=True)
        
        # 频数分布（前10个值）
        with st.expander("📊 频数分布（前10个值）"):
            for col in text_cols[:3]:
                st.markdown(f"**{col}**")
                freq = df[col].value_counts().head(10).reset_index()
                freq.columns = [col, "频数"]
                freq['占比'] = (freq['频数'] / len(df[col]) * 100).round(1).astype(str) + '%'
                freq = freq.reset_index(drop=True)
                st.dataframe(freq, use_container_width=True, hide_index=True)
                st.markdown("---")
            
            if len(text_cols) > 3:
                st.info(f"还有 {len(text_cols) - 3} 列未显示，可导出完整统计")
    else:
        st.info("没有文本类型的列")
    
    # ========== 数据质量分析 ==========
    st.markdown("---")
    render_data_quality_analysis()
    
    # ========== 导出统计结果 ==========
    st.markdown("##### 导出统计结果")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 导出完整统计报告", key="export_full_stats", use_container_width=True):
            # 构建 Excel 报告
            with pd.ExcelWriter('data_overview.xlsx') as writer:
                # 基本信息
                basic_info = pd.DataFrame({
                    "指标": ["总行数", "总列数", "缺失值总数", "内存占用(MB)"],
                    "值": [len(df), len(df.columns), missing_count, f"{memory_usage:.2f}"]
                })
                basic_info.to_excel(writer, sheet_name='基本信息', index=False)
                
                # 列信息
                col_info_df.to_excel(writer, sheet_name='列信息', index=False)
                
                # 数值统计
                if numeric_cols:
                    desc_df.to_excel(writer, sheet_name='数值统计', index=False)
                
                # 文本统计
                if text_cols:
                    text_stats_df.to_excel(writer, sheet_name='文本统计', index=False)
                
                # 高级统计
                if 'adv_df' in locals():
                    adv_df.to_excel(writer, sheet_name='高级统计', index=False)
                
                # 分段统计
                if 'segment_df' in locals() and not segment_df.empty:
                    segment_df.to_excel(writer, sheet_name='分段统计', index=False)
            
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
            # 构建 CSV 报告
            all_stats = []
            for col in numeric_cols:
                row = {"列名": col, "类型": "数值"}
                # 基础统计
                for stat in desc_df["统计指标"]:
                    if stat in df[col].describe().index:
                        row[stat] = round(df[col].describe()[stat], 2)
                # 高级统计
                for adv in advanced_stats:
                    if adv["列名"] == col:
                        row["偏度"] = adv["偏度"]
                        row["峰度"] = adv["峰度"]
                        row["变异系数"] = adv["变异系数(CV)"]
                        row["异常值数"] = adv["异常值数"]
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
    """深度分析 - 支持下钻的多种图表"""
    st.markdown("#### 🔍 深度分析")
    
    df = st.session_state.df
    
    # 获取所有列
    all_cols = df.columns.tolist()
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if not numeric_cols:
        st.warning("需要数值列才能进行深度分析")
        return
    
    # 图表类型选择
    st.markdown("##### 图表类型")
    chart_type = st.radio(
        "选择图表类型",
        ["饼图", "柱状图", "条形图", "折线图"],
        key="depth_chart_type",
        horizontal=True
    )
    
    # 层级设置
    st.markdown("##### 层级设置")
    st.caption("按选择顺序作为下钻层级（第一级 → 第二级 → ...）")
    
    level_cols = st.multiselect(
        "选择分类列（按顺序选择）",
        all_cols,
        key="depth_levels",
        placeholder="请至少选择一个分类列"
    )
    
    # 数值列选择
    value_col = st.selectbox(
        "数值列",
        numeric_cols,
        key="depth_value"
    )
    
    if not level_cols:
        st.info("请至少选择一个分类列")
        return
    
    # 显示层级预览
    with st.expander("📊 下钻层级预览"):
        st.write("下钻顺序：")
        for i, col in enumerate(level_cols):
            st.write(f"  {i+1}. {col}")
        st.write(f"数值列：{value_col}")
    
    # 饼图模式选项（仅饼图时显示）
    pie_mode = None
    if chart_type == "饼图":
        st.markdown("##### 饼图模式")
        pie_mode = st.radio(
            "选择饼图模式",
            ["交互下钻", "子图布局", "南丁格尔玫瑰图", "复合定位"],
            key="depth_pie_mode",
            horizontal=True
        )
    
    # 高级选项
    with st.expander("高级选项"):
        max_categories = st.slider(
            "最大显示类别数",
            min_value=3,
            max_value=15,
            value=11,
            key="depth_max_cat",
            help="超过此数量的类别将合并为'其他'"
        )
        format_numbers = st.checkbox("格式化数值（万/亿）", value=True, key="depth_format")
    
    # ========== 深度分析状态 ==========
    if 'depth_path' not in st.session_state:
        st.session_state.depth_path = []
    if 'depth_selected' not in st.session_state:
        st.session_state.depth_selected = None
    
    # ========== 重置按钮 ==========
    col_reset, col_empty = st.columns([1, 5])
    with col_reset:
        if st.button("🔄 重置", key="depth_reset"):
            st.session_state.depth_path = []
            st.session_state.depth_selected = None
            st.rerun()
    
    # ========== 判断是否需要使用深度分析引擎 ==========
    # 需要深度分析的场景：
    # 1. 非饼图（柱状图、条形图、折线图）
    # 2. 饼图的交互下钻模式
    use_depth_engine = (chart_type != "饼图") or (pie_mode == "交互下钻")
    
    if use_depth_engine:
        # 使用深度分析引擎（支持下钻）
        from utils.depth_analysis import DepthAnalysisEngine
        
        engine = DepthAnalysisEngine()
        config = {
            'max_categories': max_categories,
            'format_numbers': format_numbers
        }
        
        engine.render(
            df=st.session_state.df,
            level_cols=level_cols,
            value_col=value_col,
            chart_type=chart_type,
            config=config
        )
    else:
        # 原有的复合饼图逻辑（子图布局、复合定位、玫瑰图）
        from utils.chart_generator import ChartGenerator
        
        fig = ChartGenerator.create_chart(
            df=st.session_state.df,
            chart_type="复合饼图",
            level_cols=level_cols,
            value_col=value_col,
            pie_mode=pie_mode,
            max_categories=max_categories,
            format_numbers=format_numbers,
            title=f"{value_col} 按 {' → '.join(level_cols)} 分布"
        )
        
        if fig:
            st.session_state.preview_manager.update_chart_preview(
                fig,
                f"深度分析-{pie_mode}"
            )
            st.success(f"{pie_mode}深度分析已生成，请查看主内容区")
        else:
            st.error("图表生成失败，请检查数据")