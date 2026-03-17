import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# 页面配置
st.set_page_config(
    page_title="数据洞察助手", 
    page_icon="📊",
    layout="wide"
)

# 标题
st.title("📊 数据洞察助手")
st.markdown("上传你的数据文件，开始探索性数据分析")

# 初始化session state
if 'df' not in st.session_state:
    st.session_state.df = None

# 侧边栏
with st.sidebar:
    st.header("1. 数据上传")
    uploaded_file = st.file_uploader(
        "选择文件 (CSV/Excel)", 
        type=['csv', 'xlsx', 'xls'],
        help="支持CSV、Excel格式，最大200MB"
    )
    
    if uploaded_file:
        try:
            # 读取文件
            with st.spinner("正在加载数据..."):
                if uploaded_file.name.endswith('csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.df = df
                
            st.success(f"✅ 加载成功！")
            st.info(f"📊 {len(df)} 行 × {len(df.columns)} 列")
            
            # 数据类型概览
            col_types = df.dtypes.value_counts()
            st.caption(f"数据类型: {', '.join([f'{k}:{v}' for k,v in col_types.items()])}")
            
        except Exception as e:
            st.error(f"❌ 读取失败：{str(e)}")
            st.session_state.df = None

# 主界面
if st.session_state.df is not None:
    df = st.session_state.df
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 数据预览", "📊 可视化分析", "📈 统计分析", "💾 导出数据"])
    
    # Tab 1: 数据预览
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("数据预览")
            # 显示行数选择
            rows_to_show = st.slider("显示行数", 5, 100, 10)
            st.dataframe(df.head(rows_to_show), use_container_width=True)
        
        with col2:
            st.subheader("数据概览")
            st.metric("总行数", len(df))
            st.metric("总列数", len(df.columns))
            st.metric("缺失值", df.isna().sum().sum())
            
            # 快速统计
            st.caption("字段列表")
            for col in df.columns[:10]:  # 最多显示10个
                st.text(f"• {col}")
            if len(df.columns) > 10:
                st.caption(f"... 还有 {len(df.columns)-10} 个字段")
    
    # Tab 2: 可视化分析
    with tab2:
        st.subheader("可视化分析")
        
        # 选择图表类型
        chart_type = st.selectbox(
            "选择图表类型",
            ["柱状图", "折线图", "散点图", "箱线图", "直方图", "热力图"]
        )
        
        # 根据图表类型显示不同选项
        if chart_type in ["柱状图", "折线图", "散点图", "箱线图"]:
            col1, col2 = st.columns(2)
            
            with col1:
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                if len(numeric_cols) > 0:
                    x_axis = st.selectbox("X轴", numeric_cols)
                else:
                    st.warning("没有数值型字段")
                    x_axis = None
            
            with col2:
                if chart_type != "箱线图":
                    y_axis = st.selectbox("Y轴", numeric_cols, index=min(1, len(numeric_cols)-1))
                else:
                    y_axis = None
            
            if x_axis:
                if chart_type == "柱状图" and y_axis:
                    fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} 按 {x_axis} 分布")
                elif chart_type == "折线图" and y_axis:
                    fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} 趋势")
                elif chart_type == "散点图" and y_axis:
                    fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
                elif chart_type == "箱线图":
                    fig = px.box(df, y=x_axis, title=f"{x_axis} 分布")
                
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "直方图":
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                col = st.selectbox("选择字段", numeric_cols)
                bins = st.slider("组数", 5, 100, 30)
                fig = px.histogram(df, x=col, nbins=bins, title=f"{col} 分布直方图")
                st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "热力图":
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) >= 2:
                corr = df[numeric_cols].corr()
                fig = px.imshow(corr, text_auto=True, title="相关性热力图")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("需要至少2个数值字段才能生成热力图")
    
    # Tab 3: 统计分析
    with tab3:
        st.subheader("统计分析")
        
        # 选择分析类型
        analysis_type = st.radio(
            "选择分析类型",
            ["描述性统计", "分组统计", "相关性分析"],
            horizontal=True
        )
        
        if analysis_type == "描述性统计":
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                stats_df = df[numeric_cols].describe().T
                stats_df['缺失值'] = df[numeric_cols].isna().sum()
                st.dataframe(stats_df, use_container_width=True)
            else:
                st.warning("没有数值字段")
        
        elif analysis_type == "分组统计":
            categorical_cols = df.select_dtypes(include=['object']).columns
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    group_col = st.selectbox("分组字段", categorical_cols)
                with col2:
                    value_col = st.selectbox("数值字段", numeric_cols)
                
                agg_func = st.selectbox("聚合函数", ["mean", "sum", "count", "min", "max"])
                
                grouped = df.groupby(group_col)[value_col].agg(agg_func).reset_index()
                st.dataframe(grouped, use_container_width=True)
                
                # 可视化
                fig = px.bar(grouped, x=group_col, y=value_col, 
                           title=f"各{group_col}的{value_col} ({agg_func})")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("需要同时有分类字段和数值字段")
        
        elif analysis_type == "相关性分析":
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) >= 2:
                corr = df[numeric_cols].corr()
                
                # 找出强相关
                st.subheader("强相关性 (|r| > 0.5)")
                strong_corr = []
                for i in range(len(corr.columns)):
                    for j in range(i+1, len(corr.columns)):
                        if abs(corr.iloc[i, j]) > 0.5:
                            strong_corr.append({
                                '字段1': corr.columns[i],
                                '字段2': corr.columns[j],
                                '相关系数': corr.iloc[i, j]
                            })
                
                if strong_corr:
                    st.dataframe(pd.DataFrame(strong_corr))
                else:
                    st.info("未发现强相关性")
                
                # 显示完整相关矩阵
                with st.expander("查看完整相关矩阵"):
                    st.dataframe(corr)
            else:
                st.warning("需要至少2个数值字段")
    
    # Tab 4: 导出数据
    with tab4:
        st.subheader("导出处理后的数据")
        
        # 数据过滤（简单版）
        with st.expander("数据过滤（可选）"):
            filter_col = st.selectbox("选择过滤字段", df.columns)
            if filter_col:
                if df[filter_col].dtype in ['int64', 'float64']:
                    min_val = float(df[filter_col].min())
                    max_val = float(df[filter_col].max())
                    filter_range = st.slider(
                        "选择范围",
                        min_val, max_val,
                        (min_val, max_val)
                    )
                    filtered_df = df[(df[filter_col] >= filter_range[0]) & 
                                    (df[filter_col] <= filter_range[1])]
                else:
                    unique_vals = df[filter_col].unique()
                    selected_vals = st.multiselect("选择值", unique_vals)
                    if selected_vals:
                        filtered_df = df[df[filter_col].isin(selected_vals)]
                    else:
                        filtered_df = df
            else:
                filtered_df = df
        
        st.info(f"当前数据：{len(filtered_df)} 行")
        
        # 导出选项
        export_format = st.radio("导出格式", ["CSV", "Excel"])
        
        if st.button("📥 生成下载文件"):
            if export_format == "CSV":
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "点击下载 CSV",
                    csv,
                    "exported_data.csv",
                    "text/csv"
                )
            else:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name='Sheet1')
                st.download_button(
                    "点击下载 Excel",
                    output.getvalue(),
                    "exported_data.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

else:
    # 欢迎界面
    st.info("👈 请在左侧边栏上传数据文件开始分析")
    
    # 展示示例功能
    st.markdown("""
    ### ✨ 功能介绍
    
    - **数据预览**：快速查看数据概览和基本信息
    - **可视化分析**：支持多种图表类型
    - **统计分析**：描述性统计、分组统计、相关性分析
    - **数据导出**：过滤后导出CSV或Excel
    
    ### 🚀 使用步骤
    
    1. 点击左侧边栏上传文件
    2. 在标签页中选择分析功能
    3. 根据需要调整参数
    4. 导出分析结果
    
    ### 💡 支持的格式
    
    - CSV文件（.csv）
    - Excel文件（.xlsx, .xls）
    """)