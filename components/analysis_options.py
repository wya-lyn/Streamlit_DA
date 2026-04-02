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
from utils.stats_analyzer import StatsAnalyzer
from utils.chart_generator import ChartGenerator
from components.group_stats_chart import GroupStatsChart
from utils.depth_analysis import DepthAnalysisEngine
from components.member_analysis import MemberAnalyzer

# ========== 全局辅助函数 ==========
def color_risk_by_level(val):
    """
    通用的风险等级着色函数
    支持会员分析风险等级和数据质量分析风险等级
    """
    if not isinstance(val, str):
        return ''
    
    color_map = {
        # 会员分析风险等级
        "异常": '#ff9999',      # 深红色
        "高危": '#ffcccc',      # 浅红色
        "风险": '#ffe0b3',      # 橙色
        "留意": '#d1ecf1',      # 浅蓝色
        # 数据质量分析风险等级
        "高风险": '#ffcccc',     # 浅红色
        "中风险": '#fff3cd',     # 浅黄色
        "低风险": '#d1ecf1',     # 浅蓝色
        # 正常（两个表都有，无背景色）
        "正常": '',
        "良好": '',
    }
    
    bg_color = color_map.get(val, '')
    return f'background-color: {bg_color}' if bg_color else ''

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
        "🥧 深度分析",
        "🎯 会员异常分析"
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
    with analysis_tabs[6]:  # 会员异常分析
        render_member_analysis_page()
        
