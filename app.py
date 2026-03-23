"""
数据洞察助手 - 主入口文件（模块化重构版）
功能：集成所有模块，实现完整的数据分析工具
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

# 导入自定义模块
from utils.theme_manager import ThemeManager
from utils.file_loader import FileLoader
from utils.data_cleaner import DataCleaner
from utils.data_filter import DataFilter
from utils.stats_analyzer import StatsAnalyzer
from utils.chart_generator import ChartGenerator
from utils.ai_analyzer import AIAnalyzer
from utils.preview_manager import PreviewManager
from utils.logger import Logger
from components.layout import LayoutManager
from components.announcements import AnnouncementManager
from components.footer import FooterManager
from components.history_manager import HistoryManager
from utils.chart_generator import ChartGenerator
from components.data_processing import render_data_processing_tab
from components.analysis_options import render_analysis_options_tab

# ============================================
# 页面配置
# ============================================
st.set_page_config(
    page_title="数据洞察助手",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 初始化所有管理器（单例）
# ============================================
@st.cache_resource
def init_managers():
    """初始化所有管理器"""
    return {
        'announcement': AnnouncementManager(),
        'footer': FooterManager(),
        'layout': LayoutManager(),
        'history': HistoryManager(),
        'file_loader': FileLoader(),
        'data_cleaner': DataCleaner(),
        'data_filter': DataFilter(),
        'stats_analyzer': StatsAnalyzer(),
        'chart_generator': ChartGenerator(),
        'ai_analyzer': AIAnalyzer()
    }

# ============================================
# 初始化会话状态
# ============================================
def init_session_state():
    """初始化所有会话状态变量"""
    # 基础数据
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'original_df' not in st.session_state:
        st.session_state.original_df = None
    
    # 历史记录
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'current_step' not in st.session_state:
        st.session_state.current_step = -1
    
    # 预览管理
    if 'preview_manager' not in st.session_state:
        st.session_state.preview_manager = PreviewManager()
    
    # 调试
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
    
    # 界面状态
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "首页"
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'light'
    
    # ===== 新增：筛选功能相关 =====
    if 'filter_history' not in st.session_state:
        st.session_state.filter_history = []  # 存储筛选历史，用于撤销
    
    if 'filter_preview' not in st.session_state:
        st.session_state.filter_preview = None  # 存储筛选预览结果
    
    if 'filter_preview_info' not in st.session_state:
        st.session_state.filter_preview_info = None  # 存储预览信息
    
    # ===== 新增：数据确认相关 =====
    if 'confirmed_data' not in st.session_state:
        st.session_state.confirmed_data = None  # 存储确认后的数据
    
    if 'data_confirmed' not in st.session_state:
        st.session_state.data_confirmed = False  # 标记数据是否已确认
    
    # ===== 新增：文件上传相关 =====
    if 'last_uploaded_file' not in st.session_state:
        st.session_state.last_uploaded_file = None  # 记录上次上传的文件名
    if 'preview_manager' not in st.session_state:
        st.session_state.preview_manager = PreviewManager()
        print("【调试】preview_manager 已初始化")
        # 添加缺失的键
    if 'operation_history' not in st.session_state:
        st.session_state.operation_history = []
    
    if 'history' not in st.session_state:
        st.session_state.history = []

# ============================================
# 执行初始化
# ============================================
managers = init_managers()
init_session_state()
ThemeManager.init_theme()
ThemeManager.apply_custom_css()

# ============================================
# 工具函数：数据操作通用处理
# ============================================
def execute_data_operation(operation_func, operation_name, *args, **kwargs):
    """执行数据操作的标准流程"""
    try:
        Logger.info(f"开始执行{operation_name}操作")
        before_shape = st.session_state.df.shape if st.session_state.df is not None else (0, 0)
        
        # 执行操作
        result_df = operation_func(st.session_state.df, *args, **kwargs)
        
        # 【关键修复】重置索引，丢弃旧的索引
        result_df = result_df.reset_index(drop=True)
        
        # 更新数据
        st.session_state.df = result_df
        
        # 记录操作
        st.session_state.preview_manager.record_operation(operation_name)
        managers['history'].add_to_history(operation_name, st.session_state.df)
        
        after_shape = st.session_state.df.shape
        Logger.info(f"{operation_name}完成: {before_shape} -> {after_shape}")
        
        return True, f"{operation_name}操作成功"
    except Exception as e:
        Logger.error(f"{operation_name}失败: {str(e)}")
        return False, f"{operation_name}失败: {str(e)}"

# ============================================
# 侧边栏组件
# ============================================
def render_sidebar():
    """渲染左侧边栏"""
    with st.sidebar:
        st.title("📊 数据洞察助手")
        
        # 主题切换
        render_theme_toggle()
        
        st.divider()
        
        # 文件上传
        render_file_uploader()

def render_theme_toggle():
    """主题切换组件"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 主题设置")
    with col2:
        current_theme = st.session_state.theme_mode
        theme_icon = "🌙" if current_theme == "dark" else "☀️"
        if st.button(theme_icon, key="theme_toggle"):
            ThemeManager.toggle_theme()
            st.rerun()

