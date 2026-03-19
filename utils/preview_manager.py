"""
预览管理模块：统一管理数据预览、统计预览、图表预览
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime  # 【新增】导入datetime

class PreviewManager:
    """统一的预览管理器"""
    
    def __init__(self):
        # 初始化预览状态
        if 'preview_mode' not in st.session_state:
            st.session_state.preview_mode = 'data'  # data/stats/chart
        if 'preview_data' not in st.session_state:
            st.session_state.preview_data = None
        if 'preview_stats' not in st.session_state:
            st.session_state.preview_stats = None
        if 'preview_chart' not in st.session_state:
            st.session_state.preview_chart = None
        if 'preview_rows' not in st.session_state:
            st.session_state.preview_rows = 20
        if 'last_operation' not in st.session_state:
            st.session_state.last_operation = None
    
    @property
    def preview_rows(self):
        """获取预览行数"""
        return st.session_state.preview_rows
    
    # ==================== 数据预览方法 ====================
    
    def get_data_preview(self):
        """获取数据预览 - 直接从主数据读取"""
        if 'df' in st.session_state and st.session_state.df is not None:
            return st.session_state.df.head(self.preview_rows)
        return None
    
    def show_data_preview(self, title="数据预览"):
        """显示数据预览"""
        preview_df = self.get_data_preview()
        if preview_df is not None:
            st.markdown(f"### {title}")
            
            # 显示数据信息
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总行数", len(st.session_state.df))
            with col2:
                st.metric("总列数", len(st.session_state.df.columns))
            with col3:
                st.metric("预览行数", self.preview_rows)
            
            # 显示最后一次操作信息
            last_op = self.get_last_operation()
            if last_op:
                st.info(f"✅ 最后一次操作：{last_op['name']} ({last_op['time'].strftime('%H:%M:%S')})")
            
            # 显示数据预览
            st.dataframe(preview_df, use_container_width=True)
            
            # 显示列信息
            with st.expander("查看列信息"):
                col_info = pd.DataFrame({
                    '列名': st.session_state.df.columns,
                    '数据类型': st.session_state.df.dtypes.values,
                    '非空值数': st.session_state.df.count().values,
                    '缺失值数': st.session_state.df.isna().sum().values
                })
                st.dataframe(col_info, use_container_width=True)
        else:
            st.info("暂无数据预览，请先上传数据")
    
    # ==================== 统计预览方法 ====================
    
    def update_stats_preview(self, stats_df, stats_type="描述性统计"):
        """更新统计预览"""
        print(f"【调试-PreviewManager】update_stats_preview 被调用")
        print(f"【调试-PreviewManager】stats_type: {stats_type}")
        print(f"【调试-PreviewManager】stats_df 形状: {stats_df.shape if stats_df is not None else 'None'}")
        
        st.session_state.preview_mode = 'stats'
        st.session_state.preview_stats = {
            'data': stats_df,
            'type': stats_type,
            'timestamp': datetime.now()  # 【修复】使用导入的datetime
        }
        print(f"【调试-PreviewManager】预览模式已设置为: stats")
    
    def get_stats_preview(self):
        """获取统计预览"""
        stats = st.session_state.get('preview_stats', None)
        print(f"【调试-PreviewManager】get_stats_preview 被调用")
        print(f"【调试-PreviewManager】preview_stats 是否存在: {stats is not None}")
        return stats
    
    def show_stats_preview(self):
        """显示统计预览"""
        print(f"【调试-PreviewManager】show_stats_preview 被调用")
        
        stats = self.get_stats_preview()
        if stats and stats['data'] is not None:
            st.markdown(f"### {stats['type']}")
            st.dataframe(stats['data'], use_container_width=True)
            
            # 导出选项
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 导出为CSV", key="export_stats_csv", use_container_width=True):
                    csv = stats['data'].to_csv().encode('utf-8')
                    st.download_button(
                        label="点击下载CSV",
                        data=csv,
                        file_name=f"stats_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_stats_csv"
                    )
            
            with col2:
                if st.button("📥 导出为Excel", key="export_stats_excel", use_container_width=True):
                    # Excel导出需要临时文件
                    output = pd.ExcelWriter('temp_stats.xlsx', engine='xlsxwriter')
                    stats['data'].to_excel(output, sheet_name='统计结果')
                    output.close()
                    
                    with open('temp_stats.xlsx', 'rb') as f:
                        st.download_button(
                            label="点击下载Excel",
                            data=f,
                            file_name=f"stats_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_stats_excel"
                        )
            
            # 统计信息
            with st.expander("统计信息"):
                st.json({
                    "统计类型": stats['type'],
                    "生成时间": str(stats.get('timestamp', '未知')),
                    "数据形状": list(stats['data'].shape),
                    "列名": list(stats['data'].columns)
                })
        else:
            st.info("暂无统计预览，请先在右侧面板执行统计分析")
    
    # ==================== 图表预览方法 ====================
    
    def update_chart_preview(self, fig, chart_type="图表"):
        """更新图表预览"""
        print(f"【调试-PreviewManager】update_chart_preview 被调用")
        print(f"【调试-PreviewManager】chart_type: {chart_type}")
        print(f"【调试-PreviewManager】fig 类型: {type(fig)}")
        
        st.session_state.preview_mode = 'chart'
        st.session_state.preview_chart = {
            'figure': fig,
            'type': chart_type,
            'timestamp': datetime.now()  # 【修复】使用导入的datetime
        }
        print(f"【调试-PreviewManager】预览模式已设置为: chart")
    
    def get_chart_preview(self):
        """获取图表预览"""
        chart = st.session_state.get('preview_chart', None)
        print(f"【调试-PreviewManager】get_chart_preview 被调用")
        print(f"【调试-PreviewManager】preview_chart 是否存在: {chart is not None}")
        return chart
    
    def show_chart_preview(self):
        """显示图表预览"""
        print(f"【调试-PreviewManager】show_chart_preview 被调用")
        
        chart = self.get_chart_preview()
        if chart and chart['figure'] is not None:
            st.markdown(f"### {chart['type']}")
            st.plotly_chart(chart['figure'], use_container_width=True)
            
            # 图表导出选项
            st.markdown("#### 图表导出")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📥 导出为PNG", key="export_png", use_container_width=True):
                    st.info("PNG导出功能需要从主程序传入managers")
            
            with col2:
                if st.button("📥 导出为PDF", key="export_pdf", use_container_width=True):
                    st.info("PDF导出功能需要从主程序传入managers")
            
            with col3:
                if st.button("📥 导出为SVG", key="export_svg", use_container_width=True):
                    st.info("SVG导出功能需要从主程序传入managers")
            
            # 图表信息
            with st.expander("图表信息"):
                st.json({
                    "图表类型": chart.get('type', '未知'),
                    "生成时间": str(chart.get('timestamp', '未知'))
                })
        else:
            st.info("暂无图表预览，请先在右侧面板生成图表")
    
    # ==================== 统一的预览显示 ====================
    
    def show_preview(self):
        """根据当前模式显示对应的预览"""
        if st.session_state.preview_mode == 'data':
            self.show_data_preview()
        elif st.session_state.preview_mode == 'stats':
            self.show_stats_preview()
        elif st.session_state.preview_mode == 'chart':
            self.show_chart_preview()
        else:
            self.show_data_preview()
    
    # ==================== 辅助方法 ====================
    
    def set_preview_rows(self, rows):
        """设置预览行数"""
        st.session_state.preview_rows = rows
    
    def record_operation(self, operation_name):
        """记录最后一次操作"""
        st.session_state.last_operation = {
            'name': operation_name,
            'time': datetime.now()  # 【修复】使用导入的datetime
        }
    
    def get_last_operation(self):
        """获取最后一次操作"""
        return st.session_state.last_operation
    
    def clear_preview(self):
        """清空预览"""
        st.session_state.preview_data = None
        st.session_state.preview_stats = None
        st.session_state.preview_chart = None
        st.session_state.preview_mode = 'data'