def render_member_analysis_page():
    """会员异常分析页面"""
    st.markdown("#### 🎯 会员异常分析")
    
    df = st.session_state.df
    
    # 获取所有列
    all_cols = df.columns.tolist()
    
    
    # ========== 区块1：数据结构定义（数值/时间字段）==========
    st.markdown("##### 📁 数据结构定义")
    st.caption("请指定各列对应的业务含义")

    col1, col2, col3 = st.columns(3)
    with col1:
        member_col = st.selectbox("会员ID列", all_cols, key="member_col")
        bet_amount_col = st.selectbox("投注额列", all_cols, key="bet_amount_col")
    with col2:
        bet_time_col = st.selectbox("投注时间列(可选)", ["无"] + all_cols, key="bet_time_col")
        odds_col = st.selectbox("赔率列", all_cols, key="odds_col")
    with col3:
        win_loss_col = st.selectbox("输赢列", all_cols, key="win_loss_col")
        # 预留空位保持布局

    # ========== 区块2：分类层级定义（文本字段）==========
    st.markdown("##### 📊 分类层级定义")
    st.caption("按层级顺序选择分类列（体育类型 → 联赛 → 对阵 → 赛事状态 → 比赛阶段 → 玩法 → 下注项）")

    # 使用2列布局，共4行
    col1, col2 = st.columns(2)

    with col1:
        t1_col = st.selectbox("体育类型列", ["无"] + all_cols, key="t1_col")
        t3_col = st.selectbox("对阵列", ["无"] + all_cols, key="t3_col")
        t5_col = st.selectbox("比赛阶段列", ["无"] + all_cols, key="t5_col")

    with col2:
        t2_col = st.selectbox("联赛列", ["无"] + all_cols, key="t2_col")
        t4_col = st.selectbox("赛事状态列(滚球/赛前)", ["无"] + all_cols, key="t4_col")
        t6_col = st.selectbox("玩法列", ["无"] + all_cols, key="t6_col")

    # 下注项单独一行
    t7_col = st.selectbox("下注项列", ["无"] + all_cols, key="t7_col")
    
    # 构建映射
    mapping = {
            "member_id": member_col,
            "bet_amount": bet_amount_col,
            "odds": odds_col,
            "win_loss": win_loss_col,
            "bet_time": bet_time_col if bet_time_col != "无" else None,
            "t1": t1_col if t1_col != "无" else None,
            "t2": t2_col if t2_col != "无" else None,
            "t3": t3_col if t3_col != "无" else None,
            "t4": t4_col if t4_col != "无" else None,
            "t5": t5_col if t5_col != "无" else None,  # 比赛阶段
            "t6": t6_col if t6_col != "无" else None,  # 玩法
            "t7": t7_col if t7_col != "无" else None,  # 下注项
        }
            

    
    # 分析按钮
    if st.button("🔍 开始分析", key="member_analyze", type="primary"):
        with st.spinner("正在分析会员数据..."):
            try:
                
                analyzer = MemberAnalyzer(df.copy(), mapping)
                analyzer.preprocess_data()
                results = analyzer.run_analysis()
                raw_data = analyzer.member_stats
                
                
                # 逐列打印 raw_data
                if len(raw_data) > 0:
                    for col in raw_data.columns:
                        val = raw_data.iloc[0][col]
                
                # 保存到 session_state
                st.session_state.member_results = results
                st.session_state.member_raw_data = raw_data
                st.session_state.analysis_done = True
                st.session_state.mapping = mapping     
                st.session_state.original_df = df    
                
                st.success(f"分析完成！共分析 {len(results)} 个会员")
                st.rerun()
            except Exception as e:
                st.error(f"分析失败: {str(e)}")
                import traceback
                traceback.print_exc()
    
    # 显示结果
    if st.session_state.get('analysis_done', False):
        
        results = st.session_state.member_results
        raw_data = st.session_state.member_raw_data
        mapping = st.session_state.get('mapping', None)
        df_original = st.session_state.get('original_df', None)
        
        member_col = mapping["member_id"]
        
        # ========== 数据质量检测表 ==========
        st.markdown("##### 📊 数据质量检测表")
        st.caption("按会员统计的数据质量报告，订单数<10单显示'样本不足'")

        # 构建质量检测表数据
        quality_data = []

        for _, row in results.iterrows():
            member_id = row["会员ID"]
            bet_count = row.get("投注次数", 0)
            
            # 获取该会员的原始数据
            member_df = df_original[df_original[member_col] == member_id]
            
            # 基础信息
            quality_row = {
                "会员ID": member_id,
                "订单数": bet_count,
            }
            
            # 判断样本是否充足
            if bet_count < 10:
                # 样本不足，所有统计列显示"样本不足"
                quality_row["数据质量"] = "❌ 样本不足"
                quality_row["数据质量详情"] = f"订单数不足10单 ({bet_count}单)"
                
                # 文本列（t1-t7）
                for col_key in ['t1', 't2', 't3', 't4', 't5', 't6', 't7']:
                    actual_col_name = mapping.get(col_key)
                    if actual_col_name and actual_col_name in df_original.columns:
                        quality_row[f'{actual_col_name}_最高频值'] = "样本不足"
                        quality_row[f'{actual_col_name}_最高频占比'] = "样本不足"
                        quality_row[f'{actual_col_name}_唯一值数'] = "样本不足"
                
                # 数值列（赔率、投注额、输赢）
                for num_name in ['赔率', '投注额']:
                    quality_row[f'{num_name}_均值'] = "样本不足"
                    quality_row[f'{num_name}_标准差'] = "样本不足"
                    quality_row[f'{num_name}_最小值'] = "样本不足"
                    quality_row[f'{num_name}_最大值'] = "样本不足"
                    quality_row[f'{num_name}_变异系数'] = "样本不足"
                    quality_row[f'{num_name}_高频区间'] = "样本不足"

                # 输赢单独处理（只保留正负分布和倾向）
                quality_row["输赢_正负分布"] = "样本不足"
                quality_row["输赢_倾向"] = "样本不足"
                quality_data.append(quality_row)
                continue
            
            # ========== 样本充足，计算详细统计 ==========
            
            # 计算数据质量等级（使用评分）
            
            # 从 results 中直接获取风险等级
            risk_level = row.get("风险等级", "正常")

            # 根据 risk_level 设置数据质量
            if risk_level == "正常":
                quality_row["数据质量"] = "✅ 良好"
                quality_row["数据质量详情"] = "良好"
            elif risk_level == "留意":
                quality_row["数据质量"] = "⚠️ 中风险"
                quality_row["数据质量详情"] = "留意玩家 (需关注)"
            elif risk_level == "风险":
                quality_row["数据质量"] = "🔴 高风险"
                quality_row["数据质量详情"] = "风险玩家 (存在异常行为)"
            elif risk_level == "高危":
                quality_row["数据质量"] = "💀 严重异常"
                quality_row["数据质量详情"] = "高危玩家 (高度可疑)"
            elif risk_level == "异常":
                quality_row["数据质量"] = "💀 严重异常"
                quality_row["数据质量详情"] = "异常玩家 (强烈建议审查)"
            else:
                quality_row["数据质量"] = "❓ 未知"
                quality_row["数据质量详情"] = "无法判定"
            
            # 文本列统计
            # 文本列统计（使用实际列名）
            for col_key in ['t1', 't2', 't3', 't4', 't5', 't6', 't7']:
                actual_col_name = mapping.get(col_key)
                if actual_col_name and actual_col_name in df_original.columns:
                    member_cat_data = member_df[actual_col_name].dropna()
                    if len(member_cat_data) > 0:
                        value_counts = member_cat_data.value_counts()
                        top_value = value_counts.index[0] if len(value_counts) > 0 else "无数据"
                        top_pct = value_counts.iloc[0] / len(member_cat_data) if len(value_counts) > 0 else 0
                        unique_count = member_cat_data.nunique()
                        
                        quality_row[f'{actual_col_name}_最高频值'] = str(top_value)[:20] if top_value != "无数据" else "无数据"
                        quality_row[f'{actual_col_name}_最高频占比'] = f"{top_pct:.0%}" if top_pct > 0 else "0%"
                        quality_row[f'{actual_col_name}_唯一值数'] = str(unique_count)
                    else:
                        quality_row[f'{actual_col_name}_最高频值'] = "无数据"
                        quality_row[f'{actual_col_name}_最高频占比'] = "0%"
                        quality_row[f'{actual_col_name}_唯一值数'] = str(0)
            
            # 从 raw_data 获取统计（赔率、投注额、输赢）
            mr = raw_data[raw_data["会员ID"] == member_id].iloc[0] if len(raw_data[raw_data["会员ID"] == member_id]) > 0 else None
            
            if mr is not None:
                # ========== 赔率统计 ==========
                avg_odds = mr.get('平均赔率', 0) if not pd.isna(mr.get('平均赔率', 0)) else 0
                odds_std = mr.get('赔率标准差', 0) if not pd.isna(mr.get('赔率标准差', 0)) else 0
                odds_min = mr.get('单笔最小赔率', 0) if '单笔最小赔率' in mr.index and not pd.isna(mr.get('单笔最小赔率', 0)) else "N/A"
                odds_max = mr.get('单笔最大赔率', 0) if '单笔最大赔率' in mr.index and not pd.isna(mr.get('单笔最大赔率', 0)) else "N/A"
                odds_cv = mr.get('赔率变异系数', 0) if not pd.isna(mr.get('赔率变异系数', 0)) else 0

                quality_row["赔率_均值"] = f"{avg_odds:.2f}" if avg_odds > 0 else "N/A"
                quality_row["赔率_标准差"] = f"{odds_std:.2f}" if odds_std > 0 else "N/A"
                quality_row["赔率_最小值"] = f"{odds_min:.2f}" if odds_min != "N/A" and odds_min > 0 else "N/A"
                quality_row["赔率_最大值"] = f"{odds_max:.2f}" if odds_max != "N/A" and odds_max > 0 else "N/A"
                # 修复变异系数显示：区分0和N/A
                if odds_cv > 0:
                    quality_row["赔率_变异系数"] = f"{odds_cv:.2f}"
                elif odds_cv == 0:
                    quality_row["赔率_变异系数"] = "0.00"
                else:
                    quality_row["赔率_变异系数"] = "N/A"
                
                # 计算赔率高频区间（均值±10%）
                if avg_odds > 0:
                    lower = avg_odds * 0.85
                    upper = avg_odds * 1.15
                    
                    # 确保 lower 和 upper 是有效数值
                    if pd.isna(lower) or pd.isna(upper):
                        quality_row["赔率_高频区间"] = "N/A"
                    else:
                        odds_col = mapping.get("odds")
                        if odds_col and odds_col in member_df.columns:
                            # 确保赔率数据是数值类型
                            odds_data = pd.to_numeric(member_df[odds_col], errors='coerce').dropna()
                            # 过滤掉无效值（<=0 的赔率）
                            odds_data = odds_data[odds_data > 0]
                            
                            if len(odds_data) > 0:
                                try:
                                    in_range = odds_data[(odds_data >= lower) & (odds_data <= upper)].count()
                                    range_pct = in_range / len(odds_data) * 100
                                    quality_row["赔率_高频区间"] = f"[{lower:.2f}-{upper:.2f}] {range_pct:.0f}%"
                                except Exception as e:
                                    print(f"赔率高频区间计算异常: {e}")
                                    quality_row["赔率_高频区间"] = "N/A"
                            else:
                                quality_row["赔率_高频区间"] = "N/A"
                        else:
                            quality_row["赔率_高频区间"] = "N/A"
                else:
                    quality_row["赔率_高频区间"] = "N/A"
                
                # ========== 投注额统计 ==========
                avg_stake = mr.get('平均投注额', 0) if not pd.isna(mr.get('平均投注额', 0)) else 0
                stake_std = mr.get('投注额标准差', 0) if not pd.isna(mr.get('投注额标准差', 0)) else 0
                stake_min = mr.get('单笔最小投注', 0) if '单笔最小投注' in mr.index and not pd.isna(mr.get('单笔最小投注', 0)) else "N/A"
                stake_max = mr.get('单笔最大投注', 0) if '单笔最大投注' in mr.index and not pd.isna(mr.get('单笔最大投注', 0)) else "N/A"
                stake_cv = mr.get('投注额变异系数', 0) if not pd.isna(mr.get('投注额变异系数', 0)) else 0

                quality_row["投注额_均值"] = f"{avg_stake:.0f}" if avg_stake > 0 else "N/A"
                quality_row["投注额_标准差"] = f"{stake_std:.0f}" if stake_std > 0 else "N/A"
                quality_row["投注额_最小值"] = f"{stake_min:.0f}" if stake_min != "N/A" and stake_min > 0 else "N/A"
                quality_row["投注额_最大值"] = f"{stake_max:.0f}" if stake_max != "N/A" and stake_max > 0 else "N/A"
                # 修复变异系数显示：区分0和N/A
                if stake_cv > 0:
                    quality_row["投注额_变异系数"] = f"{stake_cv:.2f}"
                elif stake_cv == 0:
                    quality_row["投注额_变异系数"] = "0.00"
                else:
                    quality_row["投注额_变异系数"] = "N/A"
                
                # 计算投注额高频区间（均值±10%）
                if avg_stake > 0:
                    lower = avg_stake * 0.9
                    upper = avg_stake * 1.1
                    stake_col = mapping.get("bet_amount")
                    if stake_col and stake_col in member_df.columns:
                        stake_data = member_df[stake_col].dropna()
                        if len(stake_data) > 0:
                            in_range = stake_data[(stake_data >= lower) & (stake_data <= upper)].count()
                            range_pct = in_range / len(stake_data) * 100
                            quality_row["投注额_高频区间"] = f"[{lower:.0f}-{upper:.0f}] {range_pct:.0f}%"
                        else:
                            quality_row["投注额_高频区间"] = "N/A"
                    else:
                        quality_row["投注额_高频区间"] = "N/A"
                else:
                    quality_row["投注额_高频区间"] = "N/A"
                
                # ========== 输赢统计 ==========
                avg_winloss = mr.get('平均输赢', 0) if not pd.isna(mr.get('平均输赢', 0)) else 0
                winloss_std = mr.get('输赢标准差', 0) if not pd.isna(mr.get('输赢标准差', 0)) else 0
                winloss_min = mr.get('单笔最小输赢', 0) if '单笔最小输赢' in mr.index and not pd.isna(mr.get('单笔最小输赢', 0)) else "N/A"
                winloss_max = mr.get('单笔最大输赢', 0) if '单笔最大输赢' in mr.index and not pd.isna(mr.get('单笔最大输赢', 0)) else "N/A"
                winloss_cv = mr.get('输赢变异系数', 0) if not pd.isna(mr.get('输赢变异系数', 0)) else 0
                
                quality_row["输赢_均值"] = f"{avg_winloss:.2f}" if avg_winloss != 0 else "0.00"
                quality_row["输赢_标准差"] = f"{winloss_std:.2f}" if winloss_std > 0 else "N/A"
                quality_row["输赢_最小值"] = f"{winloss_min:.2f}" if winloss_min != "N/A" else "N/A"
                quality_row["输赢_最大值"] = f"{winloss_max:.2f}" if winloss_max != "N/A" else "N/A"
                quality_row["输赢_变异系数"] = f"{winloss_cv:.2f}" if winloss_cv > 0 else "N/A"
                
                # 输赢正负分布（直接从 raw_data 获取，如果没有则计算）
                # 输赢正负分布（直接从 raw_data 获取，如果没有则计算）
                if '输赢_正负分布' in mr.index and not pd.isna(mr.get('输赢_正负分布')):
                    quality_row["输赢_正负分布"] = mr.get('输赢_正负分布')
                else:
                    # 计算输赢正负分布
                    winloss_col = mapping.get("win_loss")
                    if winloss_col and winloss_col in member_df.columns:
                        winloss_data = member_df[winloss_col].dropna()
                        if len(winloss_data) > 0:
                            pos_count = (winloss_data > 0).sum()
                            neg_count = (winloss_data < 0).sum()
                            zero_count = (winloss_data == 0).sum()
                            total = len(winloss_data)
                            quality_row["输赢_正负分布"] = f"正{pos_count/total*100:.0f}% / 负{neg_count/total*100:.0f}% / 零{zero_count/total*100:.0f}%"
                        else:
                            quality_row["输赢_正负分布"] = "无数据"
                    else:
                        quality_row["输赢_正负分布"] = "N/A"

                # 输赢倾向（按求和）
                if '输赢_倾向' in mr.index and not pd.isna(mr.get('输赢_倾向')):
                    quality_row["输赢_倾向"] = mr.get('输赢_倾向')
                else:
                    winloss_col = mapping.get("win_loss")
                    if winloss_col and winloss_col in member_df.columns:
                        winloss_data = member_df[winloss_col].dropna()
                        if len(winloss_data) > 0:
                            total_winloss = winloss_data.sum()
                            if total_winloss > 0:
                                quality_row["输赢_倾向"] = "盈利"
                            elif total_winloss < 0:
                                quality_row["输赢_倾向"] = "亏损"
                            else:
                                quality_row["输赢_倾向"] = "平衡"
                        else:
                            quality_row["输赢_倾向"] = "无数据"
                    else:
                        quality_row["输赢_倾向"] = "N/A"
            else:
                # raw_data 中无数据，填充 N/A
                for col in ['赔率_均值', '赔率_标准差', '赔率_最小值', '赔率_最大值', '赔率_变异系数', '赔率_高频区间',
                        '投注额_均值', '投注额_标准差', '投注额_最小值', '投注额_最大值', '投注额_变异系数', '投注额_高频区间',
                        '输赢_正负分布', '输赢_倾向']:
                    quality_row[col] = "N/A"
            
            quality_data.append(quality_row)
        
        # 创建 DataFrame
        quality_df = pd.DataFrame(quality_data)
        
        # 调整列顺序
        column_order = ["会员ID", "数据质量", "数据质量详情", "订单数"]
        
        # 添加文本列
        for col_key in ['t1', 't2', 't3', 't4', 't5', 't6', 't7']:
            actual_col_name = mapping.get(col_key)
            if actual_col_name and actual_col_name in df_original.columns:
                column_order.extend([f'{actual_col_name}_最高频值', f'{actual_col_name}_最高频占比', f'{actual_col_name}_唯一值数'])
        
        # 添加数值列
        num_cols_order = [
            '赔率_均值', '赔率_标准差', '赔率_最小值', '赔率_最大值', '赔率_变异系数', '赔率_高频区间',
            '投注额_均值', '投注额_标准差', '投注额_最小值', '投注额_最大值', '投注额_变异系数', '投注额_高频区间',
            '输赢_正负分布', '输赢_倾向'
        ]
        
        for col in num_cols_order:
            if col in quality_df.columns:
                column_order.append(col)
        
        # 只保留存在的列
        column_order = [col for col in column_order if col in quality_df.columns]
        quality_df = quality_df[column_order]
        
        # 显示表格
        st.dataframe(quality_df, use_container_width=True, hide_index=True)
        
        # 导出按钮
        csv = quality_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 导出数据质量检测表",
            data=csv,
            file_name=f"data_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="export_quality"
        )
        
        # ========== 统计摘要 ==========
        st.markdown("---")
        st.markdown("##### 📊 风险等级分布")
        
        # 风险等级分布
        if "风险等级" in results.columns:
            risk_dist = results["风险等级"].value_counts().reset_index()
            risk_dist.columns = ["风险等级", "会员数"]
            st.dataframe(risk_dist, use_container_width=True, hide_index=True)
        
        # 会员性质分布
        st.markdown("##### 📊 会员性质分布")
        if "会员性质" in results.columns:
            type_dist = results["会员性质"].value_counts().reset_index()
            type_dist.columns = ["会员性质", "会员数"]
            st.dataframe(type_dist, use_container_width=True, hide_index=True)
            
        #-----质量分析-----
        
        # ========== 详细会员画像表格 ==========
        st.markdown("##### 📋 详细会员画像")

        # 辅助函数
        def get_pct(val):
            if val is None or pd.isna(val):
                return "0%"
            return f"{val:.0%}"

        # 玩法分布辅助函数
        def get_top_plays(member_id):
            """获取前3个玩法及占比"""
            try:
                play_col = mapping.get("t6")  # 新玩法列（t6）
                if not play_col or play_col not in df.columns:
                    return "无玩法数据"
                
                member_data = df[df[member_col] == member_id]
                if len(member_data) == 0:
                    return "无数据"
                
                play_counts = member_data[play_col].value_counts()
                total = len(member_data)
                
                if len(play_counts) == 0:
                    return "无数据"
                
                top_plays = []
                for i, (play, count) in enumerate(play_counts.head(3).items()):
                    pct = count / total * 100
                    play_name = str(play)[:15] + "..." if len(str(play)) > 15 else str(play)
                    top_plays.append(f"{play_name}({pct:.0f}%)")
                
                if len(play_counts) > 3:
                    other_pct = play_counts.iloc[3:].sum() / total * 100
                    top_plays.append(f"其他({other_pct:.0f}%)")
                
                return " / ".join(top_plays)
            except Exception as e:
                return "计算失败"

        display_data = []
        low_order_count = 0  # 订单数不足的会员计数

        for idx, row in results.iterrows():
            member_id = row["会员ID"]
            bet_count = row.get("投注次数", 0)
            
            # 过滤订单数不足的会员（订单数 < 10）
            if bet_count < 10:
                low_order_count += 1
                continue
            
            # 从 raw_data 获取详细分布
            member_raw = raw_data[raw_data["会员ID"] == member_id]
            if len(member_raw) == 0:
                continue
            mr = member_raw.iloc[0]
            
            # 赔率分布（使用边界列）
            odds_boundary_1 = mr.get('赔率_段1_边界', '【0】')
            odds_boundary_2 = mr.get('赔率_段2_边界', '【0】')
            odds_boundary_3 = mr.get('赔率_段3_边界', '【0】')
            odds_boundary_4 = mr.get('赔率_段4_边界', '【0】')
            odds_boundary_5 = mr.get('赔率_段5_边界', '【0】')
            
            odds_p1 = mr.get('赔率_段1占比', 0)
            odds_p2 = mr.get('赔率_段2占比', 0)
            odds_p3 = mr.get('赔率_段3占比', 0)
            odds_p4 = mr.get('赔率_段4占比', 0)
            odds_p5 = mr.get('赔率_段5占比', 0)
            
            odds_dist = f"{odds_boundary_1}{get_pct(odds_p1)} / {odds_boundary_2}{get_pct(odds_p2)} / {odds_boundary_3}{get_pct(odds_p3)} / {odds_boundary_4}{get_pct(odds_p4)} / {odds_boundary_5}{get_pct(odds_p5)}"
            
            # 投注额分布（使用边界列）
            stake_boundary_1 = mr.get('投注额_段1_边界', '【0】')
            stake_boundary_2 = mr.get('投注额_段2_边界', '【0】')
            stake_boundary_3 = mr.get('投注额_段3_边界', '【0】')
            stake_boundary_4 = mr.get('投注额_段4_边界', '【0】')
            stake_boundary_5 = mr.get('投注额_段5_边界', '【0】')
            
            stake_p1 = mr.get('投注额_段1占比', 0)
            stake_p2 = mr.get('投注额_段2占比', 0)
            stake_p3 = mr.get('投注额_段3占比', 0)
            stake_p4 = mr.get('投注额_段4占比', 0)
            stake_p5 = mr.get('投注额_段5占比', 0)
            
            stake_dist = f"{stake_boundary_1}{get_pct(stake_p1)} / {stake_boundary_2}{get_pct(stake_p2)} / {stake_boundary_3}{get_pct(stake_p3)} / {stake_boundary_4}{get_pct(stake_p4)} / {stake_boundary_5}{get_pct(stake_p5)}"
            
            # 输赢分布（使用边界列）
            winloss_boundary_1 = mr.get('输赢_段1_边界', '【0】')
            winloss_boundary_2 = mr.get('输赢_段2_边界', '【0】')
            winloss_boundary_3 = mr.get('输赢_段3_边界', '【0】')
            winloss_boundary_4 = mr.get('输赢_段4_边界', '【0】')
            winloss_boundary_5 = mr.get('输赢_段5_边界', '【0】')
            
            winloss_p1 = mr.get('输赢_段1占比', 0)
            winloss_p2 = mr.get('输赢_段2占比', 0)
            winloss_p3 = mr.get('输赢_段3占比', 0)
            winloss_p4 = mr.get('输赢_段4占比', 0)
            winloss_p5 = mr.get('输赢_段5占比', 0)
            
            winloss_dist = f"{winloss_boundary_1}{get_pct(winloss_p1)} / {winloss_boundary_2}{get_pct(winloss_p2)} / {winloss_boundary_3}{get_pct(winloss_p3)} / {winloss_boundary_4}{get_pct(winloss_p4)} / {winloss_boundary_5}{get_pct(winloss_p5)}"
            
            # 玩法分布
            play_dist = get_top_plays(member_id)
            
            # 集中度（5个指标）
            sport_conc = mr.get('t1_集中度', 0)      # 体育类型
            league_conc = mr.get('t2_集中度', 0)     # 联赛
            status_conc = mr.get('t4_集中度', 0)     # 赛事状态（原 t4）
            stage_conc = mr.get('t5_集中度', 0)      # 比赛阶段（新 t5）
            play_conc = mr.get('t6_集中度', 0)       # 玩法（原 t5，现 t6）

            concentration = f"体育{get_pct(sport_conc)} 联赛{get_pct(league_conc)} 状态{get_pct(status_conc)} 阶段{get_pct(stage_conc)} 玩法{get_pct(play_conc)}"
            
            # 其他指标
            odds_cv = mr.get('赔率变异系数', 0)
            stake_cv = mr.get('投注额变异系数', 0)
            if pd.isna(odds_cv):
                other_metrics = "N/A"
            else:
                other_metrics = f"赔率CV={odds_cv:.2f} 投注CV={stake_cv:.2f}"
            
            # 验证详情
            details = row.get("验证详情", "")
            if isinstance(details, list):
                details = " | ".join(details) if details else "无"
            
            matched_type_str = row.get("匹配类型", "")

            display_data.append({
                "会员ID": member_id,
                "会员性质": row.get("会员性质", "未知"),
                "风险等级": row.get("风险等级", "正常"),
                "赔率分布": odds_dist,
                "投注额分布": stake_dist,
                "输赢分布": winloss_dist,
                "玩法分布": play_dist,
                "集中度": concentration,
                "其他指标": other_metrics,
                "匹配类型": matched_type_str,  # 新增
                "验证详情": details
            })
        # 显示过滤提示
        if low_order_count > 0:
            st.warning(f"⚠️ 订单数少于10单的会员（共 {low_order_count} 人）已从详细画像中过滤，详见风险等级分布。")
            st.caption("提示：订单数过少的会员分析价值较低，已自动隐藏。")

        if display_data:
            display_df = pd.DataFrame(display_data)
            # 调整列顺序
            column_order = ["会员ID", "会员性质", "风险等级", "赔率分布", "投注额分布", "输赢分布", 
                "玩法分布", "集中度", "其他指标", "匹配类型", "验证详情"]
            display_df = display_df[column_order]
            
            # 风险等级筛选
            risk_filter = st.multiselect(
                "筛选风险等级",
                ["正常", "留意", "风险", "高危", "异常"],
                default=["高危", "风险", "留意", "异常"],
                key="risk_filter"
            )
            
            filtered = display_df[display_df["风险等级"].isin(risk_filter)]
            
            # 颜色标记函数
            def color_risk(val):
                if val == "异常":
                    return 'background-color: #ff9999'
                elif val == "高危":
                    return 'background-color: #ffcccc'
                elif val == "风险":
                    return 'background-color: #ffe0b3'
                elif val == "留意":
                    return 'background-color: #d1ecf1'
                return ''
            
            # 显示表格
            st.dataframe(
            filtered.style.applymap(color_risk_by_level, subset=["风险等级"]),
            use_container_width=True,
            hide_index=True
            )
            
            # 导出按钮
            csv = filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 导出会员画像",
                data=csv,
                file_name=f"member_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="export_member"
            )
        else:
            if low_order_count > 0:
                st.info(f"所有 {low_order_count} 个会员订单数均不足10单，无法生成详细画像。")
            else:
                st.info("没有生成会员画像数据")
    else:
        st.info("请配置数据结构后点击「开始分析」")
        
