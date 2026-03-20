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
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            for encoding in encodings:
                try:
                    file.seek(0)
                    df = pd.read_csv(file, encoding=encoding)
                    # 缺失值统一为 "null"
                    df = df.fillna("null")
                    return df
                except UnicodeDecodeError:
                    continue
                except Exception:
                    continue
            
            # 如果都失败，使用默认编码
            file.seek(0)
            df = pd.read_csv(file)
            df = df.fillna("null")
            return df
            
        except Exception as e:
            st.error(f"CSV读取失败: {str(e)}")
            return None
    
    @staticmethod
    def _load_excel(file):
        """加载Excel文件（支持多工作表选择）"""
        try:
            # 获取所有工作表名称
            xl = pd.ExcelFile(file)
            sheet_names = xl.sheet_names
            
            # 调试信息
            print(f"【调试】Excel文件包含 {len(sheet_names)} 个工作表: {sheet_names}")
            
            if len(sheet_names) == 1:
                # 只有一个工作表，直接加载
                df = pd.read_excel(file, sheet_name=sheet_names[0])
                print(f"【调试】加载工作表: {sheet_names[0]}")
                st.info(f"✅ 已加载工作表: {sheet_names[0]}")
            else:
                # 多个工作表，在session_state中保存选择状态
                if 'selected_sheet' not in st.session_state:
                    st.session_state.selected_sheet = sheet_names[0]
                
                # 显示工作表选择器
                selected_sheet = st.selectbox(
                    "📑 选择要加载的工作表",
                    sheet_names,
                    key="excel_sheet_selector",
                    index=sheet_names.index(st.session_state.selected_sheet) if st.session_state.selected_sheet in sheet_names else 0
                )
                
                # 保存选择
                st.session_state.selected_sheet = selected_sheet
                
                # 加载选中的工作表
                df = pd.read_excel(file, sheet_name=selected_sheet)
                print(f"【调试】加载工作表: {selected_sheet}")
                st.info(f"✅ 已加载工作表: {selected_sheet}")
            
            # 缺失值统一为 "null"
            df = df.fillna("null")
            
            return df
            
        except Exception as e:
            st.error(f"Excel读取失败: {str(e)}")
            print(f"【调试】Excel读取错误: {str(e)}")
            return None
    
    @staticmethod
    def _load_json(file):
        """加载JSON文件"""
        try:
            data = json.load(file)
            
            # 处理不同格式的JSON
            if isinstance(data, list):
                # 数组格式 [{...}, {...}]
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # 对象格式，尝试多种结构
                if 'data' in data and isinstance(data['data'], list):
                    df = pd.DataFrame(data['data'])
                elif 'rows' in data and isinstance(data['rows'], list):
                    df = pd.DataFrame(data['rows'])
                else:
                    # 单条数据
                    df = pd.DataFrame([data])
            else:
                st.error("不支持的JSON格式")
                return None
            
            # 缺失值统一为 "null"
            df = df.fillna("null")
            return df
            
        except Exception as e:
            st.error(f"JSON读取失败: {str(e)}")
            return None
    
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