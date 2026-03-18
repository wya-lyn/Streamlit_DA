"""
数据洞察助手 - 主入口文件
功能：集成所有模块，实现完整的数据分析工具
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 导入自定义模块
from utils.theme_manager import ThemeManager
from utils.file_loader import FileLoader
from utils.data_cleaner import DataCleaner
from utils.data_filter import DataFilter
from utils.stats_analyzer import StatsAnalyzer
from utils.chart_generator import ChartGenerator
from utils.ai_analyzer import AIAnalyzer
from components.layout import LayoutManager
from components.announcements import AnnouncementManager
from components.footer import FooterManager
from components.history_manager import HistoryManager

# 页面配置
st.set_page_config(
    page_title="数据洞察助手",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化主题
ThemeManager.init_theme()

# 初始化各个管理器
@st.cache_resource
def init_managers():
    """初始化所有管理器（单例）"""
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

managers = init_managers()

# 应用自定义CSS
ThemeManager.apply_custom_css()

# 初始化session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = -1

# 新增：为统一的预览功能初始化状态变量
if 'preview_mode' not in st.session_state:
    st.session_state.preview_mode = None  # 当前预览模式，如 'dedup', 'replace', 等
if 'preview_params' not in st.session_state:
    st.session_state.preview_params = {}  # 存储预览操作时的参数
if 'preview_result' not in st.session_state:
    st.session_state.preview_result = None  # 存储预览生成的数据框

# ============================================
# 顶部公告区域
# ============================================
managers['announcement'].show_announcements()

# ============================================
# 主布局
# ============================================
with st.sidebar:
    st.title("📊 数据洞察助手")
    
    # 主题切换
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 主题设置")
    with col2:
        current_theme = st.session_state.theme_mode
        theme_icon = "🌙" if current_theme == "dark" else "☀️"
        if st.button(theme_icon, key="theme_toggle"):
            ThemeManager.toggle_theme()
            st.rerun()
    
    st.divider()
    
    # 左侧主菜单
    menu_items = ["🏠 首页", "📁 数据管理", "📊 数据分析", "📈 可视化", "🤖 AI分析", "⚙️ 设置"]
    selected_main_menu = st.radio(
        "主菜单",
        menu_items,
        label_visibility="collapsed",
        key="main_menu"
    )
    
    st.divider()
    
    # 文件上传（始终显示）
    st.markdown("### 📤 数据上传")
    uploaded_file = st.file_uploader(
        "选择文件",
        type=['csv', 'xlsx', 'json'],
        help="支持CSV、Excel、JSON格式，最大20MB"
    )
    
    if uploaded_file:
        with st.spinner("正在加载数据..."):
            df = managers['file_loader'].load_file(uploaded_file)
            if df is not None:
                st.session_state.df = df
                st.session_state.original_df = df.copy()
                managers['history'].add_to_history("上传文件", df)
                st.success(f"✅ 加载成功！{len(df)}行 × {len(df.columns)}列")
                
                # 显示前10行预览
                with st.expander("数据预览（前10行）"):
                    st.dataframe(df.head(10), use_container_width=True)

# ============================================
# 右侧功能面板（可折叠）
# ============================================
with st.container():
    # 右侧功能面板开关
    show_right_panel = st.checkbox("📋 显示功能面板", value=True)
    
    if show_right_panel:
        right_tabs = st.tabs(["🧹 数据处理", "🔍 数据筛选", "📊 分析选项", "🤖 AI配置"])
        
        # Tab 1: 数据处理
        # Tab 1: 数据处理
        with right_tabs[0]:
            st.markdown("### 数据清洗")
            
            # ===== 去重功能 =====
            with st.expander("🗑️ 去重", expanded=False):
                if st.session_state.df is not None:
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
                    
                    # 预览按钮
                    if st.button("👁️ 预览去重效果", key="preview_dedup"):
                        preview_df = managers['data_cleaner'].deduplicate(
                            st.session_state.df.head(20),  # 只预览前20行
                            subset=subset_cols if subset_cols else None,
                            keep=keep_map[keep_option]
                        )
                        st.write("预览结果（前20行）：")
                        st.dataframe(preview_df, use_container_width=True)
                        st.info(f"预览数据从 {min(20, len(st.session_state.df))} 行变为 {len(preview_df)} 行")
                    
                    # 执行按钮
                    if st.button("✅ 执行去重", key="btn_dedup"):
                        before = len(st.session_state.df)
                        st.session_state.df = managers['data_cleaner'].deduplicate(
                            st.session_state.df, 
                            subset=subset_cols if subset_cols else None,
                            keep=keep_map[keep_option]
                        )
                        after = len(st.session_state.df)
                        managers['history'].add_to_history("去重", st.session_state.df)
                        st.success(f"去重完成，从 {before} 行减少到 {after} 行")
                        st.rerun()
                else:
                    st.info("请先上传数据")
            
            # ===== 替换值功能 =====
            with st.expander("🔄 替换值", expanded=False):
                if st.session_state.df is not None:
                    replace_col = st.selectbox(
                        "选择列", 
                        st.session_state.df.columns, 
                        key="replace_col"
                    )
                    replace_mode = st.radio(
                        "替换方式", 
                        ["文本替换", "正则替换", "空值替换"], 
                        key="replace_mode"
                    )
                    
                    if replace_mode == "文本替换":
                        old = st.text_input("查找内容", key="replace_old")
                        new = st.text_input("替换为", key="replace_new")
                        
                        # 预览
                        if st.button("👁️ 预览文本替换", key="preview_replace"):
                            preview_df = st.session_state.df.head(10).copy()
                            preview_df = managers['data_cleaner'].text_replace(
                                preview_df, replace_col, old, new
                            )
                            st.write("预览结果（前10行）：")
                            comparison = pd.DataFrame({
                                '原值': st.session_state.df[replace_col].head(10),
                                '新值': preview_df[replace_col]
                            })
                            st.dataframe(comparison, use_container_width=True)
                        
                        # 执行
                        if st.button("✅ 执行文本替换", key="btn_replace"):
                            st.session_state.df = managers['data_cleaner'].text_replace(
                                st.session_state.df, replace_col, old, new
                            )
                            managers['history'].add_to_history("文本替换", st.session_state.df)
                            st.success("替换完成")
                            st.rerun()
                    
                    elif replace_mode == "正则替换":
                        pattern = st.text_input("正则表达式", key="replace_pattern")
                        replacement = st.text_input("替换为", key="replace_replacement")
                        
                        if st.button("👁️ 预览正则替换", key="preview_regex"):
                            preview_df = st.session_state.df.head(10).copy()
                            preview_df = managers['data_cleaner'].text_replace(
                                preview_df, replace_col, pattern, replacement, regex=True
                            )
                            st.write("预览结果（前10行）：")
                            comparison = pd.DataFrame({
                                '原值': st.session_state.df[replace_col].head(10),
                                '新值': preview_df[replace_col]
                            })
                            st.dataframe(comparison, use_container_width=True)
                        
                        if st.button("✅ 执行正则替换", key="btn_regex_replace"):
                            st.session_state.df = managers['data_cleaner'].text_replace(
                                st.session_state.df, replace_col, pattern, replacement, regex=True
                            )
                            managers['history'].add_to_history("正则替换", st.session_state.df)
                            st.success("正则替换完成")
                            st.rerun()
                    
                    else:  # 空值替换
                        fill_value = st.text_input("填充值", "", key="replace_fill")
                        
                        if st.button("👁️ 预览空值替换", key="preview_null"):
                            preview_df = st.session_state.df.head(10).copy()
                            preview_df = managers['data_cleaner'].null_replace(
                                preview_df, replace_col, fill_value
                            )
                            st.write("预览结果（前10行）：")
                            null_rows = st.session_state.df[replace_col].head(10).isna() | (st.session_state.df[replace_col].head(10) == "null")
                            comparison = pd.DataFrame({
                                '原值': st.session_state.df[replace_col].head(10),
                                '是否空值': null_rows,
                                '新值': preview_df[replace_col]
                            })
                            st.dataframe(comparison, use_container_width=True)
                        
                        if st.button("✅ 执行空值替换", key="btn_null_replace"):
                            st.session_state.df = managers['data_cleaner'].null_replace(
                                st.session_state.df, replace_col, fill_value
                            )
                            managers['history'].add_to_history("空值替换", st.session_state.df)
                            st.success("空值替换完成")
                            st.rerun()
                else:
                    st.info("请先上传数据")
            
            # ===== 类型转换功能 =====
            with st.expander("📝 类型转换", expanded=False):
                if st.session_state.df is not None:
                    convert_col = st.selectbox(
                        "选择列", 
                        st.session_state.df.columns, 
                        key="convert_col"
                    )
                    convert_type = st.radio(
                        "转换类型", 
                        ["转换为文本", "转换为数值"], 
                        key="convert_type"
                    )
                    
                    # 预览
                    if st.button("👁️ 预览类型转换", key="preview_convert"):
                        preview_df = st.session_state.df.head(10).copy()
                        preview_df = managers['data_cleaner'].convert_type(
                            preview_df, convert_col, convert_type
                        )
                        st.write("预览结果（前10行）：")
                        comparison = pd.DataFrame({
                            '原值': st.session_state.df[convert_col].head(10),
                            '原类型': st.session_state.df[convert_col].head(10).apply(lambda x: type(x).__name__),
                            '新值': preview_df[convert_col],
                            '新类型': preview_df[convert_col].apply(lambda x: type(x).__name__)
                        })
                        st.dataframe(comparison, use_container_width=True)
                    
                    # 执行
                    if st.button("✅ 执行转换", key="btn_convert"):
                        st.session_state.df = managers['data_cleaner'].convert_type(
                            st.session_state.df, convert_col, convert_type
                        )
                        managers['history'].add_to_history("类型转换", st.session_state.df)
                        st.success("类型转换完成")
                        st.rerun()
                else:
                    st.info("请先上传数据")
            
            # ===== 分列功能 =====
            with st.expander("✂️ 分列", expanded=False):
                if st.session_state.df is not None:
                    split_col = st.selectbox(
                        "选择列", 
                        st.session_state.df.columns, 
                        key="split_col"
                    )
                    split_mode = st.radio(
                        "分列方式", 
                        ["最左分隔符", "最右分隔符"], 
                        key="split_mode"
                    )
                    separator = st.text_input("分隔符", ",", key="split_sep")
                    
                    # 预览
                    if st.button("👁️ 预览分列", key="preview_split"):
                        preview_df = st.session_state.df.head(5).copy()
                        preview_df = managers['data_cleaner'].split_column(
                            preview_df, split_col, separator, split_mode
                        )
                        st.write("预览结果（前5行）：")
                        st.dataframe(preview_df, use_container_width=True)
                        # 显示新增的列
                        new_cols = [col for col in preview_df.columns if col not in st.session_state.df.columns]
                        if new_cols:
                            st.info(f"新增列: {', '.join(new_cols)}")
                    
                    # 执行
                    if st.button("✅ 执行分列", key="btn_split"):
                        st.session_state.df = managers['data_cleaner'].split_column(
                            st.session_state.df, split_col, separator, split_mode
                        )
                        managers['history'].add_to_history("分列", st.session_state.df)
                        st.success("分列完成")
                        st.rerun()
                else:
                    st.info("请先上传数据")
            
            st.divider()
            
            # ===== 批量操作 =====
            st.markdown("### 批量操作")
            if st.session_state.df is not None:
                batch_cols = st.multiselect("选择要删除的列", st.session_state.df.columns)
                
                if batch_cols:
                    # 预览
                    if st.button("👁️ 预览删除列", key="preview_delete"):
                        preview_df = st.session_state.df.drop(columns=batch_cols).head(10)
                        st.write(f"预览删除 {batch_cols} 后的结果（前10行）：")
                        st.dataframe(preview_df, use_container_width=True)
                    
                    # 执行
                    if st.button("✅ 批量删除列", key="btn_batch_delete"):
                        before_cols = len(st.session_state.df.columns)
                        st.session_state.df = managers['data_cleaner'].delete_columns(
                            st.session_state.df, batch_cols
                        )
                        after_cols = len(st.session_state.df.columns)
                        managers['history'].add_to_history("批量删除", st.session_state.df)
                        st.success(f"已删除 {before_cols - after_cols} 列")
                        st.rerun()
            else:
                st.info("请先上传数据")
            
            # ===== 撤销/重做 =====
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("↩️ 撤销", use_container_width=True, key="btn_undo"):
                    if st.session_state.df is not None:
                        # 调用 undo 时传入当前 df
                        st.session_state.df = managers['history'].undo(st.session_state.df)
                        st.rerun()
                    else:
                        st.warning("没有数据可撤销")
            with col2:
                if st.button("↪️ 重做", use_container_width=True, key="btn_redo"):
                    if st.session_state.df is not None:
                        # 调用 redo 时传入当前 df
                        st.session_state.df = managers['history'].redo(st.session_state.df)
                        st.rerun()
                    else:
                        st.warning("没有数据可重做")
            with col3:
                if st.button("📋 历史", use_container_width=True, key="btn_history"):
                    managers['history'].show_history()
                
            # Tab 2: 数据筛选
            with right_tabs[1]:
                if st.session_state.df is not None:
                    st.markdown("### 文本筛选")
                    text_col = st.selectbox("选择文本列", st.session_state.df.select_dtypes(include=['object']).columns)
                    text_condition = st.selectbox("条件", ["包含", "等于", "开头为", "结尾为"])
                    text_value = st.text_input("筛选值")
                    if st.button("应用文本筛选"):
                        st.session_state.df = managers['data_filter'].text_filter(
                            st.session_state.df, text_col, text_condition, text_value
                        )
                        st.rerun()
                    
                    st.divider()
                    
                    st.markdown("### 数值筛选")
                    num_cols = st.session_state.df.select_dtypes(include=['int64', 'float64']).columns
                    if len(num_cols) > 0:
                        num_col = st.selectbox("选择数值列", num_cols)
                        num_condition = st.selectbox("条件", ["大于", "小于", "等于", "介于"])
                        if num_condition == "介于":
                            min_val = st.number_input("最小值")
                            max_val = st.number_input("最大值")
                            if st.button("应用数值筛选"):
                                st.session_state.df = managers['data_filter'].numeric_filter(
                                    st.session_state.df, num_col, num_condition, (min_val, max_val)
                                )
                                st.rerun()
                        else:
                            num_value = st.number_input("筛选值")
                            if st.button("应用数值筛选"):
                                st.session_state.df = managers['data_filter'].numeric_filter(
                                    st.session_state.df, num_col, num_condition, num_value
                                )
                                st.rerun()
            
            # Tab 3: 分析选项
            with right_tabs[2]:
                if st.session_state.df is not None:
                    st.markdown("### 统计选项")
                    if st.button("📊 描述性统计"):
                        stats = managers['stats_analyzer'].descriptive_stats(st.session_state.df)
                        st.dataframe(stats)
                    
                    if st.button("📈 相关性分析"):
                        corr = managers['stats_analyzer'].correlation_analysis(st.session_state.df)
                        st.dataframe(corr)
                    
                    st.divider()
                    
                    st.markdown("### 图表选项")
                    chart_type = st.selectbox(
                        "选择图表类型",
                        ["柱状图", "折线图", "散点图", "热力图", "饼图", "复合饼图"]
                    )
                    
                    if chart_type == "复合饼图":
                        pie_mode = st.selectbox(
                            "复合饼图模式",
                            ["子图布局", "交互下钻", "复合定位"]
                        )
                        st.info(f"已选择: {pie_mode}模式")
            
            # Tab 4: AI配置
            with right_tabs[3]:
                st.markdown("### 🤖 AI分析设置")
                
                # AI开关
                enable_ai = st.toggle("启用AI分析", value=False)
                if enable_ai:
                    st.info("需要OpenAI API密钥才能使用")
                    api_key = st.text_input("API密钥", type="password")
                    if api_key:
                        st.success("API密钥已设置")
                        
                        st.divider()
                        st.markdown("### 分析提示词")
                        prompt = st.text_area(
                            "输入分析需求",
                            placeholder="例如：分析销售数据趋势，找出异常点，给出建议",
                            height=100
                        )
                        
                        if st.button("🚀 生成AI分析", type="primary"):
                            with st.spinner("AI正在分析..."):
                                # 这里预留AI接口
                                st.info("AI功能预留，等待API密钥配置")
                    else:
                        st.warning("请输入API密钥")

# ============================================
# 主内容区
# ============================================

if st.session_state.df is not None:
    df = st.session_state.df
    # 主功能区标题
    st.markdown("## 📊 主内容区")
    
    # 显示当前数据
    st.dataframe(df, use_container_width=True)
    
    # 使用标签页代替嵌套的expander
    tab1, tab2, tab3 = st.tabs(["🛠️ 数据操作", "👁️ 数据预览", "📊 数据统计"])
    
    with tab1:
        # 操作类型选择（不使用expander）
        operation = st.radio(
            "选择操作类型：",
            ["去重", "替换值", "类型转换", "分列", "删除列", "修改表头"],
            horizontal=True,
            key="main_operation"
        )
        
        # 根据选择显示对应的操作界面
        if operation == "去重":
            st.markdown("##### 去重设置")
            cols = st.multiselect("选择去重依据的列（留空则基于所有列）", df.columns.tolist())
            keep = st.radio("保留方式：", ["first", "last", "False"], horizontal=True, 
                           format_func=lambda x: "保留第一个" if x == "first" else "保留最后一个" if x == "last" else "删除所有重复")
            
            if st.button("执行去重", type="primary", key="apply_dedup"):
                try:
                    original_len = len(df)
                    # 执行去重
                    subset = cols if cols else None
                    st.session_state.df = managers['data_cleaner'].deduplicate(
                        df, subset=subset, keep=keep if keep != "False" else False
                    )
                    new_len = len(st.session_state.df)
                    managers['history'].add_to_history('去重', st.session_state.df)
                    st.success(f"去重完成！从 {original_len} 行变为 {new_len} 行")
                    st.rerun()
                except Exception as e:
                    st.error(f"去重失败：{str(e)}")
        
        elif operation == "替换值":
            st.markdown("##### 替换设置")
            col = st.selectbox("选择要替换的列", df.columns.tolist(), key="replace_col")
            replace_mode = st.radio("替换模式：", ["文本替换", "正则替换", "空值填充"], horizontal=True)
            
            if replace_mode == "文本替换":
                old_val = st.text_input("查找内容")
                new_val = st.text_input("替换为")
                if st.button("执行替换", type="primary", key="apply_text_replace"):
                    try:
                        st.session_state.df = managers['data_cleaner'].text_replace(
                            df, col, old_val, new_val
                        )
                        managers['history'].add_to_history('替换值', st.session_state.df)
                        st.success("文本替换完成！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"替换失败：{str(e)}")
            
            elif replace_mode == "正则替换":
                pattern = st.text_input("正则表达式模式")
                replacement = st.text_input("替换为")
                if st.button("执行正则替换", type="primary", key="apply_regex_replace"):
                    try:
                        st.session_state.df = managers['data_cleaner'].text_replace(
                            df, col, pattern, replacement, regex=True
                        )
                        managers['history'].add_to_history('替换值', st.session_state.df)
                        st.success("正则替换完成！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"替换失败：{str(e)}")
            
            else:  # 空值填充
                fill_value = st.text_input("填充值")
                if st.button("执行空值填充", type="primary", key="apply_null_fill"):
                    try:
                        st.session_state.df = managers['data_cleaner'].null_replace(
                            df, col, fill_value
                        )
                        managers['history'].add_to_history('替换值', st.session_state.df)
                        st.success("空值填充完成！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"填充失败：{str(e)}")
        
        elif operation == "类型转换":
            st.markdown("##### 类型转换设置")
            col = st.selectbox("选择要转换的列", df.columns.tolist(), key="convert_col")
            target_type = st.selectbox("转换为类型", ["int", "float", "str", "datetime", "category"])
            
            if st.button("执行转换", type="primary", key="apply_convert"):
                try:
                    st.session_state.df = managers['data_cleaner'].convert_type(
                        df, col, target_type
                    )
                    managers['history'].add_to_history('类型转换', st.session_state.df)
                    st.success(f"列 '{col}' 已转换为 {target_type} 类型")
                    st.rerun()
                except Exception as e:
                    st.error(f"转换失败：{str(e)}")
        
        elif operation == "分列":
            st.markdown("##### 分列设置")
            col = st.selectbox("选择要分列的列", df.columns.tolist(), key="split_col")
            sep = st.text_input("分隔符", value=",")
            mode = st.radio("分列模式：", ["expand", "list"], horizontal=True,
                          format_func=lambda x: "扩展为多列" if x == "expand" else "保持为列表")
            
            if st.button("执行分列", type="primary", key="apply_split"):
                try:
                    original_cols = df.columns.tolist()
                    st.session_state.df = managers['data_cleaner'].split_column(
                        df, col, sep, mode
                    )
                    new_cols = [c for c in st.session_state.df.columns if c not in original_cols]
                    managers['history'].add_to_history('分列', st.session_state.df)
                    if new_cols:
                        st.success(f"分列完成！新增列：{', '.join(new_cols)}")
                    else:
                        st.success("分列完成！")
                    st.rerun()
                except Exception as e:
                    st.error(f"分列失败：{str(e)}")
        
        elif operation == "删除列":
            st.markdown("##### 删除列设置")
            cols_to_drop = st.multiselect("选择要删除的列", df.columns.tolist())
            
            if st.button("执行删除", type="primary", key="apply_drop"):
                try:
                    if cols_to_drop:
                        st.session_state.df = df.drop(columns=cols_to_drop)
                        managers['history'].add_to_history('删除列', st.session_state.df)
                        st.success(f"已删除列：{', '.join(cols_to_drop)}")
                        st.rerun()
                    else:
                        st.warning("请至少选择一列")
                except Exception as e:
                    st.error(f"删除失败：{str(e)}")
        
        elif operation == "修改表头":
            st.markdown("##### 修改表头设置")
            # 显示当前列名
            st.write("当前列名：")
            col_df = pd.DataFrame({
                '序号': range(len(df.columns)),
                '当前列名': df.columns.tolist()
            })
            st.dataframe(col_df, use_container_width=True)
            
            # 修改方式选择
            modify_mode = st.radio(
                "选择修改方式：",
                ["批量添加前缀/后缀", "批量替换文本", "自定义修改"],
                horizontal=True
            )
            
            if modify_mode == "批量添加前缀/后缀":
                prefix = st.text_input("添加前缀（留空则不添加）")
                suffix = st.text_input("添加后缀（留空则不添加）")
                if st.button("执行修改", type="primary", key="apply_prefix_suffix"):
                    try:
                        new_columns = df.columns.tolist()
                        if prefix:
                            new_columns = [prefix + str(col) for col in new_columns]
                        if suffix:
                            new_columns = [str(col) + suffix for col in new_columns]
                        st.session_state.df.columns = new_columns
                        managers['history'].add_to_history('修改表头', st.session_state.df)
                        st.success("表头修改完成！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"修改失败：{str(e)}")
            
            elif modify_mode == "批量替换文本":
                old_text = st.text_input("查找内容")
                new_text = st.text_input("替换为")
                if st.button("执行替换", type="primary", key="apply_header_replace"):
                    try:
                        new_columns = [str(col).replace(old_text, new_text) for col in df.columns]
                        st.session_state.df.columns = new_columns
                        managers['history'].add_to_history('修改表头', st.session_state.df)
                        st.success("表头替换完成！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"替换失败：{str(e)}")
            
            else:  # 自定义修改
                st.write("自定义修改（双击单元格编辑）：")
                edited_cols = st.data_editor(
                    pd.DataFrame({
                        '原列名': df.columns.tolist(),
                        '新列名': df.columns.tolist()
                    }),
                    use_container_width=True,
                    num_rows="fixed",
                    key="header_editor"
                )
                if st.button("应用修改", type="primary", key="apply_custom_header"):
                    try:
                        new_columns = edited_cols['新列名'].tolist()
                        if len(set(new_columns)) != len(new_columns):
                            st.error("新列名不能重复！")
                        else:
                            st.session_state.df.columns = new_columns
                            managers['history'].add_to_history('修改表头', st.session_state.df)
                            st.success("表头修改完成！")
                            st.rerun()
                    except Exception as e:
                        st.error(f"修改失败：{str(e)}")
    
    with tab2:
        st.markdown("##### 数据预览设置")
        preview_rows = st.slider("预览行数", min_value=5, max_value=100, value=20, step=5, key="preview_rows")
        
        if st.button("生成预览", key="generate_preview"):
            preview_df = df.head(preview_rows)
            st.dataframe(preview_df, use_container_width=True)
            st.caption(f"显示前 {preview_rows} 行数据")
    
    with tab3:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总行数", len(df))
        with col2:
            st.metric("总列数", len(df.columns))
        with col3:
            st.metric("缺失值", df.isna().sum().sum())
        with col4:
            st.metric("数据类型", df.dtypes.nunique())
        
        # 显示列信息
        st.markdown("##### 列信息")
        col_info = pd.DataFrame({
            '列名': df.columns,
            '数据类型': df.dtypes.values,
            '非空值数': df.count().values,
            '缺失值数': df.isna().sum().values,
            '唯一值数': [df[col].nunique() for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True)
        
        # 修改表头
        with st.expander("修改表头"):
            for col in df.columns:
                new_name = st.text_input(f"修改 {col}", col)
                if new_name != col:
                    st.session_state.df.rename(columns={col: new_name}, inplace=True)
                    st.rerun()
    
elif "数据分析" in selected_main_menu:
    st.markdown("### 统计分析")
    
    # 描述统计
    st.subheader("描述性统计")
    stats_df = managers['stats_analyzer'].descriptive_stats(df)
    st.dataframe(stats_df, use_container_width=True)
    
    # 分组统计
    st.subheader("分组统计")
    group_cols = st.multiselect("分组字段", df.select_dtypes(include=['object']).columns)
    value_cols = st.multiselect("数值字段", df.select_dtypes(include=['int64', 'float64']).columns)
    if group_cols and value_cols:
        grouped = managers['stats_analyzer'].group_stats(df, group_cols, value_cols)
        st.dataframe(grouped)

elif "可视化" in selected_main_menu:
    st.markdown("### 可视化分析")
    
    chart_type = st.selectbox(
        "图表类型",
        ["柱状图", "折线图", "散点图", "热力图", "饼图", "复合饼图"],
        key="main_chart_type"
    )
    
    if chart_type == "复合饼图":
        pie_mode = st.selectbox(
            "复合饼图模式",
            ["子图布局", "交互下钻", "复合定位"],
            key="main_pie_mode"
        )
        st.info(f"复合饼图 - {pie_mode}模式 (开发中)")
    else:
        # 简单图表
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            x_col = st.selectbox("X轴", numeric_cols)
            y_col = st.selectbox("Y轴", numeric_cols, index=min(1, len(numeric_cols)-1)) if len(numeric_cols) > 1 else None
            
            if st.button("生成图表"):
                fig = managers['chart_generator'].create_chart(df, chart_type, x_col, y_col)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

elif "AI分析" in selected_main_menu:
    st.markdown("### AI智能分析")
    st.info("请在右侧面板启用AI分析并配置API密钥")

elif "设置" in selected_main_menu:
    st.markdown("### 系统设置")
    st.info("开发中...")
    
else:
    st.info("👈 请在左侧边栏上传数据文件开始分析")
    # 功能介绍
    st.markdown("""
    ### ✨ 功能介绍
    
    - **数据上传**: 支持CSV/Excel/JSON，自动识别类型
    - **数据处理**: 去重/替换/转换/分列/合并/批量操作
    - **数据筛选**: 文本/数值/日期多条件筛选
    - **统计分析**: 描述统计/分组统计/相关性/时间序列
    - **可视化**: 7种图表 + 复合饼图3种模式
    - **AI分析**: 可开关，支持自定义提示词
    - **主题切换**: 深色/浅色一键切换
    - **本地存储**: 最近7天操作记录
    """)

# ============================================
# 底部信息
# ============================================
managers['footer'].show_footer()