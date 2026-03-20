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
        st.session_state.theme_mode = 'dark'
    
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
    """文件上传组件（简化版）"""
    st.markdown("### 📤 数据上传")
    
    uploaded_file = st.file_uploader(
        "选择文件",
        type=['csv', 'xlsx', 'json'],
        help="支持CSV、Excel、JSON格式，最大20MB",
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        # 检查是否是新上传的文件
        current_file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        
        # 如果文件已经加载过，不再重复加载
        if st.session_state.get('last_uploaded_file_key') != current_file_key:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            # 处理Excel多工作表
            if file_extension in ['xlsx', 'xls']:
                import pandas as pd
                xl = pd.ExcelFile(uploaded_file)
                sheet_names = xl.sheet_names
                
                if len(sheet_names) > 1:
                    st.info(f"📑 检测到 {len(sheet_names)} 个工作表")
                    sheet_name = st.selectbox(
                        "选择工作表",
                        sheet_names,
                        key="excel_sheet",
                        index=0
                    )
                else:
                    sheet_name = sheet_names[0]
                
                with st.spinner(f"正在加载工作表: {sheet_name}..."):
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            else:
                with st.spinner("正在加载数据..."):
                    df = managers['file_loader'].load_file(uploaded_file)
            
            if df is not None:
                # 处理缺失值
                df = df.fillna("null")
                # 重置索引
                df = df.reset_index(drop=True)
                
                st.session_state.df = df
                st.session_state.original_df = df.copy()
                st.session_state.last_uploaded_file_key = current_file_key
                managers['history'].add_to_history("上传文件", df)
                
                st.markdown(
                    f"""
                    <div style="
                        background-color: #2A5A3A;
                        border-left: 4px solid #4CAF50;
                        padding: 1rem;
                        border-radius: 4px;
                        margin-bottom: 1rem;
                        color: #FFFFFF;
                    ">
                        ✅ 加载成功！{len(df)}行 × {len(df.columns)}列
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.session_state.preview_manager.record_operation("上传文件")
                st.rerun()
            else:
                st.error("文件加载失败，请检查文件格式")
    else:
        # 没有文件上传时，清除上次上传记录
        if 'last_uploaded_file_key' in st.session_state:
            st.session_state.last_uploaded_file_key = None

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

# ============================================
# 数据处理标签页（所有功能独立封装）
# ============================================
def render_data_processing_tab():
    """数据处理标签页"""
    if st.session_state.df is None:
        st.info("请先上传数据")
        return
    
    # 全局操作栏
    st.markdown("### ⚡ 全局操作")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    with col1:
        if st.button("↩️ 撤销", key="global_undo", use_container_width=True):
            undo_last_operation()
    with col2:
        if st.button("↪️ 重做", key="global_redo", use_container_width=True):
            redo_last_operation()
    with col3:
        if st.button("📋 历史", key="global_history", use_container_width=True):
            show_global_history()
    
    st.divider()
    
    # 数据清洗（8个标签页）
    st.markdown("### 🧹 数据清洗")
    clean_tabs = st.tabs(["🗑️ 去重", "🔄 替换", "📝 转换", "✂️ 分列", "🔗 合并", "✏️ 表头", "🔍 筛选", "🗑️ 删除"])
    
    with clean_tabs[0]:
        render_deduplicate_section()
    
    with clean_tabs[1]:
        render_replace_value_section()
    
    with clean_tabs[2]:
        render_convert_type_section()
    
    with clean_tabs[3]:
        render_split_column_section()
    
    with clean_tabs[4]:
        render_merge_columns_section()
    
    with clean_tabs[5]:  # 新增：修改表头
        render_rename_columns_section()
    
    with clean_tabs[6]:  # 筛选（原第6个变为第8个）
        render_filter_section_in_tab()
    
    with clean_tabs[7]:  # 删除（原第5个变为第7个）
        
        render_delete_columns_section()
    
    st.divider()
    
    # 数据确认
    render_confirm_data_button()
    
# ============================================
# 统一筛选功能（放在这里）
# ============================================

def render_rename_columns_section():
    """修改表头功能"""
    st.write("修改列名称（表头）")
    
    # 获取当前所有列名
    current_columns = st.session_state.df.columns.tolist()
    
    # 显示当前列名
    st.markdown("**当前列名**")
    col_df = pd.DataFrame({
        '序号': range(1, len(current_columns) + 1),
        '当前列名': current_columns
    })
    st.dataframe(col_df, use_container_width=True)
    
    st.markdown("---")
    
    # 修改方式选择
    rename_mode = st.radio(
        "选择修改方式",
        ["单个修改", "批量添加前缀/后缀", "批量替换文本", "批量修改（编辑表格）"],
        key="rename_mode",
        horizontal=True
    )
    
    # 方式一：单个修改
    if rename_mode == "单个修改":
        col1, col2 = st.columns(2)
        
        with col1:
            old_name = st.selectbox("选择要修改的列", current_columns, key="rename_single_old")
        
        with col2:
            new_name = st.text_input("新列名", value=old_name, key="rename_single_new")
        
        if st.button("✏️ 应用修改", key="btn_rename_single", use_container_width=True):
            if new_name and new_name != old_name:
                if new_name in current_columns and new_name != old_name:
                    st.warning(f"列名 '{new_name}' 已存在，请使用其他名称")
                else:
                    # 执行重命名
                    new_columns = [new_name if col == old_name else col for col in current_columns]
                    st.session_state.df.columns = new_columns
                    st.session_state.preview_manager.record_operation(f"修改表头: {old_name}→{new_name}")
                    managers['history'].add_to_history("修改表头", st.session_state.df)
                    st.success(f"已将 '{old_name}' 修改为 '{new_name}'")
                    st.rerun()
            else:
                st.warning("请输入新列名")
    
    # 方式二：批量添加前缀/后缀
    elif rename_mode == "批量添加前缀/后缀":
        col1, col2 = st.columns(2)
        
        with col1:
            prefix = st.text_input("添加前缀", key="rename_prefix", placeholder="留空则不添加")
        
        with col2:
            suffix = st.text_input("添加后缀", key="rename_suffix", placeholder="留空则不添加")
        
        # 预览效果
        if prefix or suffix:
            preview_cols = []
            for col in current_columns[:5]:
                new_col = col
                if prefix:
                    new_col = prefix + new_col
                if suffix:
                    new_col = new_col + suffix
                preview_cols.append(new_col)
            
            st.caption(f"预览效果: {', '.join(preview_cols)}{'...' if len(current_columns) > 5 else ''}")
        
        if st.button("✏️ 批量添加", key="btn_rename_prefix_suffix", use_container_width=True):
            if not prefix and not suffix:
                st.warning("请至少输入前缀或后缀")
            else:
                new_columns = []
                for col in current_columns:
                    new_col = col
                    if prefix:
                        new_col = prefix + new_col
                    if suffix:
                        new_col = new_col + suffix
                    new_columns.append(new_col)
                
                st.session_state.df.columns = new_columns
                st.session_state.preview_manager.record_operation(f"批量添加: 前缀='{prefix}' 后缀='{suffix}'")
                managers['history'].add_to_history("修改表头", st.session_state.df)
                st.success("批量添加完成")
                st.rerun()
    
    # 方式三：批量替换文本
    elif rename_mode == "批量替换文本":
        col1, col2 = st.columns(2)
        
        with col1:
            old_text = st.text_input("查找内容", key="rename_replace_old")
        
        with col2:
            new_text = st.text_input("替换为", key="rename_replace_new")
        
        # 预览效果
        if old_text:
            preview_cols = []
            for col in current_columns[:5]:
                new_col = col.replace(old_text, new_text)
                preview_cols.append(new_col)
            st.caption(f"预览效果: {', '.join(preview_cols)}{'...' if len(current_columns) > 5 else ''}")
        
        if st.button("✏️ 批量替换", key="btn_rename_replace", use_container_width=True):
            if not old_text:
                st.warning("请输入要查找的内容")
            else:
                new_columns = [col.replace(old_text, new_text) for col in current_columns]
                st.session_state.df.columns = new_columns
                st.session_state.preview_manager.record_operation(f"批量替换: '{old_text}'→'{new_text}'")
                managers['history'].add_to_history("修改表头", st.session_state.df)
                st.success("批量替换完成")
                st.rerun()
    
    # 方式四：批量修改（编辑表格）
    else:
        st.markdown("**编辑表格修改列名**")
        st.caption("双击单元格直接编辑，支持批量修改")
        
        # 创建可编辑表格
        edit_df = pd.DataFrame({
            '当前列名': current_columns,
            '新列名': current_columns.copy()
        })
        
        edited_df = st.data_editor(
            edit_df,
            use_container_width=True,
            num_rows="fixed",
            key="rename_editor",
            column_config={
                "当前列名": st.column_config.TextColumn("当前列名", disabled=True),
                "新列名": st.column_config.TextColumn("新列名", required=True)
            }
        )
        
        # 检查是否有重复
        new_names = edited_df['新列名'].tolist()
        has_duplicate = len(new_names) != len(set(new_names))
        
        if has_duplicate:
            st.error("新列名存在重复，请修改后重试")
        else:
            # 显示修改预览
            changes = []
            for old, new in zip(current_columns, new_names):
                if old != new:
                    changes.append(f"'{old}' → '{new}'")
            
            if changes:
                st.info(f"将修改 {len(changes)} 个列名")
                with st.expander("查看修改详情"):
                    for change in changes[:10]:
                        st.write(f"• {change}")
                    if len(changes) > 10:
                        st.write(f"...等{len(changes)}个修改")
        
        if st.button("✏️ 应用所有修改", key="btn_rename_batch", use_container_width=True):
            if has_duplicate:
                st.error("请先解决重复列名问题")
            else:
                st.session_state.df.columns = new_names
                st.session_state.preview_manager.record_operation("批量修改表头")
                managers['history'].add_to_history("修改表头", st.session_state.df)
                st.success(f"已修改 {len([c for c in changes if c])} 个列名")
                st.rerun()

def render_filter_section_in_tab():
    """筛选功能（作为完整的标签页显示）"""
    
    # 筛选历史快捷操作（放在顶部）
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("↩️ 撤销筛选", key="undo_filter_tab", use_container_width=True):
            undo_last_operation()  # 改为使用全局撤销
    with col2:
        if st.button("🔄 重置", key="reset_filter_tab", use_container_width=True):
            reset_to_original()  # 这个函数如果存在就保留
    with col3:
        if st.button("📋 筛选历史", key="filter_history_tab", use_container_width=True):
            show_global_history()  # 改为使用全局历史
    
    st.markdown("---")
    
    # 筛选主界面
    st.markdown("#### 设置筛选条件")
    
    # 选择列
    all_cols = ["请选择要筛选的列"] + st.session_state.df.columns.tolist()
    selected_col = st.selectbox(
        "选择列",
        all_cols,
        key="filter_column_tab",
        index=0
    )
    
    if selected_col != "请选择要筛选的列":
        # 获取列的数据类型
        col_dtype = st.session_state.df[selected_col].dtype
        is_numeric = pd.api.types.is_numeric_dtype(col_dtype)
        is_datetime = pd.api.types.is_datetime64_any_dtype(col_dtype)
        
        # 根据数据类型提供不同的条件选项
        if is_numeric:
            conditions = ["等于", "不等于", "大于", "小于", "大于等于", "小于等于", "介于", "为空", "不为空"]
        elif is_datetime:
            conditions = ["等于", "不等于", "早于", "晚于", "介于", "今天", "本周", "本月", "为空", "不为空"]
        else:
            conditions = ["包含", "不包含", "等于", "不等于", "开头为", "结尾为", "为空", "不为空"]
        
        # 使用列布局让界面更紧凑
        col1, col2 = st.columns([1, 2])
        with col1:
            condition = st.selectbox("条件", conditions, key="filter_condition_tab")
        with col2:
            # 根据条件类型提供不同的输入界面
            filter_value = None
            
            if condition not in ["为空", "不为空", "今天", "本周", "本月"]:
                if condition == "介于":
                    subcol1, subcol2 = st.columns(2)
                    with subcol1:
                        if is_numeric:
                            min_val = st.number_input("最小值", key="filter_min_tab")
                        else:
                            min_val = st.text_input("开始值", key="filter_min_tab")
                    with subcol2:
                        if is_numeric:
                            max_val = st.number_input("最大值", key="filter_max_tab")
                        else:
                            max_val = st.text_input("结束值", key="filter_max_tab")
                    filter_value = (min_val, max_val)
                else:
                    if is_numeric and condition not in ["包含", "不包含", "开头为", "结尾为"]:
                        filter_value = st.number_input("筛选值", key="filter_value_tab")
                    else:
                        filter_value = st.text_input("筛选值", key="filter_value_tab")
        
        # 操作按钮
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🔍 预览结果", key="preview_filter_tab", use_container_width=True):
                preview_unified_filter(selected_col, condition, filter_value)
        with col2:
            if st.button("✅ 应用筛选", key="apply_filter_tab", use_container_width=True, type="primary"):
                apply_unified_filter(selected_col, condition, filter_value)
        with col3:
            st.write("")  # 占位
    
    # 预览结果显示
    if 'filter_preview' in st.session_state and st.session_state.filter_preview is not None:
        st.markdown("---")
        st.markdown("### 👁️ 预览结果")
        if 'filter_preview_info' in st.session_state:
            st.info(st.session_state.filter_preview_info)
        st.dataframe(st.session_state.filter_preview, use_container_width=True)
        
        if st.button("关闭预览", key="close_filter_preview_tab"):
            st.session_state.filter_preview = None
            st.session_state.filter_preview_info = None
            st.rerun()
                
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

def render_confirm_data_button():
    """确认使用本数据按钮"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 确认数据")
        st.caption("点击确认后，当前数据将作为分析基准")
    with col2:
        if st.button("✅ 确认使用本数据", key="confirm_data", type="primary", use_container_width=True):
            confirm_current_data()

def confirm_current_data():
    """确认当前数据"""
    st.session_state.confirmed_data = st.session_state.df.copy()
    st.session_state.data_confirmed = True
    st.success("数据已确认，将作为后续分析的基准")
    
    # 记录确认操作
    st.session_state.preview_manager.record_operation("数据确认")



def render_deduplicate_section():
    """去重功能"""
    with st.expander("🗑️ 去重", expanded=False):
        st.write("删除重复行")
        
        subset_cols = st.multiselect(
            "选择列（留空则基于所有列）", 
            st.session_state.df.columns,
            key="dedup_cols"
        )
        
        keep_option = st.selectbox(
            "保留方式",
            ["保留第一个", "保留最后一个", "全部删除"],
            key="dedup_keep"
        )
        
        keep_map = {
            "保留第一个": "first",
            "保留最后一个": "last",
            "全部删除": False
        }
        
        if st.button("✅ 执行去重", key="btn_dedup", use_container_width=True):
            success, message = execute_data_operation(
                managers['data_cleaner'].deduplicate,
                "去重",
                subset=subset_cols if subset_cols else None,
                keep=keep_map[keep_option]
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

def render_replace_value_section():
    """替换值功能"""
    with st.expander("🔄 替换值", expanded=False):
        col = st.selectbox(
            "选择列", 
            st.session_state.df.columns, 
            key="replace_col"
        )
        
        mode = st.radio(
            "替换方式", 
            ["文本替换", "正则替换", "空值替换"], 
            key="replace_mode",
            horizontal=True
        )
        
        if mode == "文本替换":
            old = st.text_input("查找内容", key="replace_old")
            new = st.text_input("替换为", key="replace_new")
            
            if st.button("✅ 执行文本替换", key="btn_replace", use_container_width=True):
                success, message = execute_data_operation(
                    managers['data_cleaner'].text_replace,
                    "文本替换",
                    col, old, new
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        elif mode == "正则替换":
            pattern = st.text_input("正则表达式", key="replace_pattern")
            replacement = st.text_input("替换为", key="replace_replacement")
            
            if st.button("✅ 执行正则替换", key="btn_regex_replace", use_container_width=True):
                success, message = execute_data_operation(
                    managers['data_cleaner'].text_replace,
                    "正则替换",
                    col, pattern, replacement, regex=True
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        else:  # 空值替换
            fill_value = st.text_input("填充值", "", key="replace_fill")
            
            if st.button("✅ 执行空值替换", key="btn_null_replace", use_container_width=True):
                success, message = execute_data_operation(
                    managers['data_cleaner'].null_replace,
                    "空值替换",
                    col, fill_value
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def render_convert_type_section():
    """类型转换功能"""
    with st.expander("📝 类型转换", expanded=False):
        col = st.selectbox(
            "选择列", 
            st.session_state.df.columns, 
            key="convert_col"
        )
        
        target_type = st.radio(
            "转换类型", 
            ["转换为文本", "转换为数值"], 
            key="convert_type",
            horizontal=True
        )
        
        if st.button("✅ 执行转换", key="btn_convert", use_container_width=True):
            success, message = execute_data_operation(
                managers['data_cleaner'].convert_type,
                "类型转换",
                col, target_type
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

def render_split_column_section():
    """分列功能"""
    with st.expander("✂️ 分列", expanded=False):
        col = st.selectbox(
            "选择列", 
            st.session_state.df.columns, 
            key="split_col"
        )
        
        mode = st.radio(
            "分列方式", 
            ["最左分隔符", "最右分隔符"], 
            key="split_mode",
            horizontal=True
        )
        
        separator = st.text_input("分隔符", ",", key="split_sep")
        
        # 预览分列效果
        if st.button("👁️ 预览分列", key="preview_split", use_container_width=True):
            preview_df = st.session_state.df.head(3).copy()
            preview_result = managers['data_cleaner'].split_column(
                preview_df, col, separator, mode
            )
            st.write("预览结果（前3行）：")
            st.dataframe(preview_result, use_container_width=True)
            new_cols = [c for c in preview_result.columns if c not in st.session_state.df.columns]
            if new_cols:
                st.info(f"将新增列: {', '.join(new_cols)}")
        
        if st.button("✅ 执行分列", key="btn_split", use_container_width=True):
            success, message = execute_data_operation(
                managers['data_cleaner'].split_column,
                "分列",
                col, separator, mode
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

def render_merge_columns_section():
    """合并列功能"""
    with st.expander("🔗 合并列", expanded=False):
        st.write("将多列合并为一列")
        
        merge_cols = st.multiselect(
            "选择要合并的列（按顺序选择）", 
            st.session_state.df.columns,
            key="merge_cols"
        )
        
        if len(merge_cols) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                separator = st.text_input("分隔符", value=" ", key="merge_sep")
            with col2:
                merge_position = st.radio(
                    "合并后位置",
                    ["保留原列", "删除原列"],
                    key="merge_position",
                    horizontal=True
                )
            
            new_col_name = st.text_input(
                "新列名", 
                value="_".join(merge_cols)[:30],
                key="new_col_name"
            )
            
            # 预览合并效果
            if st.button("👁️ 预览合并", key="preview_merge", use_container_width=True):
                preview_df = st.session_state.df.head(3).copy()
                preview_df = managers['data_cleaner'].merge_columns(
                    preview_df, merge_cols, new_col_name, separator
                )
                st.write("预览结果（前3行）：")
                st.dataframe(preview_df[[new_col_name] + merge_cols], use_container_width=True)
            
            # 执行合并
            if st.button("✅ 执行合并", key="btn_merge", use_container_width=True):
                # 先执行合并
                success, message = execute_data_operation(
                    managers['data_cleaner'].merge_columns,
                    "合并列",
                    merge_cols, new_col_name, separator
                )
                
                if success:
                    # 根据选择决定是否删除原列
                    if merge_position == "删除原列":
                        st.session_state.df = st.session_state.df.drop(columns=merge_cols)
                        st.session_state.preview_manager.record_operation("删除原列")
                    
                    st.success(f"合并完成，新增列：{new_col_name}")
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("请至少选择2列进行合并")
def render_delete_columns_section():
    """删除列功能"""
    st.write("删除指定的列")
    
    cols_to_delete = st.multiselect(
        "选择要删除的列", 
        st.session_state.df.columns,
        key="delete_cols_section"
    )
    
    if cols_to_delete:
        # 显示预览信息
        st.caption(f"将删除 {len(cols_to_delete)} 列: {', '.join(cols_to_delete)}")
        
        if st.button("🗑️ 执行删除", key="btn_delete_section", use_container_width=True, type="primary"):
            success, message = execute_data_operation(
                managers['data_cleaner'].delete_columns,
                "删除列",
                cols_to_delete
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    else:
        st.info("请选择要删除的列")

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
def render_analysis_options_tab():
    """分析选项标签页（整合统计和图表）"""
    if st.session_state.df is None:
        st.info("请先上传数据")
        return
    
    # 使用tabs组织不同类型的分析（增加复合饼图）
    analysis_tabs = st.tabs([
        "📈 描述性统计", 
        "🔗 相关性分析", 
        "📊 分组统计", 
        "⏱️ 时间序列", 
        "📐 数据透视表",
        "🥧 复合饼图"  # 新增复合饼图标签页
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
    
    with analysis_tabs[5]:  # 复合饼图
        render_composite_pie_chart()
        
def render_composite_pie_chart():
    """复合饼图（三种模式）"""
    st.markdown("#### 🥧 复合饼图")
    
    # 获取分类列和数值列
    category_cols = st.session_state.df.select_dtypes(include=['object']).columns.tolist()
    numeric_cols = st.session_state.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if not category_cols:
        st.warning("需要分类列才能生成复合饼图")
        return
    
    if not numeric_cols:
        st.warning("需要数值列才能生成复合饼图")
        return
    
    # 基本设置
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
    
    # 复合饼图模式选择
    st.markdown("##### 选择模式")
    pie_mode = st.radio(
        "复合饼图模式",
        ["子图布局", "交互下钻", "复合定位"],
        key="composite_pie_mode",
        horizontal=True,
        help="""
        - 子图布局：网格展示主图和子图
        - 交互下钻：点击主图区块查看详情
        - 复合定位：预设模板布局
        """
    )
    
    # 模式说明
    if pie_mode == "子图布局":
        st.info("📊 子图布局模式：主图在左上角，其他子图按网格排列，适合对比分析多个类别")
    elif pie_mode == "交互下钻":
        st.info("🖱️ 交互下钻模式：点击主图区块，下方显示该区块的详细构成，适合层级探索")
    else:
        st.info("🎯 复合定位模式：主图居中，子图按预设位置环绕，适合报告展示")
    
    # 高级选项
    with st.expander("高级选项"):
        max_categories = st.slider(
            "最大显示类别数",
            min_value=3,
            max_value=10,
            value=5,
            key="composite_max_cat",
            help="主图显示的类别数量，其余归为'其他'"
        )
        
        show_title = st.checkbox("显示图表标题", value=True, key="composite_title")
        
        if pie_mode == "子图布局":
            chart_height = st.slider(
                "图表高度",
                min_value=400,
                max_value=1000,
                value=800,
                step=50,
                key="composite_height"
            )
    
    # 生成图表按钮
    if st.button("🎨 生成复合饼图", key="btn_composite_pie", use_container_width=True, type="primary"):
        with st.spinner(f"正在生成{pie_mode}复合饼图..."):
            try:
                # 调用 chart_generator 中的复合饼图函数
                fig = managers['chart_generator'].create_chart(
                    df=st.session_state.df,
                    chart_type="复合饼图",
                    x_col=category_col,  # 分类列
                    y_col=value_col,      # 数值列
                    pie_mode=pie_mode,    # 模式选择
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
            category_counts = st.session_state.df[category_col].value_counts().head(max_categories)
            st.dataframe(category_counts.reset_index(), use_container_width=True)
        
        with col2:
            st.markdown("##### 数值汇总")
            category_sums = st.session_state.df.groupby(category_col)[value_col].sum().sort_values(ascending=False).head(max_categories)
            st.dataframe(category_sums.reset_index(), use_container_width=True)

def get_pie_mode_description(mode):
    """获取复合饼图模式说明"""
    descriptions = {
        "子图布局": "📊 网格展示：主图在左上角，其他子图按网格排列，适合对比分析多个类别",
        "交互下钻": "🖱️ 点击交互：点击主图区块，下方显示该区块的详细构成，适合层级探索",
        "复合定位": "🎯 预设模板：主图居中，子图按预设位置环绕，适合报告展示"
    }
    return descriptions.get(mode, "")

# def render_descriptive_stats_with_chart():
#     """
#     描述性统计 + 图表功能
#     ===================================
#     这是一个【完整版】函数，包含：
#     1. 列选择（数值列/文本列）
#     2. 统计指标选择
#     3. 图表类型选择
#     4. 【测试按钮】用于诊断
#     5. 【生产按钮】已启用
#     6. 调试信息面板
#     ===================================
#     """
    
#     st.markdown("#### 描述性统计")
    
#     # ===========================================
#     # 第一部分：获取列信息
#     # ===========================================
#     all_cols = st.session_state.df.columns.tolist()
#     numeric_cols = st.session_state.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
#     category_cols = st.session_state.df.select_dtypes(include=['object']).columns.tolist()
    
#     if not all_cols:
#         st.warning("没有数据可供统计")
#         return
    
#     # ===========================================
#     # 第二部分：列选择
#     # ===========================================
#     col_options = []
#     for col in all_cols:
#         if col in numeric_cols:
#             col_options.append(f"🔢 {col} (数值)")
#         else:
#             col_options.append(f"📝 {col} (文本)")
    
#     col_map = {f"🔢 {col} (数值)": col for col in numeric_cols}
#     col_map.update({f"📝 {col} (文本)": col for col in category_cols})
    
#     selected_display = st.multiselect(
#         "选择要分析的列",
#         col_options,
#         key="desc_cols_main",
#         placeholder="请选择要分析的列"
#     )
    
#     selected_cols = [col_map[disp] for disp in selected_display if disp in col_map]
    
#     if not selected_cols:
#         st.info("请选择要分析的列")
#         return
    
#     # ===========================================
#     # 第三部分：分离数值列和文本列
#     # ===========================================
#     selected_numeric = [col for col in selected_cols if col in numeric_cols]
#     selected_category = [col for col in selected_cols if col in category_cols]
    
#     # ===========================================
#     # 第四部分：统计选项和图表选项
#     # ===========================================
#     col_left, col_right = st.columns(2)
    
#     with col_left:
#         st.markdown("##### 统计选项")
        
#         # 数值列统计指标
#         numeric_stats = []
#         if selected_numeric:
#             st.markdown("**数值列统计**")
#             numeric_stats = st.multiselect(
#                 "选择数值统计指标",
#                 ["均值", "中位数", "众数", "标准差", "方差", "最小值", "最大值", 
#                  "极差", "偏度", "峰度", "25%分位数", "50%分位数", "75%分位数", "缺失值"],
#                 key="numeric_stats_main",
#                 placeholder="请选择数值统计指标"
#             )
        
#         # 文本列统计指标
#         category_stats = []
#         if selected_category:
#             st.markdown("**文本列统计**")
#             category_stats = st.multiselect(
#                 "选择文本统计指标",
#                 ["计数", "唯一值数", "最频繁值", "缺失值"],
#                 key="category_stats_main",
#                 placeholder="请选择文本统计指标"
#             )
    
#     with col_right:
#         st.markdown("##### 图表选项")
        
#         # 图表类型选择
#         chart_options = ["请选择图表类型"]
#         if selected_numeric:
#             chart_options.extend(["柱状图", "箱线图", "直方图"])
#         if selected_category:
#             chart_options.extend(["条形图", "饼图"])
        
#         chart_type = st.selectbox(
#             "选择图表类型",
#             chart_options,
#             key="chart_type_main",
#             index=0
#         )
        
#         # 直方图特殊参数
#         bins = 20
#         if chart_type == "直方图" and selected_numeric:
#             bins = st.slider("分组数", min_value=5, max_value=50, value=20, key="hist_bins_main")
    
#     # ===========================================
#     # 第五部分：状态计算
#     # ===========================================
#     has_stats = (selected_numeric and numeric_stats) or (selected_category and category_stats)
#     chart_ready = chart_type != "请选择图表类型"
    
#     # ===========================================
#     # 第六部分：【测试按钮】（保留用于诊断）
#     # ===========================================
#     st.markdown("---")
#     st.markdown("##### 🧪 测试模式（用于诊断）")
    
#     col_test1, col_test2 = st.columns(2)
    
#     with col_test1:
#         if st.button("🧪 [测试] 生成统计表", key="test_stats_btn", use_container_width=True):
#             with st.spinner("正在生成测试统计表..."):
#                 try:
#                     import pandas as pd
#                     test_data = {}
#                     for col in selected_cols:
#                         test_data[col] = [len(st.session_state.df[col])]
#                     test_df = pd.DataFrame(test_data, index=['计数值'])
                    
#                     st.session_state.preview_manager.update_stats_preview(
#                         test_df,
#                         f"【测试】统计结果 ({', '.join(selected_cols[:2])})"
#                     )
#                     st.session_state.preview_mode = 'stats'
#                     st.session_state.current_page = "📊 数据分析"
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"测试失败: {str(e)}")
    
#     with col_test2:
#         if st.button("🧪 [测试] 生成图表", key="test_chart_btn", use_container_width=True):
#             with st.spinner("正在生成测试图表..."):
#                 try:
#                     import plotly.express as px
#                     import pandas as pd
#                     test_data = pd.DataFrame({'类别': ['A', 'B', 'C', 'D'], '数值': [10, 20, 15, 25]})
#                     fig = px.bar(test_data, x='类别', y='数值', title="【测试】条形图")
                    
#                     st.session_state.preview_manager.update_chart_preview(fig, "【测试】图表")
#                     st.session_state.preview_mode = 'chart'
#                     st.session_state.current_page = "📈 可视化"
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"测试失败: {str(e)}")
    
#     # ===========================================
#     # 第七部分：【生产模式按钮】已启用
#     # ===========================================
#     st.markdown("---")
#     st.markdown("##### 📦 生产模式")
    
#     col_prod1, col_prod2 = st.columns(2)
    
#     with col_prod1:
#         if st.button("📊 生成统计表", key="prod_stats", use_container_width=True, disabled=not has_stats):
#             if not has_stats:
#                 st.warning("请先选择统计指标")
#             else:
#                 with st.spinner("正在生成统计表..."):
#                     try:
#                         import pandas as pd
#                         results = {}
                        
#                         # 处理数值列
#                         if selected_numeric and numeric_stats:
#                             stats_df = managers['stats_analyzer'].descriptive_stats(
#                                 st.session_state.df[selected_numeric]
#                             )
#                             if stats_df is not None and not stats_df.empty:
#                                 available_stats = [s for s in numeric_stats if s in stats_df.columns]
#                                 if available_stats:
#                                     results["数值统计"] = stats_df[available_stats]
                        
#                         # 处理文本列
#                         if selected_category and category_stats:
#                             cat_results = {}
#                             for col in selected_category:
#                                 cat_stats = {}
#                                 if "计数" in category_stats:
#                                     cat_stats["计数"] = len(st.session_state.df[col])
#                                 if "唯一值数" in category_stats:
#                                     cat_stats["唯一值数"] = st.session_state.df[col].nunique()
#                                 if "最频繁值" in category_stats:
#                                     cat_stats["最频繁值"] = st.session_state.df[col].mode().iloc[0] if not st.session_state.df[col].mode().empty else "N/A"
#                                 if "缺失值" in category_stats:
#                                     cat_stats["缺失值"] = st.session_state.df[col].isna().sum()
#                                 cat_results[col] = cat_stats
#                             results["文本统计"] = pd.DataFrame(cat_results).T
                        
#                         if results:
#                             if len(results) == 1:
#                                 result_df = list(results.values())[0]
#                             else:
#                                 result_df = pd.concat(results, axis=1)
                            
#                             st.session_state.preview_manager.update_stats_preview(
#                                 result_df,
#                                 f"描述性统计 ({', '.join(selected_cols[:3])}{'...' if len(selected_cols)>3 else ''})"
#                             )
#                             st.session_state.preview_mode = 'stats'
#                             st.session_state.current_page = "📊 数据分析"
#                             st.rerun()
#                         else:
#                             st.warning("没有生成任何统计结果")
                            
#                     except Exception as e:
#                         st.error(f"统计表生成失败: {str(e)}")
    
#     with col_prod2:
#         if st.button("📈 生成图表", key="prod_chart", use_container_width=True, disabled=not chart_ready):
#             if not chart_ready:
#                 st.warning("请先选择图表类型")
#             else:
#                 with st.spinner("正在生成图表..."):
#                     try:
#                         import plotly.express as px
#                         import pandas as pd
                        
#                         for col in selected_cols:
#                             fig = None
                            
#                             if col in numeric_cols:
#                                 if chart_type == "柱状图":
#                                     fig = managers['chart_generator'].create_chart(
#                                         st.session_state.df, "柱状图", col, col
#                                     )
#                                 elif chart_type == "箱线图":
#                                     fig = managers['chart_generator'].create_chart(
#                                         st.session_state.df, "箱线图", None, col
#                                     )
#                                 elif chart_type == "直方图":
#                                     fig = managers['chart_generator'].create_chart(
#                                         st.session_state.df, "直方图", col, bins=bins
#                                     )
#                             else:
#                                 if chart_type == "条形图" or chart_type == "柱状图":
#                                     freq_df = st.session_state.df[col].value_counts().reset_index()
#                                     freq_df.columns = [col, "频数"]
#                                     fig = managers['chart_generator'].create_chart(
#                                         freq_df.head(20), "柱状图", col, "频数"
#                                     )
#                                 elif chart_type == "饼图":
#                                     freq_df = st.session_state.df[col].value_counts().reset_index()
#                                     freq_df.columns = [col, "频数"]
#                                     fig = managers['chart_generator'].create_chart(
#                                         freq_df.head(10), "饼图", col, "频数"
#                                     )
                            
#                             if fig:
#                                 st.session_state.preview_manager.update_chart_preview(
#                                     fig, f"{col}-{chart_type}"
#                                 )
#                                 st.session_state.preview_mode = 'chart'
#                                 st.session_state.current_page = "📈 可视化"
#                                 st.rerun()
#                             else:
#                                 st.error(f"{col}的{chart_type}生成失败")
                                
#                     except Exception as e:
#                         st.error(f"图表生成失败: {str(e)}")
    
#     # ===========================================
#     # 第八部分：状态提示和调试信息
#     # ===========================================
#     st.markdown("---")
    
#     # 状态提示
#     col_status1, col_status2, col_status3 = st.columns(3)
#     with col_status1:
#         st.caption(f"📊 已选列: {len(selected_cols)}列")
#     with col_status2:
#         st.caption(f"📈 统计指标: {len(numeric_stats) + len(category_stats)}个")
#     with col_status3:
#         st.caption(f"🎨 图表: {chart_type}")
    
#     # 按钮状态提示
#     st.info(f"统计表按钮: {'✅ 可用' if has_stats else '❌ 需选择指标'} | 图表按钮: {'✅ 可用' if chart_ready else '❌ 需选择图表类型'}")
    
#     # 调试信息面板
#     with st.expander("🔍 调试信息面板", expanded=False):
#         st.json({
#             "selected_cols": selected_cols,
#             "selected_numeric": selected_numeric,
#             "selected_category": selected_category,
#             "numeric_stats": numeric_stats,
#             "category_stats": category_stats,
#             "chart_type": chart_type,
#             "has_stats": has_stats,
#             "chart_ready": chart_ready
#         })

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
    
    # 【修复】直接使用列名，不使用索引
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
    # 【关键修复】重置索引并隐藏
    col_info_df = col_info_df.reset_index(drop=True)
    st.dataframe(col_info_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # ===========================================
    # 第三部分：数值列统计摘要
    # ===========================================
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if numeric_cols:
        st.markdown("##### 数值列统计摘要")
        
        # 获取描述性统计
        desc_df = df[numeric_cols].describe(percentiles=[.25, .5, .75]).round(2)
        
        # 【关键修复】将索引转换为列，并重置
        desc_df = desc_df.reset_index()
        desc_df = desc_df.rename(columns={"index": "统计指标"})
        
        # 重置索引
        desc_df = desc_df.reset_index(drop=True)
        
        st.dataframe(desc_df, use_container_width=True, hide_index=True)
        
        # 高级统计指标
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
        # 【关键修复】重置索引
        text_stats_df = text_stats_df.reset_index(drop=True)
        st.dataframe(text_stats_df, use_container_width=True, hide_index=True)
        
        # 显示各列的频数分布
        with st.expander("查看各列频数分布"):
            for col in text_cols[:3]:
                st.markdown(f"**{col}**")
                freq = df[col].value_counts().head(10).reset_index()
                freq.columns = [col, "频数"]
                # 【关键修复】重置索引
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
            
            with open('data_overview.xlsx', 'rb') as f:
                st.download_button(
                    label="点击下载Excel报告",
                    data=f,
                    file_name=f"data_overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_full_stats"
                )
def render_correlation_with_heatmap():
    """相关性分析 + 热力图"""
    st.markdown("#### 相关性分析")
    
    numeric_cols = st.session_state.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("需要至少2个数值列才能进行相关性分析")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 列选择 - 没有默认值
        selected_cols = st.multiselect(
            "选择要分析的列",
            numeric_cols,
            key="corr_cols_chart",
            placeholder="请至少选择2列"
        )
        
        if selected_cols and len(selected_cols) >= 2:
            # 方法选择
            method = st.selectbox(
                "选择分析方法",
                ["请选择方法", "pearson", "spearman", "kendall"],
                key="corr_method_chart",
                format_func=lambda x: {
                    "请选择方法": "请选择分析方法",
                    "pearson": "皮尔逊 (线性相关)",
                    "spearman": "斯皮尔曼 (秩相关)",
                    "kendall": "肯德尔 (一致性)"
                }.get(x, x),
                index=0
            )
    
    with col2:
        if selected_cols and len(selected_cols) >= 2 and method != "请选择方法":
            # 图表选项
            st.markdown("##### 图表设置")
            show_values = st.checkbox("显示相关系数", value=True, key="corr_show_values")
            color_scale = st.selectbox(
                "选择色阶",
                ["RdBu_r", "Viridis", "Plasma", "Inferno"],
                key="corr_colorscale"
            )
    
    # 操作按钮
    if selected_cols and len(selected_cols) >= 2 and method != "请选择方法":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 生成相关性矩阵", key="btn_corr_matrix", use_container_width=True):
                with st.spinner("正在计算相关性..."):
                    corr_df = managers['stats_analyzer'].correlation_analysis(
                        st.session_state.df[selected_cols], method
                    )
                    if corr_df is not None and not corr_df.empty:
                        st.session_state.preview_manager.update_stats_preview(
                            corr_df, 
                            f"{method}相关性矩阵"
                        )
                        st.success("相关性矩阵已生成")
                        st.rerun()
        
        with col2:
            if st.button("🔥 生成热力图", key="btn_corr_heatmap", use_container_width=True):
                with st.spinner("正在生成热力图..."):
                    try:
                        fig = managers['chart_generator'].create_chart(
                            st.session_state.df[selected_cols], 
                            "热力图",
                            colorscale=color_scale,
                            show_values=show_values
                        )
                        if fig:
                            st.session_state.preview_manager.update_chart_preview(
                                fig, 
                                f"{method}相关性热力图"
                            )
                            st.success("热力图已生成")
                            st.rerun()
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
        
        with col3:
            st.caption(f"分析 {len(selected_cols)} 列的相关性")
    else:
        st.info("请依次选择：至少2列 → 分析方法")
            
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
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        group_cols = st.multiselect(
            "选择分组字段",
            category_cols,
            key="group_cols_chart",
            placeholder="请选择分组字段"
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
    
    with col2:
        if group_cols and value_cols and agg_func != "请选择聚合函数":
            chart_options = ["请选择图表类型", "柱状图", "折线图", "饼图", "条形图"]
            chart_type = st.selectbox(
                "选择图表类型",
                chart_options,
                key="group_chart_type",
                index=0
            )
            
            if chart_type != "请选择图表类型":
                if chart_type == "饼图":
                    st.info("饼图只显示第一个分组字段")
                
                sort_by = st.checkbox("排序显示", value=True, key="group_sort")
                show_values = st.checkbox("显示数值", value=True, key="group_show_values")
    
    if group_cols and value_cols and agg_func != "请选择聚合函数":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 执行分组统计", key="btn_group_calc", use_container_width=True):
                with st.spinner("正在计算分组统计..."):
                    try:
                        # 【修复】处理空值
                        df_clean = st.session_state.df.copy()
                        for col in group_cols:
                            df_clean[col] = df_clean[col].fillna("(空值)")
                        
                        grouped_df = df_clean.groupby(group_cols)[value_cols].agg(agg_func).reset_index()
                        
                        # 格式化数值
                        for col in value_cols:
                            grouped_df[col] = grouped_df[col].round(2)
                        
                        st.session_state.preview_manager.update_stats_preview(
                            grouped_df,
                            f"分组统计: {', '.join(group_cols)}"
                        )
                        st.success("分组统计已生成，请查看主内容区")
                        st.rerun()
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
        
        with col2:
            if chart_type != "请选择图表类型" and st.button("📈 生成分组图表", key="btn_group_chart", use_container_width=True):
                with st.spinner("正在生成图表..."):
                    try:
                        # 【修复】处理空值
                        df_clean = st.session_state.df.copy()
                        for col in group_cols:
                            df_clean[col] = df_clean[col].fillna("(空值)")
                        
                        # 聚合数据
                        agg_df = df_clean.groupby(group_cols[0])[value_cols[0]].agg(agg_func).reset_index()
                        agg_df = agg_df.dropna()
                        
                        if sort_by:
                            agg_df = agg_df.sort_values(value_cols[0], ascending=False)
                        
                        fig = managers['chart_generator'].create_chart(
                            agg_df, 
                            chart_type, 
                            group_cols[0], 
                            value_cols[0]
                        )
                        
                        if fig:
                            st.session_state.preview_manager.update_chart_preview(
                                fig,
                                f"{value_cols[0]}按{group_cols[0]}分组"
                            )
                            st.success("分组图表已生成，请查看主内容区")
                            st.rerun()
                        else:
                            st.error("图表生成失败")
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
        
        with col3:
            st.caption(f"已选择: {len(group_cols)}个分组, {len(value_cols)}个数值")
    else:
        st.info("请依次选择：分组字段 → 数值字段 → 聚合函数")
            
def render_time_series_with_chart():
    """时间序列分析 + 趋势图"""
    st.markdown("#### 时间序列分析")
    
    # 检测日期列
    date_cols = []
    for col in st.session_state.df.columns:
        if pd.api.types.is_datetime64_any_dtype(st.session_state.df[col]):
            date_cols.append(col)
    
    if not date_cols:
        st.warning("没有日期类型的列，请先转换日期格式")
        return
    
    numeric_cols = st.session_state.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    if not numeric_cols:
        st.warning("没有数值列可用于分析")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        date_col = st.selectbox("日期列", date_cols, key="ts_date_chart")
        value_col = st.selectbox("数值列", numeric_cols, key="ts_value_chart")
        
        freq = st.selectbox(
            "重采样频率",
            ["D", "W", "M", "Q", "Y"],
            key="ts_freq_chart",
            format_func=lambda x: {"D": "日", "W": "周", "M": "月", "Q": "季", "Y": "年"}[x]
        )
    
    with col2:
        st.markdown("##### 分析选项")
        show_ma = st.checkbox("移动平均线", value=True, key="ts_ma")
        if show_ma:
            ma_window = st.slider("移动平均窗口", 3, 30, 7, key="ts_ma_window")
        
        show_trend = st.checkbox("趋势线", value=False, key="ts_trend")
        show_seasonal = st.checkbox("季节性分解", value=False, key="ts_seasonal")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 时间序列表", key="btn_ts_table", use_container_width=True):
            with st.spinner("正在分析..."):
                ts_df = managers['stats_analyzer'].time_series_analysis(
                    st.session_state.df, date_col, value_col, freq
                )
                if ts_df is not None:
                    st.session_state.preview_manager.update_stats_preview(
                        ts_df.head(100),
                        f"{value_col}时间序列 ({freq})"
                    )
                    st.success("时间序列表已生成")
                    st.rerun()
    
    with col2:
        if st.button("📈 生成趋势图", key="btn_ts_chart", use_container_width=True):
            with st.spinner("正在生成图表..."):
                # 准备时间序列数据
                ts_data = st.session_state.df[[date_col, value_col]].copy()
                ts_data[date_col] = pd.to_datetime(ts_data[date_col])
                ts_data = ts_data.set_index(date_col).resample(freq).mean().reset_index()
                
                fig = managers['chart_generator'].create_chart(
                    ts_data, "折线图", date_col, value_col
                )
                
                if fig and show_ma:
                    # 计算移动平均
                    ts_data['MA'] = ts_data[value_col].rolling(window=ma_window).mean()
                    fig.add_scatter(x=ts_data[date_col], y=ts_data['MA'], 
                                   mode='lines', name=f'MA{ma_window}')
                
                st.session_state.preview_manager.update_chart_preview(
                    fig, f"{value_col}趋势图"
                )
                st.success("趋势图已生成")
                st.rerun()
    
    with col3:
        st.caption(f"频率: {freq}")
        
def render_pivot_with_chart():
    """数据透视表 + 透视图"""
    st.markdown("#### 数据透视表")
    
    all_cols = st.session_state.df.columns.tolist()
    numeric_cols = st.session_state.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        index_cols = st.multiselect(
            "选择行字段",
            all_cols,
            key="pivot_index_chart",
            placeholder="请选择行字段"
        )
        
        columns_cols = st.multiselect(
            "选择列字段（可选）",
            all_cols,
            key="pivot_columns_chart",
            placeholder="请选择列字段"
        )
        
        values_cols = st.multiselect(
            "选择值字段",
            numeric_cols,
            key="pivot_values_chart",
            placeholder="请选择值字段"
        )
        
        # 聚合函数 - 添加"请选择"选项，没有默认值
        agg_options = ["请选择聚合函数", "mean", "sum", "count", "min", "max", "std"]
        agg_func = st.selectbox(
            "选择聚合函数",
            agg_options,
            key="pivot_agg_chart",
            format_func=lambda x: {
                "请选择聚合函数": "请选择聚合函数",
                "mean": "平均值",
                "sum": "求和",
                "count": "计数",
                "min": "最小值",
                "max": "最大值",
                "std": "标准差"
            }.get(x, x),
            index=0  # 索引0是"请选择聚合函数"
        )
    
    with col2:
        if index_cols and values_cols and agg_func != "请选择聚合函数":
            st.markdown("##### 图表设置")
            chart_options = ["请选择图表类型", "柱状图", "热力图", "饼图", "堆积柱状图"]
            chart_type = st.selectbox(
                "选择图表类型",
                chart_options,
                key="pivot_chart_type",
                index=0
            )
            
            if chart_type != "请选择图表类型":
                if chart_type == "热力图":
                    show_values = st.checkbox("显示数值", value=True, key="pivot_show_values")
                
                stack = st.checkbox("堆积显示", value=False, key="pivot_stack") if chart_type == "柱状图" else False
    
    if index_cols and values_cols and agg_func != "请选择聚合函数":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 生成透视表", key="btn_pivot_table", use_container_width=True):
                with st.spinner("正在生成透视表..."):
                    try:
                        pivot_df = pd.pivot_table(
                            st.session_state.df,
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
                        # 准备数据
                        pivot_data = pd.pivot_table(
                            st.session_state.df,
                            index=index_cols[0],
                            columns=columns_cols[0] if columns_cols else None,
                            values=values_cols[0],
                            aggfunc=agg_func,
                            fill_value=0
                        ).reset_index()
                        
                        # 调试信息
                        st.write(f"透视数据列: {pivot_data.columns.tolist()}")
                        
                        if chart_type == "热力图":
                            fig = managers['chart_generator'].create_chart(
                                pivot_data, 
                                "热力图",
                                show_values=show_values
                            )
                        elif chart_type == "饼图":
                            fig = managers['chart_generator'].create_chart(
                                pivot_data, 
                                "饼图",
                                index_cols[0],
                                values_cols[0]
                            )
                        else:  # 柱状图或堆积柱状图
                            fig = managers['chart_generator'].create_chart(
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
                        else:
                            st.error("图表生成失败")
                    except Exception as e:
                        st.error(f"生成失败: {str(e)}")
                        st.exception(e)
        
        with col3:
            st.caption(f"聚合: {agg_func}")
    else:
        st.info("请依次选择：行字段 → 值字段 → 聚合函数")















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
    st.info("👈 请在左侧边栏上传数据文件开始分析")
    
    with st.expander("✨ 功能介绍", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📁 数据管理
            - **数据上传**：支持CSV/Excel/JSON，自动识别类型
            - **数据预览**：统一预览管理，可调节预览行数
            - **数据清洗**：去重/替换/转换/分列/合并/批量操作
            - **数据筛选**：文本/数值多条件筛选
            - **撤销/重做**：操作历史记录
            
            ### 📊 数据分析
            - **描述性统计**：均值/中位数/标准差/偏度/峰度等
            - **相关性分析**：Pearson/Spearman/Kendall
            - **分组统计**：多级分组聚合
            """)
        
        with col2:
            st.markdown("""
            ### 📈 可视化
            - **基础图表**：柱状图/折线图/散点图/热力图/饼图
            - **复合饼图**：子图布局/交互下钻/复合定位
            - **高级图表**：箱线图/直方图
            - **图表交互**：缩放/平移/悬停/点击联动
            
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
    col1, col2, col3 = st.columns([1, 1, 6])
    with col1:
        if st.button("🔄 刷新", key="refresh_preview", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("📊 数据信息", key="show_info", use_container_width=True):
            with st.expander("数据信息", expanded=True):
                render_data_info()
    with col3:
        st.write("")
    
    # 显示数据基本信息
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
    
    # 显示列信息
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
                fig = managers['chart_generator'].create_chart(
                    st.session_state.df, "饼图", cat_col, val_col
                )
                if fig:
                    st.session_state.preview_manager.update_chart_preview(fig, "饼图")
                    st.rerun()
    elif numeric_cols:
        x_col = st.selectbox("X轴", numeric_cols, key="quick_chart_x")
        y_col = st.selectbox("Y轴", numeric_cols, key="quick_chart_y", index=min(1, len(numeric_cols)-1)) if len(numeric_cols) > 1 else None
        if st.button("生成", key="quick_gen_chart"):
            fig = managers['chart_generator'].create_chart(
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
        st.warning("请先上传数据")
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
        if st.button("🌙 深色模式", use_container_width=True):
            if st.session_state.theme_mode != 'dark':
                ThemeManager.toggle_theme()
                st.rerun()
    with col2:
        if st.button("☀️ 浅色模式", use_container_width=True):
            if st.session_state.theme_mode != 'light':
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
    print("="*50)
    print("【调试】程序启动/刷新")
    print(f"【调试】当前时间: {datetime.now().strftime('%H:%M:%S')}")
    print(f"【调试】当前页面: {st.session_state.get('current_page', '未设置')}")
    print(f"【调试】预览模式: {st.session_state.get('preview_mode', '未设置')}")
    
    # 显示顶部公告
    managers['announcement'].show_announcements()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 渲染右侧功能面板
    render_right_panel()
    
    # 渲染主内容区
    render_main_content()
    st.divider()
    st.caption(f"当前页面: {st.session_state.get('current_page', '未知')}")
    
    # 显示底部信息
    managers['footer'].show_footer()
    
    print("【调试】主程序执行完毕")
    print("="*50)

# ============================================
# 程序启动
# ============================================
if __name__ == "__main__":
    main()