def render_file_uploader():
    """文件上传组件"""
    
    uploaded_file = st.file_uploader(
        "点击或拖拽文件到此处",
        type=['csv', 'xlsx', 'json'],
        help="支持 CSV、Excel、JSON 格式，最大 20MB",
        key="file_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_file is None:
        return
    
    # 生成当前文件唯一标识
    current_file_key = f"{uploaded_file.name}_{uploaded_file.size}"
    last_key = st.session_state.get('last_uploaded_file_key')
    
    # 重复上传同一文件
    if last_key == current_file_key:
        if st.session_state.df is not None:
            st.info(f"📁 已加载: {uploaded_file.name}")
        return
    
    # 新文件，清空旧数据
    st.session_state.df = None
    st.session_state.original_df = None
    st.session_state.preview_manager.clear_preview()
    
    # 统一调用 file_loader 处理所有格式
    with st.spinner("正在加载数据..."):
        df = managers['file_loader'].load_file(uploaded_file)
    
    if df is not None:
        df = df.reset_index(drop=True)
        st.session_state.df = df
        st.session_state.original_df = df.copy()
        st.session_state.last_uploaded_file_key = current_file_key
        managers['history'].add_to_history("上传文件", df)
        st.success(f"✅ 加载成功！{len(df)}行 × {len(df.columns)}列")
        st.session_state.preview_manager.record_operation("上传文件")
        st.rerun()
    else:
        # 不立即报错，因为可能是多工作表等待确认
        # 检查是否在多工作表选择状态
        if any(key.startswith('excel_state_') for key in st.session_state.keys()):
            # 正在等待用户选择工作表，不显示错误
            pass
        else:
            st.error("文件加载失败，请检查文件格式")
# ============================================
# 右侧功能面板
# ============================================
def render_right_panel():
    """渲染右侧功能面板"""
    with st.container():
        show_right_panel = st.checkbox("📋 显示功能面板", value=True)
        
        if show_right_panel:
            # 移除"数据筛选"标签，只保留三个标签
            tabs = st.tabs(["🧹 数据处理", "📊 分析选项", "🤖 AI配置"])
            
            with tabs[0]:
                render_data_processing_tab()  # 这个标签页现在包含数据处理和筛选
            
            with tabs[1]:
                render_analysis_options_tab()
            
            with tabs[2]:
                render_ai_config_tab()

# 统一筛选功能（放在这里）
# ============================================


       
def undo_last_operation():
    """全局撤销操作"""
    if st.session_state.df is not None:
        st.session_state.df = managers['history'].undo(st.session_state.df)
        st.session_state.preview_manager.record_operation("撤销")
        st.rerun()

def redo_last_operation():
    """全局重做操作"""
    if st.session_state.df is not None:
        st.session_state.df = managers['history'].redo(st.session_state.df)
        st.session_state.preview_manager.record_operation("重做")
        st.rerun()

def show_global_history():
    """显示全局历史"""
    managers['history'].show_history()

def preview_unified_filter(column, condition, value):
    """预览统一筛选结果"""
    try:
        # 获取列的数据类型
        col_dtype = st.session_state.df[column].dtype
        is_numeric = pd.api.types.is_numeric_dtype(col_dtype)
        
        # 对预览数据应用筛选
        preview_df = st.session_state.df.head(20).copy()
        
        if condition in ["为空", "不为空"]:
            if condition == "为空":
                result_df = preview_df[preview_df[column].isna() | (preview_df[column] == "null")]
            else:
                result_df = preview_df[preview_df[column].notna() & (preview_df[column] != "null")]
        
        elif condition in ["今天", "本周", "本月"]:
            result_df = managers['data_filter'].date_filter(preview_df, column, condition, None)
        
        elif condition == "介于":
            min_val, max_val = value
            if is_numeric:
                result_df = preview_df[(preview_df[column] >= min_val) & (preview_df[column] <= max_val)]
            else:
                result_df = preview_df[(preview_df[column].astype(str) >= str(min_val)) & 
                                      (preview_df[column].astype(str) <= str(max_val))]
        
        else:
            if is_numeric and condition not in ["包含", "不包含", "开头为", "结尾为"]:
                # 数值比较
                if condition == "等于":
                    result_df = preview_df[preview_df[column] == value]
                elif condition == "不等于":
                    result_df = preview_df[preview_df[column] != value]
                elif condition == "大于":
                    result_df = preview_df[preview_df[column] > value]
                elif condition == "小于":
                    result_df = preview_df[preview_df[column] < value]
                elif condition == "大于等于":
                    result_df = preview_df[preview_df[column] >= value]
                elif condition == "小于等于":
                    result_df = preview_df[preview_df[column] <= value]
                else:
                    result_df = preview_df
            else:
                # 文本筛选
                if condition == "包含":
                    result_df = preview_df[preview_df[column].astype(str).str.contains(str(value), na=False, regex=False)]
                elif condition == "不包含":
                    result_df = preview_df[~preview_df[column].astype(str).str.contains(str(value), na=False, regex=False)]
                elif condition == "等于":
                    result_df = preview_df[preview_df[column].astype(str) == str(value)]
                elif condition == "不等于":
                    result_df = preview_df[preview_df[column].astype(str) != str(value)]
                elif condition == "开头为":
                    result_df = preview_df[preview_df[column].astype(str).str.startswith(str(value), na=False)]
                elif condition == "结尾为":
                    result_df = preview_df[preview_df[column].astype(str).str.endswith(str(value), na=False)]
                else:
                    result_df = preview_df
        
        st.session_state.filter_preview = result_df
        st.session_state.filter_preview_info = f"筛选结果：{len(result_df)} 行（共预览20行）"
        st.rerun()
        
    except Exception as e:
        st.error(f"预览失败: {str(e)}")

def apply_unified_filter(column, condition, value):
    """应用统一筛选"""
    try:
        # 保存当前数据到历史
        if 'filter_history' not in st.session_state:
            st.session_state.filter_history = []
        
        st.session_state.filter_history.append({
            'data': st.session_state.df.copy(),
            'type': '筛选',
            'params': f"{column} {condition} {value}",
            'time': datetime.now().strftime('%H:%M:%S')
        })
        
        # 获取列的数据类型
        col_dtype = st.session_state.df[column].dtype
        is_numeric = pd.api.types.is_numeric_dtype(col_dtype)
        
        # 应用筛选
        if condition in ["为空", "不为空"]:
            if condition == "为空":
                result_df = st.session_state.df[st.session_state.df[column].isna() | (st.session_state.df[column] == "null")]
            else:
                result_df = st.session_state.df[st.session_state.df[column].notna() & (st.session_state.df[column] != "null")]
        
        elif condition in ["今天", "本周", "本月"]:
            result_df = managers['data_filter'].date_filter(st.session_state.df, column, condition, None)
        
        elif condition == "介于":
            min_val, max_val = value
            if is_numeric:
                result_df = st.session_state.df[(st.session_state.df[column] >= min_val) & 
                                               (st.session_state.df[column] <= max_val)]
            else:
                result_df = st.session_state.df[(st.session_state.df[column].astype(str) >= str(min_val)) & 
                                               (st.session_state.df[column].astype(str) <= str(max_val))]
        
        else:
            if is_numeric and condition not in ["包含", "不包含", "开头为", "结尾为"]:
                # 数值比较
                if condition == "等于":
                    result_df = st.session_state.df[st.session_state.df[column] == value]
                elif condition == "不等于":
                    result_df = st.session_state.df[st.session_state.df[column] != value]
                elif condition == "大于":
                    result_df = st.session_state.df[st.session_state.df[column] > value]
                elif condition == "小于":
                    result_df = st.session_state.df[st.session_state.df[column] < value]
                elif condition == "大于等于":
                    result_df = st.session_state.df[st.session_state.df[column] >= value]
                elif condition == "小于等于":
                    result_df = st.session_state.df[st.session_state.df[column] <= value]
                else:
                    result_df = st.session_state.df
            else:
                # 文本筛选
                if condition == "包含":
                    result_df = st.session_state.df[st.session_state.df[column].astype(str).str.contains(str(value), na=False, regex=False)]
                elif condition == "不包含":
                    result_df = st.session_state.df[~st.session_state.df[column].astype(str).str.contains(str(value), na=False, regex=False)]
                elif condition == "等于":
                    result_df = st.session_state.df[st.session_state.df[column].astype(str) == str(value)]
                elif condition == "不等于":
                    result_df = st.session_state.df[st.session_state.df[column].astype(str) != str(value)]
                elif condition == "开头为":
                    result_df = st.session_state.df[st.session_state.df[column].astype(str).str.startswith(str(value), na=False)]
                elif condition == "结尾为":
                    result_df = st.session_state.df[st.session_state.df[column].astype(str).str.endswith(str(value), na=False)]
                else:
                    result_df = st.session_state.df
        
        # 更新数据
        st.session_state.df = result_df
        st.session_state.preview_manager.record_operation(f"筛选-{condition}")
        
        # 清除预览
        st.session_state.filter_preview = None
        st.session_state.filter_preview_info = None
        
        st.success(f"筛选完成，当前 {len(result_df)} 行")
        st.rerun()
        
    except Exception as e:
        st.error(f"筛选失败: {str(e)}")


def confirm_current_data():
    """确认当前数据"""
    st.session_state.confirmed_data = st.session_state.df.copy()
    st.session_state.data_confirmed = True
    st.success("数据已确认，将作为后续分析的基准")
    
    # 记录确认操作
    st.session_state.preview_manager.record_operation("数据确认")

# ============================================
# 数据筛选标签页
# ============================================
def reset_to_original():
    """重置到原始数据"""
    if st.session_state.original_df is not None:
        # 保存当前到历史
        if 'filter_history' not in st.session_state:
            st.session_state.filter_history = []
        st.session_state.filter_history.append({
            'data': st.session_state.df.copy(),
            'type': '重置到原始',
            'params': ''
        })
        
        st.session_state.df = st.session_state.original_df.copy()
        st.session_state.preview_manager.record_operation("重置到原始数据")
        st.success("已重置到原始数据")
        st.rerun()
    else:
        st.warning("没有原始数据可重置")

            
# ============================================
# 分析选项标签页
# ============================================
   

def get_pie_mode_description(mode):
    """获取复合饼图模式说明"""
    descriptions = {
        "子图布局": "📊 网格展示：主图在左上角，其他子图按网格排列，适合对比分析多个类别",
        "交互下钻": "🖱️ 点击交互：点击主图区块，下方显示该区块的详细构成，适合层级探索",
        "复合定位": "🎯 预设模板：主图居中，子图按预设位置环绕，适合报告展示"
    }
    return descriptions.get(mode, "")


         
          
    



# ============================================
# AI配置标签页
# ============================================
def render_ai_config_tab():
    """AI配置标签页"""
    st.markdown("### 🤖 AI分析设置")
    
    enable_ai = st.toggle("启用AI分析", value=False, key="ai_enabled")
    
    if enable_ai:
        st.info("需要OpenAI API密钥才能使用")
        api_key = st.text_input("API密钥", type="password", key="ai_api_key")
        
        if api_key:
            managers['ai_analyzer'].set_api_key(api_key)
            st.success("API密钥已设置")
            
            st.divider()
            st.markdown("### 分析提示词")
            
            prompt = st.text_area(
                "输入分析需求",
                placeholder="例如：分析销售数据趋势，找出异常点，给出建议",
                height=100,
                key="ai_prompt"
            )
            
            analysis_type = st.selectbox(
                "分析类型",
                ["数据洞察", "趋势分析", "异常检测", "预测建议", "自定义"],
                key="ai_analysis_type"
            )
            
            if st.button("🚀 生成AI分析", type="primary", key="btn_ai_analyze", use_container_width=True):
                if st.session_state.df is None:
                    st.warning("请先上传数据")
                elif not prompt:
                    st.warning("请输入分析需求")
                else:
                    with st.spinner("AI正在分析数据..."):
                        result = managers['ai_analyzer'].analyze(
                            st.session_state.df, prompt, analysis_type
                        )
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.markdown("### AI分析结果")
                            st.markdown(result)
                            
# ============================================
# 主内容区 - 统一的预览显示
# ============================================
def render_main_content():
    """渲染主内容区"""
    if st.session_state.df is None:
        render_welcome_page()
        return
    
    # 直接根据预览模式显示内容
    preview_mode = st.session_state.get('preview_mode', 'data')
    
    if preview_mode == 'stats':
        render_analysis_preview_page()  # 显示统计结果
    elif preview_mode == 'chart':
        render_chart_preview_page()      # 显示图表
    else:
        render_data_preview_page()       # 显示数据预览

def render_welcome_page():
    """欢迎页面（无数据时显示）"""

    # 功能介绍（可折叠）
    with st.expander("✨ 功能介绍", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📁 数据管理
            - **数据上传**：支持CSV/Excel/JSON，自动识别类型
            - **数据预览**：统一预览管理，可调节预览行数
            - **数据清洗**：去重/替换/转换/分列/合并/修改表头/删除列
            - **数据筛选**：文本/数值/日期多条件筛选
            - **撤销/重做**：操作历史记录
            
            ### 📊 数据分析
            - **描述性统计**：均值/中位数/标准差/偏度/峰度等
            - **相关性分析**：Pearson/Spearman/Kendall
            - **分组统计**：1-3级分组，子图布局
            - **时间序列分析**：趋势图/移动平均/同比环比
            - **数据透视表**：灵活的数据透视
            """)
        
        with col2:
            st.markdown("""
            ### 📈 可视化
            - **基础图表**：柱状图/折线图/散点图/热力图/饼图
            - **复合饼图**：子图布局/交互下钻/复合定位
            - **高级图表**：箱线图/直方图/分组柱状图/堆积柱状图
            - **图表交互**：缩放/平移/悬停/点击联动
            - **图表导出**：PNG/PDF/SVG
            
            ### 🤖 AI分析
            - **可开关控制**：默认关闭
            - **API密钥配置**：支持OpenAI格式
            - **自动洞察**：生成分析报告
            
            ### ⚙️ 其他功能
            - **主题切换**：深色/浅色一键切换
            - **数据导出**：CSV/Excel/JSON
            - **图表导出**：PNG/PDF/SVG
            """)

        
def render_data_preview_page():
    """数据预览页面"""
    st.markdown("## 📊 数据预览")
    
    if st.session_state.df is None:
        st.warning("暂无数据，请先在左侧边栏上传文件")
        return
    
    # 添加刷新按钮
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔄 刷新", key="refresh_preview", use_container_width=True):
            st.rerun()
    with col2:
        st.write("")
    
    # 数据基本信息（Metric 卡片）
    render_data_info()
    
    # 预览行数设置
    preview_rows = st.slider(
        "预览行数", 
        min_value=5, 
        max_value=100, 
        value=st.session_state.preview_manager.preview_rows,
        step=5,
        key="main_preview_rows"
    )
    st.session_state.preview_manager.set_preview_rows(preview_rows)
    
    # 显示最后一次操作信息
    last_op = st.session_state.preview_manager.get_last_operation()
    if last_op:
        st.info(f"✅ 最后一次操作：{last_op['name']} ({last_op['time'].strftime('%H:%M:%S')})")
    
    # 显示数据预览
    st.markdown("### 当前数据预览")
    preview_df = st.session_state.df.head(preview_rows)
    st.dataframe(preview_df, use_container_width=True, hide_index=True)
    
    # 显示列信息（可折叠）
    with st.expander("查看列信息", expanded=False):
        render_column_info()
    
    # 数据导出
    render_data_export()

def render_data_info():
    """显示数据基本信息"""
    if st.session_state.df is None:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="总行数", 
            value=len(st.session_state.df),
            help="数据总行数"
        )
    
    with col2:
        st.metric(
            label="总列数", 
            value=len(st.session_state.df.columns),
            help="数据总列数"
        )
    
    with col3:
        missing_count = st.session_state.df.isna().sum().sum()
        st.metric(
            label="缺失值", 
            value=missing_count,
            help="缺失值总数"
        )
    
    with col4:
        memory_usage = st.session_state.df.memory_usage(deep=True).sum() / 1024
        st.metric(
            label="内存占用", 
            value=f"{memory_usage:.1f} KB",
            help="数据占用内存大小"
        )

def render_column_info():
    """显示列信息"""
    df = st.session_state.df
    
    # 过滤掉无列名的列
    valid_cols = [col for col in df.columns if col != '' and col is not None]
    
    col_info = pd.DataFrame({
        '列名': valid_cols,
        '数据类型': [df[col].dtype for col in valid_cols],
        '非空值数': [df[col].count() for col in valid_cols],
        '缺失值数': [df[col].isna().sum() for col in valid_cols],
        '唯一值数': [df[col].nunique() for col in valid_cols]
    })
    
    col_info = col_info.reset_index(drop=True)
    st.dataframe(col_info, use_container_width=True, hide_index=True)
    print(df.columns)

def render_data_export():
    """数据导出功能"""
    st.markdown("### 数据导出")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 导出为CSV", key="export_csv", use_container_width=True):
            csv = st.session_state.df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="点击下载CSV",
                data=csv,
                file_name=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_csv"
            )
    
    with col2:
        if st.button("📥 导出为Excel", key="export_excel", use_container_width=True):
            # Excel导出需要临时文件
            output = pd.ExcelWriter('temp_export.xlsx', engine='xlsxwriter')
            st.session_state.df.to_excel(output, index=False, sheet_name='Sheet1')
            output.close()
            
            with open('temp_export.xlsx', 'rb') as f:
                st.download_button(
                    label="点击下载Excel",
                    data=f,
                    file_name=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_excel"
                )
    
    with col3:
        if st.button("📥 导出为JSON", key="export_json", use_container_width=True):
            json_str = st.session_state.df.to_json(orient='records', force_ascii=False, indent=2)
            st.download_button(
                label="点击下载JSON",
                data=json_str,
                file_name=f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_json"
            )

def render_analysis_preview_page():
    """统计分析预览页面"""
    print("="*50)
    print("【调试】进入 render_analysis_preview_page 函数")
    
    st.markdown("## 📊 统计分析预览")
    # 直接调用预览管理器的显示方法
    st.session_state.preview_manager.show_stats_preview()
    # 调试信息
    with st.expander("🔍 调试信息"):
        stats = st.session_state.preview_manager.get_stats_preview()
        st.write("是否有统计结果:", stats is not None)
        if stats:
            st.write("统计类型:", stats.get('type'))
            st.write("统计形状:", stats['data'].shape if stats['data'] is not None else "None")
    
    # 检查预览管理器
    if not hasattr(st.session_state, 'preview_manager'):
        print("【调试】错误: preview_manager 不存在")
        st.error("预览管理器未初始化")
        return
    
    # 获取统计预览
    stats = st.session_state.preview_manager.get_stats_preview()
    print(f"【调试】get_stats_preview 返回: {stats is not None}")
    
    if stats and stats['data'] is not None:
        print(f"【调试】找到统计结果")
        print(f"【调试】统计类型: {stats['type']}")
        print(f"【调试】统计形状: {stats['data'].shape}")
        print(f"【调试】统计内容:\n{stats['data']}")
        
        st.markdown(f"### {stats['type']}")
        st.dataframe(stats['data'], use_container_width=True)
        
        # 导出统计结果
        if st.button("📥 导出统计结果", key="export_stats"):
            csv = stats['data'].to_csv().encode('utf-8')
            st.download_button(
                label="点击下载CSV",
                data=csv,
                file_name=f"stats_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        print("【调试】没有统计结果可显示")
        st.info("暂无统计预览，请先在右侧面板执行统计分析")
        
        # 快速入口
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 生成描述性统计", key="quick_descriptive"):
                # 这里需要调用实际的统计函数
                st.info("请在右侧面板选择列和统计指标")
        
        with col2:
            if st.button("📈 生成相关性分析", key="quick_correlation"):
                st.info("请在右侧面板选择分析方法")
    
    print("【调试】render_analysis_preview_page 函数执行完毕")
    print("="*50)

def render_chart_preview_page():
    """图表预览页面"""
    print("="*50)
    print("【调试】进入 render_chart_preview_page 函数")
    print(f"【调试】当前时间: {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("## 📈 图表预览")
    # 直接调用预览管理器的显示方法
    st.session_state.preview_manager.show_chart_preview()
    
    # 调试信息
    with st.expander("🔍 调试信息"):
        chart = st.session_state.preview_manager.get_chart_preview()
        st.write("是否有图表:", chart is not None)
        if chart:
            st.write("图表类型:", chart.get('type'))
    
    # 检查预览管理器
    if not hasattr(st.session_state, 'preview_manager'):
        print("【调试】错误: preview_manager 不存在于 session_state")
        st.error("预览管理器未初始化")
        return
    
    print(f"【调试】preview_manager 存在")
    print(f"【调试】当前预览模式: {st.session_state.get('preview_mode', '未设置')}")
    
    # 显示图表预览
    chart = st.session_state.preview_manager.get_chart_preview()
    print(f"【调试】get_chart_preview 返回: {chart is not None}")
    
    if chart and chart['figure'] is not None:
        print(f"【调试】找到图表，开始显示")
        print(f"【调试】图表类型: {chart.get('type', '未知')}")
        print(f"【调试】图表时间戳: {chart.get('timestamp', '未知')}")
        
        st.markdown(f"### {chart['type']}")
        st.plotly_chart(chart['figure'], use_container_width=True)
        print(f"【调试】图表显示完成")
        
        # 图表导出
        with st.expander("图表导出选项"):
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📥 PNG", key="preview_export_png"):
                    st.info("导出功能预留")
            with col2:
                if st.button("📥 PDF", key="preview_export_pdf"):
                    st.info("导出功能预留")
            with col3:
                if st.button("📥 SVG", key="preview_export_svg"):
                    st.info("导出功能预留")
    else:
        print(f"【调试】没有图表可显示")
        st.info("暂无图表预览，请先在右侧面板生成图表")
        
        # 快速图表生成
        with st.expander("快速生成示例图表", expanded=False):
            st.info("请在右侧分析选项标签页生成图表")
    
    print("【调试】render_chart_preview_page 函数执行完毕")
    print("="*50)

def render_chart_export(fig):
    """图表导出功能"""
    st.markdown("### 图表导出")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 导出为PNG", key="export_chart_png", use_container_width=True):
            img_bytes = managers['chart_generator'].export_chart(fig, "png")
            if img_bytes:
                st.download_button(
                    label="点击下载PNG",
                    data=img_bytes,
                    file_name=f"chart_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    key="download_png"
                )
    
    with col2:
        if st.button("📥 导出为PDF", key="export_chart_pdf", use_container_width=True):
            img_bytes = managers['chart_generator'].export_chart(fig, "pdf")
            if img_bytes:
                st.download_button(
                    label="点击下载PDF",
                    data=img_bytes,
                    file_name=f"chart_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    key="download_pdf"
                )
    
    with col3:
        if st.button("📥 导出为SVG", key="export_chart_svg", use_container_width=True):
            img_bytes = managers['chart_generator'].export_chart(fig, "svg")
            if img_bytes:
                st.download_button(
                    label="点击下载SVG",
                    data=img_bytes,
                    file_name=f"chart_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg",
                    mime="image/svg+xml",
                    key="download_svg"
                )

def render_quick_chart_options():
    """快速图表生成选项"""
    chart_type = st.selectbox(
        "选择图表类型",
        ["柱状图", "折线图", "散点图", "饼图"],
        key="quick_chart_type"
    )
    
    numeric_cols = st.session_state.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if chart_type == "饼图":
        category_cols = st.session_state.df.select_dtypes(include=['object']).columns.tolist()
        if category_cols and numeric_cols:
            cat_col = st.selectbox("分类列", category_cols, key="quick_pie_cat")
            val_col = st.selectbox("数值列", numeric_cols, key="quick_pie_val")
            if st.button("生成", key="quick_gen_pie"):
                fig = ChartGenerator.create_chart(
                    st.session_state.df, "饼图", cat_col, val_col
                )
                if fig:
                    st.session_state.preview_manager.update_chart_preview(fig, "饼图")
                    st.rerun()
    elif numeric_cols:
        x_col = st.selectbox("X轴", numeric_cols, key="quick_chart_x")
        y_col = st.selectbox("Y轴", numeric_cols, key="quick_chart_y", index=min(1, len(numeric_cols)-1)) if len(numeric_cols) > 1 else None
        if st.button("生成", key="quick_gen_chart"):
            fig = ChartGenerator.create_chart(
                st.session_state.df, chart_type, x_col, y_col
            )
            if fig:
                st.session_state.preview_manager.update_chart_preview(fig, chart_type)
                st.rerun()

def render_ai_analysis_page():
    """AI分析页面"""
    st.markdown("## 🤖 AI智能分析")
    
    if not st.session_state.get('ai_enabled', False):
        st.info("请在右侧面板启用AI分析并配置API密钥")
        return
    
    if st.session_state.df is None:
        st.warning("请先在左侧栏进行数据上传")
        return
    
    # 显示AI分析结果（如果有）
    st.markdown("### 分析结果")
    st.info("AI分析功能已启用，请在右侧面板输入分析需求")
    
    # 数据概览
    with st.expander("数据概览", expanded=False):
        st.write(f"数据量：{len(st.session_state.df)}行 × {len(st.session_state.df.columns)}列")
        st.write("字段列表：", ", ".join(st.session_state.df.columns[:10]))
        if len(st.session_state.df.columns) > 10:
            st.write(f"...等{len(st.session_state.df.columns)}个字段")

def render_settings_page():
    """设置页面"""
    st.markdown("## ⚙️ 系统设置")
    
    # 主题设置
    st.markdown("### 主题设置")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("☀️ 浅色模式", use_container_width=True):
            if st.session_state.theme_mode != 'light':
                ThemeManager.toggle_theme()
                st.rerun()
    with col2:
        if st.button("🌙 深色模式", use_container_width=True):
            if st.session_state.theme_mode != 'dark':
                ThemeManager.toggle_theme()
                st.rerun()
    
    st.divider()
    
    # 预览设置
    st.markdown("### 预览设置")
    default_preview_rows = st.number_input(
        "默认预览行数",
        min_value=5,
        max_value=100,
        value=20,
        step=5,
        key="settings_preview_rows"
    )
    if st.button("应用预览设置", key="apply_preview_settings"):
        st.session_state.preview_manager.set_preview_rows(default_preview_rows)
        st.success("预览设置已更新")
    
    st.divider()
    
    # 历史记录管理
    st.markdown("### 历史记录管理")
    if st.button("🗑️ 清空历史记录", key="clear_history"):
        managers['history'].clear_history()
        st.success("历史记录已清空")
    
    # 显示历史记录
    managers['history'].show_history()
    
    st.divider()
    
    # 调试信息
    st.markdown("### 调试信息")
    if st.button("📋 显示调试日志", key="show_logs"):
        from utils.logger import Logger
        Logger.show_logs()

# ============================================
# 主程序入口
# ============================================
def main():
    """主程序入口"""
    # 顶部区域
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("## 📊 数据洞察助手")
    with col2:
        if st.button("🌙 深色模式" if st.session_state.theme_mode == 'light' else "☀️ 浅色模式", key="top_theme"):
            ThemeManager.toggle_theme()
            st.rerun()
    with col3:
        pass
    
    st.markdown("---")
    
    # 文件上传区域（紧凑）
    with st.container():
        render_file_uploader()
    
    st.markdown("---")
    
    # 功能标签页
    tab1, tab2, tab3 = st.tabs(["🧹 数据处理", "📊 分析选项", "🤖 AI配置"])
    
    with tab1:
        render_data_processing_tab()
    with tab2:
        render_analysis_options_tab()
    with tab3:
        render_ai_config_tab()
    
    # 主内容区
    render_main_content()
    
    # 底部
    managers['footer'].show_footer()

# ============================================
# 程序启动
# ============================================
if __name__ == "__main__":
    main()