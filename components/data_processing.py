"""
数据处理模块：包含数据处理标签页的所有功能
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from utils.data_cleaner import DataCleaner
from utils.logger import Logger
from utils.data_filter import DataFilter
from utils.data_templates import PROCESSING_TEMPLATES  # 添加这行


# ============================================
# 一键处理面板
# ============================================

def _execute_step(step):
    """执行单个处理步骤"""
    import re
    import pandas as pd
    from utils.data_filter import DataFilter
    
    step_type = step["type"]
    params = step.get("params", {})
    
    # ========== 提升为标题 ==========
    if step_type == "提升为标题":
        row_number = params.get("row_number", 1)
        _promote_to_header(row_number)
    
    # ========== 类型转换 ==========
    elif step_type == "类型转换":
        column = params.get("column")
        columns = params.get("columns", [])
        target_type = params.get("target_type")
        
        def clean_and_convert(val):
            """清理并转换为目标类型"""
            if target_type == "数值":
                if isinstance(val, str):
                    # 移除千分位逗号
                    val = val.replace(',', '')
                    # 移除不可见字符
                    val = re.sub(r'[\x00-\x1f\x7f\u200b\u200c\u200d\u2060\uFEFF]', '', val)
                    val = val.strip()
                    # 处理负数括号格式 (123.45) -> -123.45
                    if val.startswith('(') and val.endswith(')'):
                        val = '-' + val[1:-1]
                try:
                    return pd.to_numeric(val, errors='coerce')
                except:
                    return None
            elif target_type == "文本":
                if hasattr(val, 'astype'):
                    return val.astype(str)
                return str(val)
            elif target_type == "日期时间":
                try:
                    return pd.to_datetime(val, errors='coerce')
                except:
                    return None
            elif target_type == "百分比":
                if isinstance(val, str):
                    val = val.replace('%', '').strip()
                    try:
                        return float(val) / 100
                    except:
                        return None
                return val
            else:
                return val
        
        # 处理单列
        if column and column in st.session_state.df.columns:
            st.session_state.df[column] = st.session_state.df[column].apply(clean_and_convert)
        
        # 处理多列
        if columns:
            for col in columns:
                if col in st.session_state.df.columns:
                    st.session_state.df[col] = st.session_state.df[col].apply(clean_and_convert)
        
        st.session_state.preview_manager.record_operation(f"类型转换-{target_type}")
    
    # ========== 自动检测类型 ==========
    elif step_type == "自动检测类型":
        columns = params.get("columns", [])
        if not columns:
            columns = st.session_state.df.columns.tolist()
        
        for col in columns:
            if col not in st.session_state.df.columns:
                continue
            
            # 先尝试转换为数值
            try:
                converted = pd.to_numeric(st.session_state.df[col], errors='coerce')
                if converted.notna().sum() > 0:
                    st.session_state.df[col] = converted
                    continue
            except:
                pass
            
            # 再尝试转换为日期时间
            try:
                converted = pd.to_datetime(st.session_state.df[col], errors='coerce')
                if converted.notna().sum() > 0:
                    st.session_state.df[col] = converted
                    continue
            except:
                pass
            
            # 最后转为文本
            st.session_state.df[col] = st.session_state.df[col].astype(str)
        
        st.session_state.preview_manager.record_operation("自动检测类型")
    
    # ========== 去重 ==========
    elif step_type == "去重":
        subset = params.get("subset", [])
        keep = params.get("keep", "first")
        execute_data_operation(st.session_state.df, st.session_state.df, "去重", subset=subset, keep=keep)
    
    # ========== 删除空列 ==========
    elif step_type == "删除空列":
        execute_data_operation(st.session_state.df, st.session_state.df, "删除空列", [])
    
    # ========== 删除列 ==========
    elif step_type == "删除列":
        columns = params.get("columns", [])
        if columns:
            execute_data_operation(st.session_state.df, st.session_state.df, "删除列", columns)
    
    # ========== 替换 ==========
    elif step_type == "替换":
        column = params.get("column")
        old = params.get("old")
        new = params.get("new")
        mode = params.get("mode", "文本替换")
        if column:
            if mode == "文本替换":
                execute_data_operation(st.session_state.df, st.session_state.df, "文本替换", column, old, new)
            elif mode == "空值替换":
                execute_data_operation(st.session_state.df, st.session_state.df, "空值替换", column, new)
    
    # ========== 分列 ==========
    elif step_type == "分列":
        column = params.get("column")
        separator = params.get("separator")
        mode = params.get("mode", "最左分隔符")
        if column and separator:
            execute_data_operation(st.session_state.df, st.session_state.df, "分列", column, separator, mode)
    
    # ========== 修改表头 ==========
    elif step_type == "修改表头":
        old_name = params.get("old_name")
        new_name = params.get("new_name")
        if old_name and new_name and old_name in st.session_state.df.columns:
            st.session_state.df = st.session_state.df.rename(columns={old_name: new_name})
    
    # ========== 筛选 ==========
    elif step_type == "筛选":
        column = params.get("column")
        condition = params.get("condition")
        value = params.get("value")
        if column and column in st.session_state.df.columns:
            if condition == "不等于":
                st.session_state.df = st.session_state.df[st.session_state.df[column] != value]
            elif condition == "不为空":
                st.session_state.df = st.session_state.df[st.session_state.df[column].notna()]
            elif condition == "为空":
                st.session_state.df = st.session_state.df[st.session_state.df[column].isna()]
            else:
                filter_obj = DataFilter()
                st.session_state.df = filter_obj.text_filter(st.session_state.df, column, condition, str(value))
    
    # ========== 清理字符 ==========
    elif step_type == "清理字符":
        column = params.get("column")
        columns = params.get("columns", [])
        
        def clean_text(text):
            """清理不可见字符"""
            if isinstance(text, str):
                text = re.sub(r'[\x00-\x1f\x7f]', '', text)
                text = re.sub(r'[\u200b\u200c\u200d\u2060\uFEFF]', '', text)
                text = text.strip()
            return text
        
        if column and column in st.session_state.df.columns:
            st.session_state.df[column] = st.session_state.df[column].apply(clean_text)
        
        if columns:
            for col in columns:
                if col in st.session_state.df.columns:
                    st.session_state.df[col] = st.session_state.df[col].apply(clean_text)
        
        st.session_state.preview_manager.record_operation("清理字符")


def _promote_to_header(row_number):
    """将指定行提升为标题"""
    try:
        df = st.session_state.df
        if row_number <= 0 or row_number > len(df):
            st.warning(f"行号 {row_number} 超出范围")
            return
        
        new_columns = df.iloc[row_number - 1].tolist()
        
        final_columns = []
        seen = {}
        for col in new_columns:
            col_str = str(col) if col is not None else ""
            if col_str == "" or col_str == "nan":
                col_str = "列"
            if col_str in seen:
                seen[col_str] += 1
                col_str = f"{col_str}_{seen[col_str]}"
            else:
                seen[col_str] = 1
            final_columns.append(col_str)
        
        new_df = df.iloc[row_number:].reset_index(drop=True)
        new_df.columns = final_columns
        
        st.session_state.df = new_df
        st.session_state.preview_manager.record_operation(f"提升第{row_number}行为标题")
        
    except Exception as e:
        st.error(f"提升标题失败: {str(e)}")


def render_quick_process():
    """一键处理面板（7个单选按钮）"""
    st.markdown("### ⚡ 一键处理模板")
    st.caption("选择数据处理模板，一键执行预设操作")
    
    template_ids = ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]
    
    # 显示7个模板按钮（每行4个）
    cols = st.columns(4)
    selected_template = None
    
    for i, tid in enumerate(template_ids):
        template = PROCESSING_TEMPLATES.get(tid, {})
        name = template.get("name", f"模板{tid}")
        col_idx = i % 4
        with cols[col_idx]:
            if st.button(f"📋 {name}", key=f"template_btn_{tid}", use_container_width=True):
                selected_template = tid
                st.session_state.selected_template = tid
    
    # 如果有选中的模板，显示详情和执行按钮
    current_tid = selected_template or st.session_state.get('selected_template')
    if current_tid:
        template = PROCESSING_TEMPLATES.get(current_tid, {})
        if template:
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{template['name']}**")
                st.caption(template['description'])
            
            with col2:
                if st.button("🔍 查看步骤", key=f"show_steps_{current_tid}", use_container_width=True):
                    with st.expander(f"{template['name']} 处理步骤", expanded=True):
                        for i, step in enumerate(template['steps'], 1):
                            st.write(f"{i}. {step['type']}: {step.get('params', {})}")
            
            with col3:
                if st.button("🚀 执行模板", key=f"execute_{current_tid}", use_container_width=True, type="primary"):
                    if not template['steps']:
                        st.warning(f"模板 '{template['name']}' 尚未配置处理步骤")
                    else:
                        with st.spinner(f"正在执行 {template['name']}..."):
                            for step in template['steps']:
                                _execute_step(step)
                            st.success(f"{template['name']} 执行完成！")
                            st.rerun()


# ============================================
# 数据处理标签页主函数
# ============================================

def render_data_processing_tab():
    """数据处理标签页"""
    if st.session_state.df is None:
        st.info("请先上传数据")
        return
    
    # ===== 一键处理面板 =====
    render_quick_process()
    
    st.markdown("---")
    
    # ===== 全局操作栏 =====
    st.markdown("### ⚡ 全局操作")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
    with col1:
        if st.button("↩️ 撤销", key="global_undo", use_container_width=True):
            undo_last_operation()
    with col2:
        if st.button("↪️ 重做", key="global_redo", use_container_width=True):
            redo_last_operation()
    with col3:
        if st.button("📋 历史", key="global_history", use_container_width=True):
            show_global_history()
    with col4:
        if st.button("🔄 重置", key="global_reset", use_container_width=True):
            if st.session_state.original_df is not None:
                st.session_state.preview_manager.record_operation("重置到原始数据")
                st.session_state.df = st.session_state.original_df.copy()
                st.success("已重置到初始状态")
                st.rerun()
            else:
                st.warning("没有原始数据可重置")
    
    st.divider()
    
    # ===== 数据清洗（8个标签页）=====
    st.markdown("### 🧹 数据清洗")
    clean_tabs = st.tabs(["🗑️ 去重", "🔄 替换", "📝 转换", "✂️ 分列", "🔗 合并", "✏️ 表头", "🗑️ 删除", "🔍 筛选"])
    
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
    with clean_tabs[5]:
        render_rename_columns_section()
    with clean_tabs[6]:
        render_delete_columns_section()
    with clean_tabs[7]:
        render_filter_section_in_tab()
    
    st.divider()
    
    # ===== 数据确认 =====
    render_confirm_data_button()


def render_deduplicate_section():
    """去重功能"""
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
            st.session_state.df,
            st.session_state.df,
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
    with st.expander("🔄 替换值", expanded=True):
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
                    st.session_state.df,
                    st.session_state.df,
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
                    st.session_state.df,
                    st.session_state.df,
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
                    st.session_state.df,
                    st.session_state.df,
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
    st.write("转换数据类型")
    
    col = st.selectbox(
        "选择列", 
        st.session_state.df.columns, 
        key="convert_col"
    )
    
    target_type = st.selectbox(
        "转换为类型", 
        ["文本", "数值", "日期时间", "百分比"],
        key="convert_type"
    )
    
    type_map = {
        "文本": "str",
        "数值": "float",
        "日期时间": "datetime",
        "百分比": "percentage"
    }
    
    if st.button("✅ 执行转换", key="btn_convert", use_container_width=True):
        success, message = execute_data_operation(
            st.session_state.df,
            st.session_state.df,
            "类型转换",
            col, type_map[target_type]
        )
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)


def render_split_column_section():
    """分列功能"""
    st.write("将一列拆分为多列")
    
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
    
    if st.button("👁️ 预览分列", key="preview_split", use_container_width=True):
        preview_df = st.session_state.df.head(3).copy()
        preview_result = execute_split_preview(preview_df, col, separator, mode)
        st.write("预览结果（前3行）：")
        st.dataframe(preview_result, use_container_width=True)
    
    if st.button("✅ 执行分列", key="btn_split", use_container_width=True):
        success, message = execute_data_operation(
            st.session_state.df,
            st.session_state.df,
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
    st.write("将多列合并为一列")
    
    merge_cols = st.multiselect(
        "选择要合并的列（按顺序选择）", 
        st.session_state.df.columns,
        key="merge_cols"
    )
    
    if len(merge_cols) >= 2:
        separator = st.text_input("分隔符", value=" ", key="merge_sep")
        
        new_col_name = st.text_input(
            "新列名", 
            value="_".join(merge_cols)[:30],
            key="new_col_name"
        )
        
        if st.button("👁️ 预览合并", key="preview_merge", use_container_width=True):
            preview_df = st.session_state.df.head(3).copy()
            preview_df = execute_merge_preview(preview_df, merge_cols, new_col_name, separator)
            st.write("预览结果（前3行）：")
            st.dataframe(preview_df[[new_col_name] + merge_cols], use_container_width=True)
        
        if st.button("✅ 执行合并", key="btn_merge", use_container_width=True):
            success, message = execute_data_operation(
                st.session_state.df,
                st.session_state.df,
                "合并列",
                merge_cols, new_col_name, separator
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    else:
        st.info("请至少选择2列进行合并")


def render_rename_columns_section():
    """修改表头功能"""
    st.write("修改列名称（表头）")
    
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
        ["单个修改", "批量添加前缀/后缀", "批量替换文本", "批量修改（编辑表格）", "提升为标题"],
        key="rename_mode",
        horizontal=True
    )
    
    # ========== 方式一：单个修改 ==========
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
                    st.session_state.df = st.session_state.df.rename(columns={old_name: new_name})
                    st.session_state.preview_manager.record_operation(f"修改表头: {old_name}→{new_name}")
                    st.success(f"已将 '{old_name}' 修改为 '{new_name}'")
                    st.rerun()
            else:
                st.warning("请输入新列名")
    
    # ========== 方式二：批量添加前缀/后缀 ==========
    elif rename_mode == "批量添加前缀/后缀":
        col1, col2 = st.columns(2)
        with col1:
            prefix = st.text_input("添加前缀", key="rename_prefix", placeholder="留空则不添加")
        with col2:
            suffix = st.text_input("添加后缀", key="rename_suffix", placeholder="留空则不添加")
        
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
                st.success("批量添加完成")
                st.rerun()
    
    # ========== 方式三：批量替换文本 ==========
    elif rename_mode == "批量替换文本":
        col1, col2 = st.columns(2)
        with col1:
            old_text = st.text_input("查找内容", key="rename_replace_old")
        with col2:
            new_text = st.text_input("替换为", key="rename_replace_new")
        
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
                st.success("批量替换完成")
                st.rerun()
    
    # ========== 方式四：批量修改（编辑表格） ==========
    elif rename_mode == "批量修改（编辑表格）":
        st.markdown("**编辑表格修改列名**")
        st.caption("双击单元格直接编辑，支持批量修改")
        
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
        
        new_names = edited_df['新列名'].tolist()
        has_duplicate = len(new_names) != len(set(new_names))
        
        if has_duplicate:
            st.error("新列名存在重复，请修改后重试")
        else:
            changes = []
            for old, new in zip(current_columns, new_names):
                if old != new:
                    changes.append(f"'{old}' → '{new}'")
            if changes:
                st.info(f"将修改 {len(changes)} 个列名")
        
        if st.button("✏️ 应用所有修改", key="btn_rename_batch", use_container_width=True):
            if has_duplicate:
                st.error("请先解决重复列名问题")
            else:
                st.session_state.df.columns = new_names
                st.session_state.preview_manager.record_operation("批量修改表头")
                st.success(f"已修改 {len(changes)} 个列名")
                st.rerun()
    
    # ========== 方式五：提升为标题 ==========
    elif rename_mode == "提升为标题":
        st.markdown("**提升为标题**")
        st.caption("将指定行设置为列名，并删除该行之前的所有行")
        
        df = st.session_state.df
        total_rows = len(df)
        
        # 行号输入
        row_number = st.number_input(
            "请指定第几行作为标题行（从1开始计数）",
            min_value=1,
            max_value=total_rows,
            value=min(3, total_rows),
            step=1,
            key="promote_row_number"
        )
        
        # 预览
        with st.expander("预览数据"):
            st.write(f"**第 {row_number} 行数据（将成为新列名）:**")
            header_row = df.iloc[row_number - 1].tolist()
            st.write(header_row)
            st.write(f"**前5行数据预览:**")
            st.dataframe(df.head(5), use_container_width=True)
        
        # 执行按钮
        if st.button("✅ 确认提升", key="btn_promote_header", use_container_width=True, type="primary"):
            try:
                # 获取新列名候选
                new_columns_raw = df.iloc[row_number - 1].tolist()
                
                # ========== 验证和清理列名 ==========
                cleaned_columns = []
                col_counter = 1
                
                for i, col in enumerate(new_columns_raw):
                    # 1. 转换为字符串
                    col_str = str(col) if col is not None else ""
                    
                    # 2. 处理空值
                    if col_str == "" or col_str == "nan" or col_str == "None":
                        col_str = f"列_{col_counter}"
                        col_counter += 1
                    
                    # 3. 处理全数字
                    if col_str.isdigit():
                        col_str = f"列_{col_str}"
                    
                    # 4. 处理非法字符（只允许中文、字母、数字、下划线）
                    import re
                    col_str = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9_]', '_', col_str)
                    
                    # 5. 去除首尾下划线
                    col_str = col_str.strip('_')
                    
                    # 6. 如果处理后为空，填充默认值
                    if col_str == "":
                        col_str = f"列_{col_counter}"
                        col_counter += 1
                    
                    cleaned_columns.append(col_str)
                
                # 7. 处理重复列名
                final_columns = []
                seen = {}
                for col in cleaned_columns:
                    if col not in seen:
                        seen[col] = 1
                        final_columns.append(col)
                    else:
                        seen[col] += 1
                        final_columns.append(f"{col}_{seen[col]}")
                
                # 验证最终列名数量
                if len(final_columns) != len(new_columns_raw):
                    st.warning(f"列名数量不一致，原列数={len(new_columns_raw)}，处理后={len(final_columns)}")
                    return
                
                # 执行数据转换
                # 删除前 row_number 行（0 到 row_number-1）
                new_df = df.iloc[row_number:].reset_index(drop=True)
                new_df.columns = final_columns
                
                # 更新数据
                st.session_state.df = new_df
                st.session_state.original_df = new_df.copy()
                st.session_state.preview_manager.record_operation(f"提升第{row_number}行为标题")
                
                st.success(f"✅ 已将第 {row_number} 行提升为标题，删除前 {row_number - 1} 行")
                st.rerun()
                
            except Exception as e:
                st.error(f"操作失败: {str(e)}")


def render_delete_columns_section():
    """删除列功能（支持删除空列）"""
    st.write("删除指定的列")
    
    # 获取所有列名
    all_columns = st.session_state.df.columns.tolist()
    
    # 检测空列
    empty_columns = []
    for col in all_columns:
        if st.session_state.df[col].isna().all() or (st.session_state.df[col] == "").all():
            empty_columns.append(col)
    
    # 显示空列检测结果
    if empty_columns:
        st.warning(f"⚠️ 检测到 {len(empty_columns)} 个空列（所有值都为空）")
        with st.expander(f"查看空列列表 ({len(empty_columns)}列)"):
            for col in empty_columns:
                st.write(f"- `{col}`")
    
    # 删除方式选择
    delete_mode = st.radio(
        "选择删除方式",
        ["手动选择列删除", "删除所有空列"],
        key="delete_mode",
        horizontal=True
    )
    
    if delete_mode == "手动选择列删除":
        # ===========================================
        # 【位置1】手动选择删除的代码块
        # ===========================================
        cols_to_delete = st.multiselect(
            "选择要删除的列", 
            all_columns,
            key="delete_cols_section"
        )
        
        if cols_to_delete:
            st.caption(f"将删除 {len(cols_to_delete)} 列: {', '.join(cols_to_delete[:5])}{'...' if len(cols_to_delete) > 5 else ''}")
            
            # 【需要修改的按钮1】
            if st.button("🗑️ 执行删除", key="btn_delete_section", use_container_width=True, type="primary"):
                success, message = execute_data_operation(
                    st.session_state.df,
                    st.session_state.df,
                    "删除列",
                    cols_to_delete
                )
                if success:
                    st.success(message)
                    # 【新增】更新预览
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("请选择要删除的列")
    
    else:
        # ===========================================
        # 【位置2】删除所有空列的代码块
        # ===========================================
        if not empty_columns:
            st.info("没有检测到空列")
        else:
            st.warning(f"将删除 {len(empty_columns)} 个空列")
            
            with st.expander("查看要删除的列"):
                for col in empty_columns:
                    st.write(f"- `{col}`")
            
            col1, col2 = st.columns(2)
            with col1:
                # 【需要修改的按钮2】
                if st.button("✅ 确认删除空列", key="btn_delete_empty", use_container_width=True, type="primary"):
                    success, message = execute_data_operation(
                        st.session_state.df,
                        st.session_state.df,
                        "删除空列",
                        empty_columns
                    )
                    if success:
                        st.success(f"已删除 {len(empty_columns)} 个空列")
                        # 【新增】更新预览
                        
                        st.rerun()
                    else:
                        st.error(message)
            with col2:
                if st.button("取消", key="btn_cancel_delete", use_container_width=True):
                    st.rerun()


def render_filter_section_in_tab():
    """筛选功能（作为完整的标签页显示）"""
    
    # 筛选历史快捷操作
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("↩️ 撤销筛选", key="undo_filter_tab", use_container_width=True):
            undo_last_filter()
    with col2:
        if st.button("🔄 重置", key="reset_filter_tab", use_container_width=True):
            reset_to_original()
    with col3:
        if st.button("📋 筛选历史", key="filter_history_tab", use_container_width=True):
            show_filter_history()
    
    st.markdown("---")
    
    # 筛选主界面
    st.markdown("#### 设置筛选条件")
    
    all_cols = ["请选择要筛选的列"] + st.session_state.df.columns.tolist()
    selected_col = st.selectbox(
        "选择列",
        all_cols,
        key="filter_column_tab",
        index=0
    )
    
    if selected_col != "请选择要筛选的列":
        col_dtype = st.session_state.df[selected_col].dtype
        is_numeric = pd.api.types.is_numeric_dtype(col_dtype)
        is_datetime = pd.api.types.is_datetime64_any_dtype(col_dtype)
        
        if is_numeric:
            conditions = ["等于", "不等于", "大于", "小于", "大于等于", "小于等于", "介于", "为空", "不为空"]
        elif is_datetime:
            conditions = ["等于", "不等于", "早于", "晚于", "介于", "今天", "本周", "本月", "为空", "不为空"]
        else:
            conditions = ["包含", "不包含", "等于", "不等于", "开头为", "结尾为", "为空", "不为空"]
        
        condition = st.selectbox("条件", conditions, key="filter_condition_tab")
        
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
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 预览结果", key="preview_filter_tab", use_container_width=True):
                preview_unified_filter(selected_col, condition, filter_value)
        with col2:
            if st.button("✅ 应用筛选", key="apply_filter_tab", use_container_width=True, type="primary"):
                apply_unified_filter(selected_col, condition, filter_value)
    
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


def render_confirm_data_button():
    """确认使用本数据按钮"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 确认数据")
        st.caption("点击确认后，当前数据将作为分析基准")
    with col2:
        if st.button("✅ 确认使用本数据", key="confirm_data", type="primary", use_container_width=True):
            st.session_state.confirmed_data = st.session_state.df.copy()
            st.session_state.data_confirmed = True
            st.success("数据已确认，将作为后续分析的基准")
            st.session_state.preview_manager.record_operation("数据确认")


