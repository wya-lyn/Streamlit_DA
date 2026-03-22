"""
文件加载模块：处理各种格式文件的读取
"""

import streamlit as st
import pandas as pd
import json
import os
from io import StringIO

class FileLoader:
    """文件加载器，支持CSV/Excel/JSON"""
    
    @staticmethod
    def load_file(uploaded_file):
        """加载上传的文件"""
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
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
        try:
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            for encoding in encodings:
                try:
                    file.seek(0)
                    df = pd.read_csv(file, encoding=encoding)
                    # 移除 fillna("null")，保持空值原样
                    return df
                except UnicodeDecodeError:
                    continue
                except Exception:
                    continue
            
            file.seek(0)
            df = pd.read_csv(file)
            # 移除 fillna("null")，保持空值原样
            return df
            
        except Exception as e:
            st.error(f"CSV读取失败: {str(e)}")
            return None
    
    @staticmethod
    def _load_excel(file):
        """加载Excel文件（支持多工作表选择）"""
        try:
            import pandas as pd
            import streamlit as st
            
            xl = pd.ExcelFile(file)
            sheet_names = xl.sheet_names
            
            # 只有一个工作表，直接加载
            if len(sheet_names) == 1:
                df = pd.read_excel(file, sheet_name=sheet_names[0])
                return df
            
            # 多个工作表，显示选择器
            st.info(f"📑 检测到 {len(sheet_names)} 个工作表")
            
            # 初始化/重置 session_state（确保当前文件的选择有效）
            if 'excel_selected_sheet' not in st.session_state:
                st.session_state.excel_selected_sheet = sheet_names[0]
            else:
                # 检查保存的选择是否在当前文件的工作表列表中
                if st.session_state.excel_selected_sheet not in sheet_names:
                    st.session_state.excel_selected_sheet = sheet_names[0]
            
            if 'excel_confirmed' not in st.session_state:
                st.session_state.excel_confirmed = False
            
            # 工作表选择下拉框
            selected_sheet = st.selectbox(
                "请选择要加载的工作表",
                sheet_names,
                key="excel_sheet_selector",
                index=sheet_names.index(st.session_state.excel_selected_sheet)
            )
            st.session_state.excel_selected_sheet = selected_sheet
            
            # 确认按钮
            if st.button("✅ 确认加载", key="confirm_excel_load", use_container_width=True):
                st.session_state.excel_confirmed = True
                st.rerun()
                return None
            
            # 未确认时等待
            if not st.session_state.excel_confirmed:
                st.info("请选择工作表后点击「确认加载」按钮")
                return None
            
            # 确认后加载数据
            df = pd.read_excel(file, sheet_name=st.session_state.excel_selected_sheet)
            
            # 加载完成后清除确认状态，以便下次上传
            st.session_state.excel_confirmed = False
            return df
            
        except Exception as e:
            st.error(f"Excel读取失败: {str(e)}")
            return None
        
    
    @staticmethod
    def _load_json(file):
        """加载JSON文件（支持嵌套展开，最大4层，支持JSON字符串解析）"""
        # 读取文件内容
        content = file.read()
        
        # 尝试多种编码
        try:
            data = json.loads(content.decode('utf-8'))
        except UnicodeDecodeError:
            try:
                data = json.loads(content.decode('utf-8-sig'))
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
        
        # 展开嵌套结构（最大4层，支持JSON字符串解析）
        def flatten_json(obj, parent_key='', sep='.', depth=0):
            """递归展开JSON对象，最大深度4层，支持JSON字符串解析"""
            print(f"[DEBUG] depth={depth}, parent_key={parent_key}, obj类型={type(obj)}")
            items = []
            
            # 深度限制
            if depth > 3:
                return {parent_key: json.dumps(obj, ensure_ascii=False) if isinstance(obj, (dict, list)) else obj}
            
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    
                    # 尝试将字符串解析为 JSON
                    if isinstance(v, str):
                        try:
                            parsed = json.loads(v)
                            if isinstance(parsed, (dict, list)):
                                v = parsed
                        except (json.JSONDecodeError, TypeError):
                            pass
                    
                    if isinstance(v, dict):
                        # 递归处理字典，深度+1
                        items.extend(flatten_json(v, new_key, sep=sep, depth=depth + 1).items())
                    elif isinstance(v, list):
                        # 处理列表中的每个元素
                        processed_list = []
                        has_complex = False
                        
                        for item in v:
                            if isinstance(item, str):
                                try:
                                    parsed = json.loads(item)
                                    if isinstance(parsed, (dict, list)):
                                        processed_list.append(parsed)
                                        has_complex = True
                                        continue
                                except (json.JSONDecodeError, TypeError):
                                    pass
                            processed_list.append(item)
                            if isinstance(item, (dict, list)):
                                has_complex = True
                        
                        if has_complex and depth < 3:
                            # 展开列表中的复杂对象
                            for idx, list_item in enumerate(processed_list):
                                if isinstance(list_item, dict):
                                    for sub_k, sub_v in list_item.items():
                                        sub_key = f"{new_key}.{idx}.{sub_k}" if parent_key else f"{idx}.{sub_k}"
                                        if isinstance(sub_v, (dict, list)):
                                            items.extend(flatten_json(sub_v, sub_key, sep=sep, depth=depth + 1).items())
                                        else:
                                            items.append((sub_key, sub_v))
                                elif isinstance(list_item, list):
                                    items.append((f"{new_key}.{idx}", json.dumps(list_item, ensure_ascii=False)))
                                else:
                                    items.append((f"{new_key}.{idx}", list_item))
                        else:
                            # 简单列表，转为 JSON 字符串
                            items.append((new_key, json.dumps(processed_list, ensure_ascii=False)))
                    else:
                        items.append((new_key, v))
            
            elif isinstance(obj, list):
                # 处理顶层数组中的对象
                for idx, item in enumerate(obj):
                    if isinstance(item, dict):
                        for k, v in item.items():
                            new_key = f"{parent_key}.{idx}.{k}" if parent_key else f"{idx}.{k}"
                            if isinstance(v, (dict, list)):
                                items.extend(flatten_json(v, new_key, sep=sep, depth=depth + 1).items())
                            else:
                                items.append((new_key, v))
                    elif isinstance(item, list):
                        items.append((f"{parent_key}.{idx}", json.dumps(item, ensure_ascii=False)))
                    else:
                        items.append((f"{parent_key}.{idx}", item))
            else:
                items.append((parent_key, obj))
            
            return dict(items)
        
        # 展开所有行
        flattened_data = []
        for row in json_data:
            if isinstance(row, dict):
                flattened_data.append(flatten_json(row, depth=0))  # 明确传递 depth=0
            else:
                flattened_data.append({'_value': row})
        
        # 创建 DataFrame
        df = pd.DataFrame(flattened_data)
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
            "memory_usage": df.memory_usage(deep=True).sum() / 1024,  # KB
            "missing_values": df.isna().sum().sum(),
            "numeric_columns": len(df.select_dtypes(include=['int64', 'float64']).columns),
            "text_columns": len(df.select_dtypes(include=['object']).columns)
        }
        
        return info