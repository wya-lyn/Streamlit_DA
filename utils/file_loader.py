"""
文件加载模块：处理各种格式文件的读取
"""

import streamlit as st
import pandas as pd
import json
import io
import hashlib


class FileLoader:
    """文件加载器，支持CSV/Excel/JSON"""
    
    @staticmethod
    def _get_file_hash(file_content):
        """生成文件内容的 MD5 哈希值（用于唯一标识）"""
        return hashlib.md5(file_content).hexdigest()
    
    @staticmethod
    def _clean_excel_states():
        """清理所有 excel_state_ 开头的 session_state"""
        for key in list(st.session_state.keys()):
            if key.startswith('excel_state_'):
                del st.session_state[key]
    
    @staticmethod
    def load_file(uploaded_file):
        """加载上传的文件，返回 DataFrame"""
        if uploaded_file is None:
            return None
        
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        try:
            if file_extension == 'csv':
                return FileLoader._load_csv(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                return FileLoader._load_excel(uploaded_file)
            elif file_extension == 'json':
                return FileLoader._load_json(uploaded_file)
            else:
                st.error(f"不支持的文件格式: {file_extension}")
                return None
        except Exception as e:
            st.error(f"文件加载失败: {str(e)}")
            return None
    
    @staticmethod
    def _load_csv(file):
        """加载CSV文件"""
        # 读取文件内容用于哈希计算（可选，用于文件去重）
        file.seek(0)
        file_content = file.read()
        file_hash = FileLoader._get_file_hash(file_content)
        
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        df = None
        
        for encoding in encodings:
            try:
                file.seek(0)
                df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
        
        # 如果都失败，使用默认编码
        if df is None:
            file.seek(0)
            df = pd.read_csv(io.BytesIO(file_content))
        
        if df is not None:
            # 可选：存储文件哈希用于去重检测
            st.session_state['last_file_hash'] = file_hash
        
        return df
    
    @staticmethod
    def _load_excel(file):
        """加载Excel文件（支持多工作表选择）"""
        try:
            # 读取文件内容到内存
            file_content = file.read()
            
            # 生成稳定的文件哈希
            file_hash = FileLoader._get_file_hash(file_content)
            
            # 获取工作表名称
            xl = pd.ExcelFile(io.BytesIO(file_content))
            sheet_names = xl.sheet_names
            
            # 只有一个工作表，直接加载
            if len(sheet_names) == 1:
                df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_names[0])
                # 清理可能残留的状态
                FileLoader._clean_excel_states()
                return df
            
            # 多个工作表，显示选择器
            st.info(f"📑 检测到 {len(sheet_names)} 个工作表")
            
            state_key = f"excel_state_{file_hash}"
            
            # 清理其他旧的 excel_state（避免累积）
            for key in list(st.session_state.keys()):
                if key.startswith('excel_state_') and key != state_key:
                    del st.session_state[key]
            
            # 初始化状态
            if state_key not in st.session_state:
                st.session_state[state_key] = {
                    'selected_sheet': sheet_names[0],
                    'confirmed': False,
                    'content': file_content,
                    'sheet_names': sheet_names,
                    'file_hash': file_hash
                }
            
            state = st.session_state[state_key]
            
            # 工作表选择下拉框
            selected_sheet = st.selectbox(
                "请选择要加载的工作表",
                state['sheet_names'],
                key=f"excel_sheet_{file_hash}",
                index=state['sheet_names'].index(state['selected_sheet'])
            )
            state['selected_sheet'] = selected_sheet
            
            # 确认按钮
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("✅ 确认加载", key=f"excel_confirm_{file_hash}", use_container_width=True):
                    state['confirmed'] = True
                    st.rerun()
                    return None
            
            # 取消按钮（可选）
            with col2:
                if st.button("❌ 取消", key=f"excel_cancel_{file_hash}", use_container_width=True):
                    FileLoader._clean_excel_states()
                    st.rerun()
                    return None
            
            # 未确认时等待
            if not state['confirmed']:
                st.info("请选择工作表后点击「确认加载」按钮")
                return None
            
            # 确认后从保存的内容加载数据
            df = pd.read_excel(io.BytesIO(state['content']), sheet_name=state['selected_sheet'])
            
            # 加载完成后清理状态
            FileLoader._clean_excel_states()
            
            return df
            
        except Exception as e:
            st.error(f"Excel读取失败: {str(e)}")
            # 发生错误时清理状态
            FileLoader._clean_excel_states()
            return None
    
    @staticmethod
    def _load_json(file):
        """加载JSON文件（支持嵌套展开，最大4层）"""
        # 读取文件内容
        file.seek(0)
        file_content = file.read()
        
        # 生成文件哈希（用于去重）
        file_hash = FileLoader._get_file_hash(file_content)
        
        # 尝试多种编码
        try:
            data = json.loads(file_content.decode('utf-8'))
        except UnicodeDecodeError:
            try:
                data = json.loads(file_content.decode('utf-8-sig'))
            except Exception:
                st.error("文件编码错误，请使用 UTF-8 编码")
                return None
        except json.JSONDecodeError as e:
            st.error(f"JSON 格式错误: {str(e)}")
            return None
        
        # 处理不同的JSON结构
        if isinstance(data, list):
            json_data = data
        elif isinstance(data, dict):
            if 'data' in data and isinstance(data['data'], list):
                json_data = data['data']
            else:
                st.error("不是规范的 JSON 格式：对象中没有 data 数组字段")
                return None
        else:
            st.error("不是规范的 JSON 格式：根节点必须是数组或包含 data 数组的对象")
            return None
        
        # 检查数据是否为空
        if not json_data:
            st.error("JSON 文件中没有数据")
            return None
        
        # 展开嵌套结构（最大4层）
        def flatten_json(obj, parent_key='', sep='.', depth=0):
            """递归展开JSON对象，最大深度4层"""
            items = []
            
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    
                    if isinstance(v, dict) and depth < 3:
                        items.extend(flatten_json(v, new_key, sep=sep, depth=depth + 1).items())
                    elif isinstance(v, list):
                        # 处理列表
                        for idx, item in enumerate(v):
                            if isinstance(item, dict):
                                items.extend(flatten_json(item, new_key, sep=sep, depth=depth + 1).items())
                            else:
                                item_key = f"{new_key}{sep}{idx}"
                                items.append((item_key, item))
                    else:
                        items.append((new_key, v))
            
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    if isinstance(item, dict):
                        items.extend(flatten_json(item, parent_key, sep=sep, depth=depth + 1).items())
                    else:
                        items.append((f"{parent_key}{sep}{idx}" if parent_key else f"{idx}", item))
            else:
                items.append((parent_key, obj))
            
            return dict(items)
        
        flattened_data = []
        for row in json_data:
            if isinstance(row, dict):
                flattened_row = flatten_json(row)
                flattened_data.append(flattened_row)
            else:
                flattened_data.append({'_value': row})
        
        # 创建 DataFrame
        df = pd.DataFrame(flattened_data)
        
        # 存储文件哈希（可选）
        st.session_state['last_file_hash'] = file_hash
        
        return df
    
    @staticmethod
    def get_file_info(df):
        """获取文件信息"""
        if df is None:
            return {}
        
        info = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum() / 1024,
            "missing_values": df.isna().sum().sum(),
            "numeric_columns": len(df.select_dtypes(include=['int64', 'float64']).columns),
            "text_columns": len(df.select_dtypes(include=['object']).columns)
        }
        return info