# ===== 辅助函数 =====
def execute_data_operation(df, original_df, operation_name, *args, **kwargs):
    """执行数据操作的标准流程"""
    try:

        
        Logger.info(f"开始执行{operation_name}操作")
        before_shape = df.shape if df is not None else (0, 0)
        
        cleaner = DataCleaner()
        result_df = df.copy()  # 创建副本
        
        if operation_name == "去重":
            result_df = cleaner.deduplicate(df, *args, **kwargs)
        elif operation_name == "文本替换":
            result_df = cleaner.text_replace(df, *args, **kwargs)
        elif operation_name == "正则替换":
            result_df = cleaner.text_replace(df, *args, **kwargs)
        elif operation_name == "空值替换":
            result_df = cleaner.null_replace(df, *args, **kwargs)
        elif operation_name == "类型转换":
            result_df = cleaner.convert_type(df, *args, **kwargs)
        elif operation_name == "分列":
            result_df = cleaner.split_column(df, *args, **kwargs)
        elif operation_name == "合并列":
            result_df = cleaner.merge_columns(df, *args, **kwargs)
        elif operation_name == "删除列" or operation_name == "删除空列":
            # 确保 args[0] 是列名列表
            cols_to_delete = args[0] if args else []
            result_df = cleaner.delete_columns(df, cols_to_delete)
        
        # 重置索引
        result_df = result_df.reset_index(drop=True)
        
        after_shape = result_df.shape
        Logger.info(f"{operation_name}完成: {before_shape} -> {after_shape}")
        
        # 直接更新 session_state 中的 df
        st.session_state.df = result_df
        st.session_state.preview_manager.record_operation(operation_name)
        
        return True, f"{operation_name}操作成功"
    except Exception as e:
        Logger.error(f"{operation_name}失败: {str(e)}")
        return False, f"{operation_name}失败: {str(e)}"


