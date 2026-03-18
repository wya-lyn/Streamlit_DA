"""
AI分析模块：可开关的AI功能，预留API接口
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime

class AIAnalyzer:
    """AI分析器（可开关）"""
    
    def __init__(self):
        self.client = None
        self.api_key = None
    
    def set_api_key(self, api_key):
        """设置API密钥"""
        self.api_key = api_key
        # 这里预留OpenAI客户端初始化
        # if api_key:
        #     from openai import OpenAI
        #     self.client = OpenAI(api_key=api_key)
    
    def is_ready(self):
        """检查AI功能是否就绪"""
        return self.api_key is not None and len(self.api_key) > 0
    
    def analyze(self, df, prompt, analysis_type="数据洞察"):
        """执行AI分析"""
        if not self.is_ready():
            return {"error": "API密钥未配置"}
        
        try:
            # 准备数据上下文
            data_context = self._prepare_data_context(df)
            
            # 构建提示词
            full_prompt = self._build_prompt(data_context, prompt, analysis_type)
            
            # 这里预留实际的API调用
            # if self.client:
            #     response = self.client.chat.completions.create(
            #         model="gpt-3.5-turbo",
            #         messages=[
            #             {"role": "system", "content": "你是一个专业的数据分析师。"},
            #             {"role": "user", "content": full_prompt}
            #         ],
            #         temperature=0.7,
            #         max_tokens=2000
            #     )
            #     return response.choices[0].message.content
            
            # 返回模拟结果（演示用）
            return self._mock_analysis(data_context, prompt, analysis_type)
            
        except Exception as e:
            return {"error": str(e)}
    
    def _prepare_data_context(self, df):
        """准备数据上下文"""
        context = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "sample_data": df.head(10).to_dict('records'),
            "numeric_summary": {},
            "missing_values": df.isna().sum().to_dict()
        }
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            context["numeric_summary"][col] = {
                "min": float(df[col].min()) if not df[col].isna().all() else None,
                "max": float(df[col].max()) if not df[col].isna().all() else None,
                "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                "median": float(df[col].median()) if not df[col].isna().all() else None
            }
        
        return context
    
    def _build_prompt(self, data_context, user_prompt, analysis_type):
        """构建完整的提示词"""
        prompt = f"""
数据集信息：
- 数据量：{data_context['rows']}行，{data_context['columns']}列
- 字段列表：{', '.join(data_context['column_names'])}
- 字段类型：{json.dumps(data_context['dtypes'], ensure_ascii=False, indent=2)}
- 缺失值情况：{json.dumps(data_context['missing_values'], ensure_ascii=False, indent=2)}

数据样例（前10行）：
{json.dumps(data_context['sample_data'], ensure_ascii=False, indent=2, default=str)[:1000]}

数值字段统计：
{json.dumps(data_context['numeric_summary'], ensure_ascii=False, indent=2, default=str)}

分析类型：{analysis_type}
用户需求：{user_prompt}

请提供详细的数据分析报告，包括：
1. 数据整体情况评估
2. 关键发现和洞察
3. 具体建议
4. 需要进一步分析的方向
"""
        return prompt
    
    def _mock_analysis(self, data_context, user_prompt, analysis_type):
        """模拟分析结果（演示用）"""
        return f"""
# 🤖 AI分析报告

## 数据概况
- 数据集包含 {data_context['rows']} 行数据，{data_context['columns']} 个字段
- 字段类型分布：{len([c for c in data_context['dtypes'].values() if 'int' in c or 'float' in c])} 个数值字段，{len([c for c in data_context['dtypes'].values() if 'object' in c])} 个文本字段

## 关键发现
1. **数据完整性**：平均缺失率约 {sum(data_context['missing_values'].values()) / (data_context['rows'] * data_context['columns']) * 100:.1f}%
2. **数值分布**：各数值字段的分布较为合理
3. **数据质量**：样本数据显示数据格式规范

## 基于您需求的回答
**分析类型**：{analysis_type}
**您的需求**：{user_prompt}

根据提供的数据，建议可以：
1. 重点关注数值字段的相关性分析
2. 对文本字段进行频次统计
3. 考虑时间序列趋势（如果包含日期字段）

## 下一步建议
- 使用可视化功能深入探索数据
- 尝试数据清洗功能处理缺失值
- 进行分组统计发现更多模式

*（注：这是模拟分析结果，配置OpenAI API密钥后可获得真实的AI分析）*
"""
    
    def generate_report(self, df, prompt, include_charts=False):
        """生成分析报告"""
        analysis = self.analyze(df, prompt, "报告生成")
        
        report = f"""
# 数据分析报告
生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{analysis}

## 数据附录
- 总行数：{len(df)}
- 总列数：{len(df.columns)}
- 字段列表：{', '.join(df.columns[:10])}{'...' if len(df.columns) > 10 else ''}
"""
        return report