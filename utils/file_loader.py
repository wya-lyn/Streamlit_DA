"""
文件加载模块：处理各种格式文件的读取
"""

import streamlit as st
import pandas as pd
import json


class FileLoader:
    """文件加载器，支持CSV/Excel/JSON"""
    
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
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        for encoding in encodings:
            try:
                file.seek(0)
                df = pd.read_csv(file, encoding=encoding)
                return df
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
        
        # 如果都失败，使用默认编码
        file.seek(0)
        df = pd.read_csv(file)
        return df
    
    @staticmethod
    def _load_excel(file):
        """加载Excel文件（单工作表直接加载）"""
        try:
            import pandas as pd
            # 注意：多工作表已在 render_file_uploader 中处理
            # 这里只处理单工作表的情况
            df = pd.read_excel(file, sheet_name=0)
            return df
        except Exception as e:
            st.error(f"Excel读取失败: {str(e)}")
            return None
                
    @staticmethod
    def _load_json(file):
        """加载JSON文件（支持嵌套展开，最大4层）"""
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
        

                
        # 展开嵌套结构（最大4层）
        def flatten_json(obj, parent_key='', sep='.', depth=0, is_top_level=False):
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
                                # 列表元素是对象，不加索引，直接用 new_key
                                items.extend(flatten_json(item, new_key, sep=sep, depth=depth + 1).items())
                            else:
                                # 列表元素是基本类型，需要加索引
                                item_key = f"{new_key}{sep}{idx}"
                                items.append((item_key, item))
                    else:
                        items.append((new_key, v))
            
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    if isinstance(item, dict):
                        # 顶层数组：直接展开，不加索引
                        items.extend(flatten_json(item, new_key, sep=sep, depth=depth + 1).items())
                    else:
                        items.append((f"{idx}", item))
            else:
                items.append((parent_key, obj))
            
            return dict(items)
                
        flattened_data = []
        for row in json_data:
            if isinstance(row, dict):
                # 注意：row 已经是数组中的元素，不是顶层数组
                # 所以 is_top_level=False
                flattened_row = flatten_json(row, is_top_level=False)
                flattened_data.append(flattened_row)
            else:
                flattened_data.append({'_value': row})

        # 打印第一行的所有键
        if flattened_data:
            print(f"【调试】第一行的键: {list(flattened_data[0].keys())}")
            print(f"【调试】第一行的键数量: {len(flattened_data[0].keys())}")
        odds_keys = [k for k in flattened_data[0].keys() if 'oddsInternational' in k]
        print(f"【调试】包含 oddsInternational 的键: {odds_keys}")
        
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
            "memory_usage": df.memory_usage(deep=True).sum() / 1024,
            "missing_values": df.isna().sum().sum(),
            "numeric_columns": len(df.select_dtypes(include=['int64', 'float64']).columns),
            "text_columns": len(df.select_dtypes(include=['object']).columns)
        }
        return info