def execute_split_preview(df, column, separator, mode):
    """预览分列效果"""
    from utils.data_cleaner import DataCleaner
    cleaner = DataCleaner()
    return cleaner.split_column(df, column, separator, mode)


def execute_merge_preview(df, columns, new_col_name, separator):
    """预览合并效果"""
    from utils.data_cleaner import DataCleaner
    cleaner = DataCleaner()
    return cleaner.merge_columns(df, columns, new_col_name, separator)


def undo_last_operation():
    """全局撤销操作"""
    if st.session_state.df is not None:
        from components.history_manager import HistoryManager
        history = HistoryManager()
        st.session_state.df = history.undo(st.session_state.df)
        st.session_state.preview_manager.record_operation("撤销")
        st.rerun()


def redo_last_operation():
    """全局重做操作"""
    if st.session_state.df is not None:
        from components.history_manager import HistoryManager
        history = HistoryManager()
        st.session_state.df = history.redo(st.session_state.df)
        st.session_state.preview_manager.record_operation("重做")
        st.rerun()


def show_global_history():
    """显示全局历史"""
    from components.history_manager import HistoryManager
    history = HistoryManager()
    history.show_history()


def undo_last_filter():
    """撤销最后一次筛选"""
    if 'filter_history' in st.session_state and st.session_state.filter_history:
        last_state = st.session_state.filter_history.pop()
        st.session_state.df = last_state['data']
        st.session_state.preview_manager.record_operation(f"撤销{last_state['type']}")
        st.success(f"已撤销{last_state['type']}")
        st.rerun()
    else:
        st.warning("没有可撤销的筛选操作")


