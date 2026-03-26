Streamlit_DA/
│
├── app.py
│   └── 主程序入口
│       ├── main()                               # 程序主入口
│       ├── init_session_state()                 # 初始化会话状态
│       ├── init_managers()                      # 初始化管理器
│       ├── render_sidebar()                     # 渲染侧边栏
│       ├── render_file_uploader()               # 文件上传组件
│       ├── render_right_panel()                 # 右侧功能面板
│       ├── render_main_content()                # 主内容区
│       ├── render_welcome_page()                # 欢迎页面
│       ├── render_data_preview_page()           # 数据预览页面
│       ├── render_analysis_preview_page()       # 统计分析预览页面
│       ├── render_chart_preview_page()          # 图表预览页面
│       ├── render_ai_analysis_page()            # AI分析页面
│       └── render_settings_page()               # 设置页面
│
├── configs/
│   ├── announcements.json                       # 公告配置
│   └── site_config.json                         # 站点配置
│
├── components/
│   ├── analysis_options.py
│   │   ├── render_analysis_options_tab()        # 分析选项标签页主入口
│   │   ├── render_descriptive_stats_with_chart() # 数据概览
│   │   ├── render_correlation_with_heatmap()    # 相关性分析 + 热力图
│   │   ├── render_group_stats_with_chart()      # 分组统计 + 聚合图表
│   │   ├── render_time_series_with_chart()      # 时间序列分析 + 趋势图
│   │   ├── render_pivot_with_chart()            # 数据透视表 + 透视图
│   │   └── render_composite_pie_chart()         # 深度分析（支持下钻的多种图表）
│   │
│   ├── announcements.py
│   │   └── AnnouncementManager                  # 公告管理器
│   │
│   ├── data_processing.py
│   │   ├── render_data_processing_tab()         # 数据处理标签页主入口
│   │   ├── render_deduplicate_section()         # 去重功能
│   │   ├── render_replace_value_section()       # 替换值功能
│   │   ├── render_convert_type_section()        # 类型转换功能
│   │   ├── render_split_column_section()        # 分列功能
│   │   ├── render_merge_columns_section()       # 合并列功能
│   │   ├── render_rename_columns_section()      # 修改表头功能
│   │   ├── render_delete_columns_section()      # 删除列功能
│   │   ├── render_filter_section_in_tab()       # 筛选功能
│   │   ├── render_confirm_data_button()         # 数据确认按钮
│   │   ├── execute_data_operation()             # 统一数据操作执行
│   │   ├── undo_last_operation()                # 全局撤销
│   │   ├── redo_last_operation()                # 全局重做
│   │   ├── show_global_history()                # 显示操作历史
│   │   ├── undo_last_filter()                   # 撤销筛选
│   │   ├── reset_to_original()                  # 重置到原始数据
│   │   ├── show_filter_history()                # 显示筛选历史
│   │   ├── preview_unified_filter()             # 预览筛选结果
│   │   └── apply_unified_filter()               # 应用筛选条件
│   │
│   ├── footer.py
│   │   └── FooterManager                        # 底部管理器
│   │
│   ├── group_stats_chart.py
│   │   └── GroupStatsChart                      # 分组统计图表生成器
│   │
│   ├── history_manager.py
│   │   ├── HistoryManager                       # 历史记录管理器
│   │   └── LocalStorage                         # 本地存储管理
│   │
│   └── layout.py
│       └── LayoutManager                        # 布局管理器
│
├── utils/
│   ├── ai_analyzer.py
│   │   └── AIAnalyzer                           # AI分析器
│   │
│   ├── chart_factory.py
│   │   ├── BaseChart                            # 图表基类
│   │   ├── BarChart                             # 柱状图
│   │   ├── LineChart                            # 折线图
│   │   ├── PieChart                             # 饼图
│   │   ├── ScatterChart                         # 散点图
│   │   ├── BoxChart                             # 箱线图
│   │   ├── HistogramChart                       # 直方图
│   │   ├── HeatmapChart                         # 热力图
│   │   ├── GroupedBarChart                      # 分组柱状图
│   │   ├── StackedBarChart                      # 堆积柱状图
│   │   ├── HorizontalBarChart                   # 条形图
│   │   └── CompositePieChart                    # 复合饼图
│   │
│   ├── chart_generator.py
│   │   └── ChartGenerator                       # 图表生成器（统一入口）
│   │
│   ├── data_cleaner.py
│   │   └── DataCleaner                          # 数据清洗处理器
│   │
│   ├── data_filter.py
│   │   └── DataFilter                           # 数据筛选器
│   │
│   ├── depth_analysis.py
│   │   ├── DepthAnalysisEngine                  # 深度分析引擎
│   │   ├── ChartRenderer                        # 图表渲染器基类
│   │   ├── PieChartRenderer                     # 饼图渲染器
│   │   ├── BarChartRenderer                     # 柱状图渲染器
│   │   ├── HorizontalBarChartRenderer           # 条形图渲染器
│   │   └── LineChartRenderer                    # 折线图渲染器
│   │
│   ├── file_loader.py
│   │   └── FileLoader                           # 文件加载器
│   │
│   ├── logger.py
│   │   └── Logger                               # 日志记录器
│   │
│   ├── preview_manager.py
│   │   └── PreviewManager                       # 预览管理器
│   │
│   ├── stats_analyzer.py
│   │   └── StatsAnalyzer                        # 统计分析器
│   │
│   └── theme_manager.py
│       └── ThemeManager                         # 主题管理器
│
└── assets/
    └── style.css                                 # 自定义样式