def render_data_quality_analysis():
    """数据质量分析（异常检测）"""
    st.markdown("##### ⚠️ 数据质量分析")
    st.caption("通过频度分布检测数据是否可能存在异常（如机器操作、数据倾斜等）")
    
    df = st.session_state.df
    
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
            
            # 确保最频繁值转换为字符串
            top_value = value_counts.index[0] if len(value_counts) > 0 else "无"
            top_value_str = str(top_value)[:30] if top_value != "无" else "无"
            
            quality_stats.append({
                "列名": col,
                "类型": "文本",
                "风险等级": risk_level,
                "唯一值数": unique,
                "唯一值占比": f"{unique_pct:.1f}%",
                "最频繁值": top_value_str,
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
    
    # ========== 显示结果 ==========
    quality_df = pd.DataFrame(quality_stats)
    
    # 检查风险等级列是否存在
    if '风险等级' in quality_df.columns:
        # 确保风险等级列是字符串类型
        quality_df['风险等级'] = quality_df['风险等级'].astype(str)
        
        st.dataframe(
            quality_df.style.applymap(color_risk_by_level, subset=['风险等级']),
            use_container_width=True,
            hide_index=True
        )
    else:
        # 如果没有风险等级列，直接显示表格
        st.dataframe(quality_df, use_container_width=True, hide_index=True)
    
    # ========== 风险汇总 ==========
    if '风险等级' in quality_df.columns:
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
    else:
        st.info("无法进行风险等级汇总")
        

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
            mode_val_str = str(mode_val) if mode_val != "N/A" else "N/A"
            
            text_stats.append({
                "列名": col,
                "总记录数": total_count,
                "唯一值数": unique_count,
                "唯一值占比": f"{unique_count / total_count * 100:.1f}%",
                "最频繁值": mode_val_str,
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