def reset_to_original():
    """重置到原始数据"""
    if st.session_state.original_df is not None:
        if 'filter_history' not in st.session_state:
            st.session_state.filter_history = []
        st.session_state.filter_history.append({
            'data': st.session_state.df.copy(),
            'type': '重置到原始',
            'params': '',
            'time': datetime.now().strftime('%H:%M:%S')
        })
        st.session_state.df = st.session_state.original_df.copy()
        st.session_state.preview_manager.record_operation("重置到原始数据")
        st.success("已重置到原始数据")
        st.rerun()
    else:
        st.warning("没有原始数据可重置")


def show_filter_history():
    """显示筛选历史"""
    if 'filter_history' in st.session_state and st.session_state.filter_history:
        history_df = pd.DataFrame([
            {
                '操作': item['type'],
                '参数': item['params'],
                '时间': item.get('time', '')
            }
            for item in st.session_state.filter_history[-5:]
        ])
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("暂无筛选历史")


def preview_unified_filter(column, condition, value):
    """预览统一筛选结果"""
    try:
        from utils.data_filter import DataFilter
        filter_obj = DataFilter()
        
        preview_df = st.session_state.df.head(20).copy()
        
        if condition in ["为空", "不为空"]:
            if condition == "为空":
                result_df = preview_df[preview_df[column].isna() | (preview_df[column] == "null")]
            else:
                result_df = preview_df[preview_df[column].notna() & (preview_df[column] != "null")]
        elif condition in ["今天", "本周", "本月"]:
            result_df = filter_obj.date_filter(preview_df, column, condition, None)
        elif condition == "介于":
            min_val, max_val = value
            result_df = preview_df[(preview_df[column] >= min_val) & (preview_df[column] <= max_val)]
        else:
            result_df = filter_obj.text_filter(preview_df, column, condition, str(value)) if not pd.api.types.is_numeric_dtype(preview_df[column].dtype) else filter_obj.numeric_filter(preview_df, column, condition, value)
        
        st.session_state.filter_preview = result_df
        st.session_state.filter_preview_info = f"筛选结果：{len(result_df)} 行（共预览20行）"
        st.rerun()
    except Exception as e:
        st.error(f"预览失败: {str(e)}")


