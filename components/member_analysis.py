"""
会员异常分析模块
用于检测会员投注行为异常
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px


class MemberAnalyzer:
    """会员异常分析器"""
    
    def __init__(self, df, mapping):
        """
        初始化分析器
        
        Parameters:
        -----------
        df : DataFrame
            原始数据
        mapping : dict
            列名映射
        """
        self.df = df
        self.mapping = mapping
        self.member_stats = None
        self.results = None
        
    def get_column_info(self):
        """获取列信息用于调试"""
        return {
            "原始列名": self.df.columns.tolist(),
            "映射配置": {k: v for k, v in self.mapping.items() if v is not None}
        }
    
    def preprocess_data(self):
        """数据预处理"""
        # 时间列转换
        if self.mapping.get("bet_time"):
            self.df[self.mapping["bet_time"]] = pd.to_datetime(
                self.df[self.mapping["bet_time"]], errors='coerce'
            )
        
        # 数值列转换 - 先转为字符串清理，再转数值
        num_cols = [self.mapping["bet_amount"], self.mapping["win_loss"], self.mapping["odds"]]
        for col in num_cols:
            if col in self.df.columns:
                # 先转为字符串，清理特殊字符
                self.df[col] = self.df[col].astype(str)
                # 移除千分位逗号、空格等
                self.df[col] = self.df[col].str.replace(',', '')
                self.df[col] = self.df[col].str.strip()
                # 转为数值
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        return self
    
    def aggregate_member_data(self):
        """按会员聚合统计数据"""
        df = self.df.copy()
        
        # ========== 1. 数据清洗 ==========
        member_col = self.mapping["member_id"]
        
        # 文本列：填充空值为"未知"
        text_cols = ['t1', 't2', 't3', 't4', 't5', 't6']
        for col_key in text_cols:
            col_name = self.mapping.get(col_key)
            if col_name and col_name in df.columns:
                df[col_name] = df[col_name].fillna("未知").astype(str)
        
        # 数值列：转换为数值，空值填充0
        num_cols = [self.mapping["bet_amount"], self.mapping["win_loss"], self.mapping["odds"]]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # 时间列处理
        if self.mapping.get("bet_time") and self.mapping["bet_time"] in df.columns:
            df[self.mapping["bet_time"]] = pd.to_datetime(df[self.mapping["bet_time"]], errors='coerce')
        
        # ========== 2. 基础聚合统计 ==========
        member_group = df.groupby(member_col)

        bet_stats = member_group.agg({
            self.mapping["bet_amount"]: ['sum', 'mean', 'min', 'max', 'count', 'std'],
            self.mapping["win_loss"]: ['sum', 'mean', 'min', 'max', 'std'],
            self.mapping["odds"]: ['mean', 'min', 'max', 'std']
        }).reset_index()

        bet_stats.columns = [
            '会员ID', '总投注额', '平均投注额', '单笔最小投注', '单笔最大投注', '投注次数', '投注额标准差',
            '总输赢', '平均输赢', '单笔最小输赢', '单笔最大输赢', '输赢标准差',
            '平均赔率', '单笔最小赔率', '单笔最大赔率', '赔率标准差'
        ]
        
        # ========== 3. 时间间隔分析 ==========
        if self.mapping.get("bet_time") and self.mapping["bet_time"] in df.columns:
            df_sorted = df.sort_values([member_col, self.mapping["bet_time"]])
            df_sorted['间隔秒数'] = df_sorted.groupby(member_col)[self.mapping["bet_time"]].diff().dt.total_seconds()
            interval_stats = df_sorted.groupby(member_col)['间隔秒数'].agg(['min', 'mean']).reset_index()
            interval_stats.columns = ['会员ID', '最小间隔秒数', '平均间隔秒数']
            bet_stats = bet_stats.merge(interval_stats, on='会员ID', how='left').fillna(0)
        
        # ========== 4. 文本列集中度分析 ==========
        concentration_fields = ['t1', 't2', 't4', 't5', 't6']

        for col_key in concentration_fields:
            col_name = self.mapping.get(col_key)
            if col_name and col_name in df.columns:
                member_cat = df.groupby([member_col, col_name]).size().reset_index(name='计数')
                member_total = member_cat.groupby(member_col)['计数'].sum().reset_index(name='总数')
                member_max = member_cat.groupby(member_col)['计数'].max().reset_index(name='最大计数')
                member_max = member_max.merge(member_total, on=member_col)
                member_max[f'{col_key}_集中度'] = member_max['最大计数'] / member_max['总数']
                member_max = member_max.rename(columns={member_col: '会员ID'})
                bet_stats = bet_stats.merge(member_max[['会员ID', f'{col_key}_集中度']], on='会员ID', how='left').fillna(0)
        
        # ========== 5. 赔率分段分析（核心修复） ==========
        odds_col = self.mapping["odds"]
        name = "赔率"

        if odds_col in df.columns:
            df[odds_col] = pd.to_numeric(df[odds_col], errors='coerce')
            df['赔率_分段'] = None
            df['赔率_分段提示'] = None
            df['赔率_边界'] = None  # 新增：存储边界信息
            
            for member_id, member_data in df.groupby(member_col):
                odds_values = member_data[odds_col].dropna()
                odds_values = odds_values[odds_values > 0]
                
                if len(odds_values) == 0:
                    df.loc[member_data.index, '赔率_分段'] = '段3'
                    df.loc[member_data.index, '赔率_分段提示'] = "无数据"
                    df.loc[member_data.index, '赔率_边界'] = "【0】"
                    continue
                
                unique_odds = odds_values.unique()
                unique_odds.sort()
                n_unique = len(unique_odds)
                
                odds_to_segment = {}
                segment_count = 0
                boundaries = {}
                
                if n_unique >= 5:
                    try:
                        bins = pd.qcut(pd.Series(unique_odds), q=5, retbins=True)[1]
                        segments = pd.qcut(pd.Series(unique_odds), q=5, labels=['段1', '段2', '段3', '段4', '段5'])
                        odds_to_segment = dict(zip(unique_odds, segments))
                        segment_count = 5
                        df.loc[member_data.index, '赔率_分段提示'] = "5段"
                        # 记录边界
                        boundaries = {
                            '段1': f'【{bins[0]:.2f}-{bins[1]:.2f}】',
                            '段2': f'【{bins[1]:.2f}-{bins[2]:.2f}】',
                            '段3': f'【{bins[2]:.2f}-{bins[3]:.2f}】',
                            '段4': f'【{bins[3]:.2f}-{bins[4]:.2f}】',
                            '段5': f'【>{bins[4]:.2f}】',
                        }
                    except Exception as e:
                        print(f"【调试】5段分段失败: {e}")
                
                if segment_count == 0 and n_unique >= 3:
                    try:
                        bins = pd.qcut(pd.Series(unique_odds), q=3, retbins=True)[1]
                        segments_3 = pd.qcut(pd.Series(unique_odds), q=3, labels=['段2', '段3', '段4'])
                        odds_to_segment = dict(zip(unique_odds, segments_3))
                        segment_count = 3
                        df.loc[member_data.index, '赔率_分段提示'] = "3段"
                        # 3段时，段1和段5为0
                        boundaries = {
                            '段1': '【0】',
                            '段2': f'【{bins[0]:.2f}-{bins[1]:.2f}】',
                            '段3': f'【{bins[1]:.2f}-{bins[2]:.2f}】',
                            '段4': f'【{bins[2]:.2f}-{bins[3]:.2f}】',
                            '段5': '【0】',
                        }
                    except Exception as e:
                        print(f"【调试】3段分段失败: {e}")
                
                if segment_count == 0:
                    odds_to_segment = {v: '段3' for v in unique_odds}
                    fixed_odds = unique_odds[0]
                    df.loc[member_data.index, '赔率_分段提示'] = f"赔率固定 ({fixed_odds:.2f})"
                    boundaries = {
                        '段1': '【0】',
                        '段2': '【0】',
                        '段3': f'【{fixed_odds:.2f}】',
                        '段4': '【0】',
                        '段5': '【0】',
                    }
                
                if odds_to_segment:
                    df.loc[member_data.index, '赔率_分段'] = member_data[odds_col].map(odds_to_segment).fillna('段3')
                    # 保存边界到DataFrame（每行相同）
                    for seg, label in boundaries.items():
                        df.loc[member_data.index, f'赔率_{seg}_边界'] = label
            
            # 计算各段占比（按订单笔数）
            segment_dist = df.groupby([member_col, '赔率_分段']).size().unstack(fill_value=0)
            member_total = segment_dist.sum(axis=1)
            
            # 集中度
            max_seg_pct = (segment_dist.max(axis=1) / member_total).fillna(0)
            bet_stats[f'{name}_集中度'] = bet_stats['会员ID'].map(max_seg_pct.to_dict()).fillna(0)
            
            # 各段占比和边界
            for seg in ['段1', '段2', '段3', '段4', '段5']:
                if seg in segment_dist.columns:
                    seg_pct = (segment_dist[seg] / member_total).fillna(0)
                else:
                    seg_pct = pd.Series(0, index=member_total.index)
                bet_stats[f'{name}_{seg}占比'] = bet_stats['会员ID'].map(seg_pct.to_dict()).fillna(0)
                
                # 添加边界信息
                boundary_col = f'赔率_{seg}_边界'
                if boundary_col in df.columns:
                    boundary_map = df.groupby(member_col)[boundary_col].first().to_dict()
                    bet_stats[f'{name}_{seg}_边界'] = bet_stats['会员ID'].map(boundary_map).fillna('【0】')
            
            # 添加分段提示信息
            segment_hint = df.groupby(member_col)['赔率_分段提示'].first().reset_index()
            segment_hint.columns = ['会员ID', '赔率_分段提示']
            bet_stats = bet_stats.merge(segment_hint, on='会员ID', how='left').fillna('')
            
        
        # ========== 投注额分段分析（按会员动态计算边界） ==========
        bet_amount_col = self.mapping["bet_amount"]
        name2 = "投注额"

        if bet_amount_col in df.columns:
            df[bet_amount_col] = pd.to_numeric(df[bet_amount_col], errors='coerce')
            df['投注额_分段'] = None
            df['投注额_分段提示'] = None
            
            # 按会员单独计算边界和分段
            for member_id, member_data in df.groupby(member_col):
                values = member_data[bet_amount_col].dropna()
                values = values[values > 0]
                
                if len(values) < 5:
                    # 数据不足，全部归为段3
                    df.loc[member_data.index, '投注额_分段'] = '段3'
                    df.loc[member_data.index, '投注额_分段提示'] = f"数据不足({len(values)}单)"
                    # 设置默认边界
                    for seg in ['段1', '段2', '段3', '段4', '段5']:
                        df.loc[member_data.index, f'投注额_{seg}_边界'] = '【0】'
                    continue
                
                # 计算百分位数
                q1 = values.quantile(0.2)
                q2 = values.quantile(0.4)
                q3 = values.quantile(0.6)
                q4 = values.quantile(0.8)
                
                # 边界定义（使用整数）
                boundaries = {
                    '段1': f'【≤{int(q1)}】',
                    '段2': f'【{int(q1)}-{int(q2)}】',
                    '段3': f'【{int(q2)}-{int(q3)}】',
                    '段4': f'【{int(q3)}-{int(q4)}】',
                    '段5': f'【>{int(q4)}】',
                }
                
                def assign_segment(x):
                    if x == 0 or pd.isna(x):
                        return '段3'
                    elif x <= q1:
                        return '段1'
                    elif x <= q2:
                        return '段2'
                    elif x <= q3:
                        return '段3'
                    elif x <= q4:
                        return '段4'
                    else:
                        return '段5'
                
                # 分配分段
                df.loc[member_data.index, '投注额_分段'] = member_data[bet_amount_col].apply(assign_segment)
                df.loc[member_data.index, '投注额_分段提示'] = "5段"
                
                # 保存边界
                for seg, label in boundaries.items():
                    df.loc[member_data.index, f'投注额_{seg}_边界'] = label
            
            # 计算各段占比
            segment_dist = df.groupby([member_col, '投注额_分段']).size().unstack(fill_value=0)
            member_total = segment_dist.sum(axis=1)
            
            # 集中度
            max_seg_pct = (segment_dist.max(axis=1) / member_total).fillna(0)
            bet_stats[f'{name2}_集中度'] = bet_stats['会员ID'].map(max_seg_pct.to_dict()).fillna(0)
            
            # 各段占比和边界
            for seg in ['段1', '段2', '段3', '段4', '段5']:
                if seg in segment_dist.columns:
                    seg_pct = (segment_dist[seg] / member_total).fillna(0)
                else:
                    seg_pct = pd.Series(0, index=member_total.index)
                bet_stats[f'{name2}_{seg}占比'] = bet_stats['会员ID'].map(seg_pct.to_dict()).fillna(0)
                
                # 添加边界
                boundary_col = f'投注额_{seg}_边界'
                if boundary_col in df.columns:
                    boundary_map = df.groupby(member_col)[boundary_col].first().to_dict()
                    bet_stats[f'{name2}_{seg}_边界'] = bet_stats['会员ID'].map(boundary_map).fillna('【0】')
        
        # ========== 7. 输赢分段分析 ==========
        # ========== 输赢分段分析（按会员动态计算边界，处理负数） ==========
        win_loss_col = self.mapping["win_loss"]
        name3 = "输赢"

        if win_loss_col in df.columns:
            df[win_loss_col] = pd.to_numeric(df[win_loss_col], errors='coerce')
            df['输赢_分段'] = None
            df['输赢_分段提示'] = None
            
            # 按会员单独计算边界和分段
            for member_id, member_data in df.groupby(member_col):
                values = member_data[win_loss_col].dropna()
                
                if len(values) < 5:
                    # 数据不足，全部归为段3
                    df.loc[member_data.index, '输赢_分段'] = '段3'
                    df.loc[member_data.index, '输赢_分段提示'] = f"数据不足({len(values)}单)"
                    for seg in ['段1', '段2', '段3', '段4', '段5']:
                        df.loc[member_data.index, f'输赢_{seg}_边界'] = '【0】'
                    continue
                
                # 计算百分位数
                q1 = values.quantile(0.2)
                q2 = values.quantile(0.4)
                q3 = values.quantile(0.6)
                q4 = values.quantile(0.8)
                
                # 边界定义（保留2位小数，处理负数）
                def format_boundary(val):
                    if val >= 0:
                        return f"{val:.0f}"
                    else:
                        return f"{val:.0f}"
                
                boundaries = {
                    '段1': f'【≤{format_boundary(q1)}】',
                    '段2': f'【{format_boundary(q1)}-{format_boundary(q2)}】',
                    '段3': f'【{format_boundary(q2)}-{format_boundary(q3)}】',
                    '段4': f'【{format_boundary(q3)}-{format_boundary(q4)}】',
                    '段5': f'【>{format_boundary(q4)}】',
                }
                
                def assign_segment(x):
                    if pd.isna(x):
                        return '段3'
                    elif x <= q1:
                        return '段1'
                    elif x <= q2:
                        return '段2'
                    elif x <= q3:
                        return '段3'
                    elif x <= q4:
                        return '段4'
                    else:
                        return '段5'
                
                # 分配分段
                df.loc[member_data.index, '输赢_分段'] = member_data[win_loss_col].apply(assign_segment)
                df.loc[member_data.index, '输赢_分段提示'] = "5段"
                
                # 保存边界
                for seg, label in boundaries.items():
                    df.loc[member_data.index, f'输赢_{seg}_边界'] = label
            
            # 计算各段占比
            segment_dist = df.groupby([member_col, '输赢_分段']).size().unstack(fill_value=0)
            member_total = segment_dist.sum(axis=1)
            
            # 集中度
            max_seg_pct = (segment_dist.max(axis=1) / member_total).fillna(0)
            bet_stats[f'{name3}_集中度'] = bet_stats['会员ID'].map(max_seg_pct.to_dict()).fillna(0)
            
            # 各段占比和边界
            for seg in ['段1', '段2', '段3', '段4', '段5']:
                if seg in segment_dist.columns:
                    seg_pct = (segment_dist[seg] / member_total).fillna(0)
                else:
                    seg_pct = pd.Series(0, index=member_total.index)
                bet_stats[f'{name3}_{seg}占比'] = bet_stats['会员ID'].map(seg_pct.to_dict()).fillna(0)
                
                # 添加边界
                boundary_col = f'输赢_{seg}_边界'
                if boundary_col in df.columns:
                    boundary_map = df.groupby(member_col)[boundary_col].first().to_dict()
                    bet_stats[f'{name3}_{seg}_边界'] = bet_stats['会员ID'].map(boundary_map).fillna('【0】')
        
        # ========== 8. 变异系数 ==========
        bet_stats['赔率变异系数'] = bet_stats['赔率标准差'] / bet_stats['平均赔率'].replace(0, np.nan)
        # 投注额变异系数
        bet_stats['投注额变异系数'] = bet_stats['投注额标准差'] / bet_stats['平均投注额'].replace(0, np.nan)
        # 输赢变异系数
        bet_stats['输赢变异系数'] = bet_stats['输赢标准差'] / bet_stats['平均输赢'].replace(0, np.nan)

        # 填充空值为0（表示无法计算或为常数列）
        bet_stats['赔率变异系数'] = bet_stats['赔率变异系数'].fillna(0)
        bet_stats['投注额变异系数'] = bet_stats['投注额变异系数'].fillna(0)
        bet_stats['输赢变异系数'] = bet_stats['输赢变异系数'].fillna(0)
        
        self.member_stats = bet_stats
        
        return self
    
    def determine_member_type(self, row):
        """
        判定会员类型（基于累加评分机制）
        返回: (类型, 风险等级, 验证详情, 总分)
        """
        # ========== 获取各项指标 ==========
        # 赔率分段占比
        odds_p1 = row.get('赔率_段1占比', 0)      # 低赔区 (1.0-1.5)
        odds_p2 = row.get('赔率_段2占比', 0)      # 中低赔区 (1.5-1.8)
        odds_p3 = row.get('赔率_段3占比', 0)      # 正常区 (1.8-2.0)
        odds_p4 = row.get('赔率_段4占比', 0)      # 中高赔区 (2.0-2.5)
        odds_p5 = row.get('赔率_段5占比', 0)      # 高赔区 (>2.5)
        
        # 投注额分段占比
        stake_p1 = row.get('投注额_段1占比', 0)   # 微注区
        stake_p2 = row.get('投注额_段2占比', 0)   # 小额区
        stake_p3 = row.get('投注额_段3占比', 0)   # 中额区
        stake_p4 = row.get('投注额_段4占比', 0)   # 大额区
        stake_p5 = row.get('投注额_段5占比', 0)   # 超大额区
        
        # 输赢分段占比
        winloss_p1 = row.get('输赢_段1占比', 0)   # 大额亏损
        winloss_p2 = row.get('输赢_段2占比', 0)   # 中等亏损
        winloss_p3 = row.get('输赢_段3占比', 0)   # 持平/微利
        winloss_p4 = row.get('输赢_段4占比', 0)   # 中等盈利
        winloss_p5 = row.get('输赢_段5占比', 0)   # 大额盈利
        
        # 体育类型集中度
        sport_conc = row.get('t1_集中度', 0)
        # 联赛集中度
        league_conc = row.get('t2_集中度', 0)
        # 赛事状态集中度（原 t4，滚球/赛前）
        status_conc = row.get('t4_集中度', 0)
        # 比赛阶段集中度（新 t5，上半场/下半场等）
        match_stage_conc = row.get('t5_集中度', 0)
        # 玩法集中度（原 t5，现 t6）
        play_conc = row.get('t6_集中度', 0)
        
        # 变异系数
        odds_cv = row.get('赔率变异系数', 0)
        stake_cv = row.get('投注额变异系数', 0)
        winloss_cv = row.get('输赢变异系数', 0)
        
        # 高频指标
        freq_daily = row.get('日均投注次数', 0)
        interval_short = row.get('最小间隔秒数', 999)
        
        # ========== 评分累加 ==========
        score = 0
        features = []
        
        # 1. 赔率偏好
        if odds_p1 > 0.6:
            score += 1
            features.append(f"低赔偏好({odds_p1:.0%})")
        if odds_p4 + odds_p5 > 0.5:
            score += 1
            features.append(f"高赔偏好({(odds_p4+odds_p5):.0%})")
        
        # 2. 投注额偏好
        if stake_p1 > 0.5:
            score += 1
            features.append(f"微注偏好({stake_p1:.0%})")
        if stake_p4 + stake_p5 > 0.4:
            score += 1
            features.append(f"大额投注({(stake_p4+stake_p5):.0%})")
        
        # 3. 输赢特征
        if winloss_p2 + winloss_p3 > 0.6:
            score += 1
            features.append(f"输赢稳定({(winloss_p2+winloss_p3):.0%})")
        if winloss_p5 > 0.3:
            score += 1
            features.append(f"大额亏损({winloss_p5:.0%})")
        if winloss_p4 + winloss_p5 > 0.5:
            score += 1
            features.append(f"大额盈利({(winloss_p4+winloss_p5):.0%})")
        
        # 4. 集中度（单一偏好）
        if sport_conc > 0.8:
            score += 1
            features.append(f"单一体育({sport_conc:.0%})")
        if league_conc > 0.8:
            score += 1
            features.append(f"单一联赛({league_conc:.0%})")
        if play_conc > 0.8:
            score += 1
            features.append(f"单一玩法({play_conc:.0%})")
        if match_stage_conc > 0.9:
            score += 1
            features.append(f"单一阶段({match_stage_conc:.0%})")
        
        # 5. 高频特征
        if freq_daily > 50:
            score += 1
            features.append(f"高频投注({freq_daily:.0f}次/日)")
        if interval_short < 10:
            score += 1
            features.append(f"间隔极短({interval_short:.0f}秒)")
        
        # 6. 波动特征
        if odds_cv < 0.05:
            score += 1
            features.append(f"固定赔率({odds_cv:.2f})")
        if stake_cv < 0.1:
            score += 1
            features.append(f"固定投注({stake_cv:.2f})")
        if stake_cv > 1.5:
            score += 1
            features.append(f"投注波动大({stake_cv:.2f})")
        if winloss_cv > 2.0:
            score += 1
            features.append(f"输赢波动大({winloss_cv:.2f})")
        
        # ========== 3. 确定基础类型和风险等级 ==========
        if score == 0:
            risk_level = "正常"
            member_type = "👤 正常玩家"
            type_desc = "各项指标分布均匀，无明显异常"
        elif score <= 2:
            risk_level = "留意"
            member_type = "👀 观察玩家"
            type_desc = f"有 {score} 个轻微异常特征，建议关注"
        elif score <= 4:
            risk_level = "风险"
            member_type = "⚠️ 风险玩家"
            type_desc = f"有 {score} 个异常特征，存在风险行为"
        elif score <= 6:
            risk_level = "高危"
            member_type = "🔴 高危玩家"
            type_desc = f"有 {score} 个严重异常特征，高度可疑"
        else:
            risk_level = "异常"
            member_type = "💀 异常玩家"
            type_desc = f"有 {score} 个极度异常特征，强烈建议审查"
        
        # ========== 4. 收集匹配类型（独立列表）==========
        matched_types = []
        
        # 软件刷单（使用玩法集中度 play_conc）
        if odds_p1 > 0.6 and stake_p1 > 0.5 and play_conc > 0.7:
            matched_types.append("软件刷单")

        # 套利玩家
        if odds_p1 > 0.6 and (winloss_p2 + winloss_p3) > 0.5:
            matched_types.append("套利玩家")

        # 职业玩家
        if odds_p2 > 0.4 and stake_p2 > 0.4 and winloss_p2 > 0.4:
            matched_types.append("职业玩家")

        # 高赔猎手
        if (odds_p4 + odds_p5) > 0.5 and (stake_p4 + stake_p5) > 0.4:
            matched_types.append("高赔猎手")

        # 问题玩家
        if winloss_p5 > 0.3 and (stake_p4 + stake_p5) > 0.4:
            matched_types.append("问题玩家")

        # 单一玩家（使用体育、联赛、玩法集中度）
        if sport_conc > 0.8 and league_conc > 0.8 and play_conc > 0.8:
            matched_types.append("单一玩家")

        # 阶段偏好玩家（使用赛事状态集中度 status_conc，不是比赛阶段）
        if status_conc > 0.9:
            matched_types.append("阶段偏好玩家")

        # 高频玩家
        if freq_daily > 50 and interval_short < 10:
            matched_types.append("高频玩家")

        # 波动玩家
        if stake_cv > 1.5 and winloss_cv > 2.0:
            matched_types.append("波动玩家")
        
        # ========== 5. 构建验证详情（匹配类型不加入 features）==========
        details = [f"总分: {score}", f"触发特征: {', '.join(features[:5])}"]
        if len(features) > 5:
            details.append(f"等{len(features)}个特征")
        details.append(type_desc)
        
        return member_type, risk_level, " | ".join(details), matched_types, score
    
    def run_analysis(self):
        """执行分析"""
        if self.member_stats is None:
            self.aggregate_member_data()
        
        results = []
        for _, row in self.member_stats.iterrows():
            member_type, risk_level, details, matched_types, score = self.determine_member_type(row)
            
            # 将匹配类型列表转换为字符串
            matched_types_str = " / ".join(matched_types) if matched_types else ""
            
            results.append({
                "会员ID": row["会员ID"],
                "会员性质": member_type,
                "风险等级": risk_level,
                "匹配类型": matched_types_str,  # 新增
                "验证详情": details,
                "总分": score,  # 新增，便于后续使用
                "总投注额": row.get("总投注额", 0),
                "投注次数": row.get("投注次数", 0),
                "平均赔率": row.get("平均赔率", 0),
                "总输赢": row.get("总输赢", 0),
                "赔率集中": row.get("赔率_集中度", 0),
                "投注额集中": row.get("投注额_集中度", 0),
                "玩法集中": row.get("t5_集中度", 0),
                "赔率_分段提示": row.get("赔率_分段提示", "")
            })       
        self.results = pd.DataFrame(results)
        return self.results
    
    def get_statistics_comparison(self, results):
        """获取异常会员与正常会员的统计对比"""
        
        # 分离异常会员和正常会员
        abnormal = results[results["风险等级"] != "正常"]
        normal = results[results["风险等级"] == "正常"]
        
        comparison = []
        
        # 指标列表
        metrics = [
            ("总投注额", "总投注额"),
            ("投注次数", "投注次数"),
            ("平均赔率", "平均赔率"),
            ("总输赢", "总输赢"),
            ("赔率集中", "赔率集中"),
            ("投注额集中", "投注额集中"),
            ("玩法集中", "玩法集中")
        ]
        
        for metric_name, col_name in metrics:
            if col_name in results.columns:
                abnormal_mean = abnormal[col_name].mean() if len(abnormal) > 0 else 0
                normal_mean = normal[col_name].mean() if len(normal) > 0 else 0
                diff_pct = ((abnormal_mean - normal_mean) / normal_mean * 100) if normal_mean != 0 else 0
                
                comparison.append({
                    "指标": metric_name,
                    "异常会员均值": f"{abnormal_mean:.2f}",
                    "正常会员均值": f"{normal_mean:.2f}",
                    "差异": f"{diff_pct:+.1f}%",
                    "说明": "偏高" if diff_pct > 10 else "偏低" if diff_pct < -10 else "相近"
                })
        
        return pd.DataFrame(comparison)


    def get_risk_level_distribution(self, results):
        """获取风险等级分布"""
        distribution = results["风险等级"].value_counts().reset_index()
        distribution.columns = ["风险等级", "会员数"]
        distribution["占比"] = (distribution["会员数"] / len(results) * 100).round(1).astype(str) + "%"
        return distribution


    def get_member_type_distribution(self, results):
        """获取会员类型分布"""
        distribution = results["会员性质"].value_counts().reset_index()
        distribution.columns = ["会员性质", "会员数"]
        distribution["占比"] = (distribution["会员数"] / len(results) * 100).round(1).astype(str) + "%"
        return distribution