def apply_unified_filter(column, condition, value):
    """应用统一筛选"""
    try:
        from utils.data_filter import DataFilter
        filter_obj = DataFilter()
        
        if 'filter_history' not in st.session_state:
            st.session_state.filter_history = []
        
        st.session_state.filter_history.append({
            'data': st.session_state.df.copy(),
            'type': '筛选',
            'params': f"{column} {condition} {value}",
            'time': datetime.now().strftime('%H:%M:%S')
        })
        
        if condition in ["为空", "不为空"]:
            if condition == "为空":
                result_df = st.session_state.df[st.session_state.df[column].isna() | (st.session_state.df[column] == "null")]
            else:
                result_df = st.session_state.df[st.session_state.df[column].notna() & (st.session_state.df[column] != "null")]
        elif condition in ["今天", "本周", "本月"]:
            result_df = filter_obj.date_filter(st.session_state.df, column, condition, None)
        elif condition == "介于":
            min_val, max_val = value
            result_df = st.session_state.df[(st.session_state.df[column] >= min_val) & (st.session_state.df[column] <= max_val)]
        else:
            result_df = filter_obj.text_filter(st.session_state.df, column, condition, str(value)) if not pd.api.types.is_numeric_dtype(st.session_state.df[column].dtype) else filter_obj.numeric_filter(st.session_state.df, column, condition, value)
        
        st.session_state.df = result_df
        st.session_state.preview_manager.record_operation(f"筛选-{condition}")
        
        st.session_state.filter_preview = None
        st.session_state.filter_preview_info = None
        
        st.success(f"筛选完成，当前 {len(result_df)} 行")
        st.rerun()
    except Exception as e:
        st.error(f"筛选失败: {str(e)}")