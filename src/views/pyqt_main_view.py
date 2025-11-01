from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                           QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit, QMessageBox, 
                           QTabWidget, QGroupBox, QFormLayout, QHeaderView)
from PySide6.QtCore import Qt, QDate, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QBrush, QLinearGradient, QPainter
import datetime

# 创建渐变背景组件类
class GradientBackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 简化背景设置，避免paintEvent可能的问题
        self.setStyleSheet("background-color: #f0f5fa;")

class PyQtMainView(QMainWindow):
    def __init__(self, account_model, prediction_model):
        super().__init__()
        self.account_model = account_model
        self.prediction_model = prediction_model
        
        # 设置窗口标题和大小
        self.setWindowTitle("智能记账本")
        self.setGeometry(100, 100, 1000, 700)
        
        # 设置窗口图标（可以使用内置图标或自定义图标）
        # self.setWindowIcon(QIcon("path/to/icon.png"))
        
        # 应用全局样式表
        self.apply_styles()
        
        # 创建中心部件
        central_widget = GradientBackgroundWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建标题标签
        title_label = QLabel("智能记账系统")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("title_label")
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.setObjectName("main_tab_widget")
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_records_tab()
        self.create_add_record_tab()
        self.create_analysis_tab()
        self.create_prediction_tab()
        
        # 创建状态栏
        # 设置状态栏字体
        status_font = QFont()
        status_font.setPointSize(10)
        self.statusBar().setFont(status_font)
        self.statusBar().setObjectName("status_bar")
        self.statusBar().showMessage("就绪")
        
        # 添加窗口出现动画
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(800)
        # 移除动画效果，简化实现
        # self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        
        # 初始加载数据
        # 创建初始化数据加载的延迟调用
        QTimer.singleShot(100, self.load_records)
    
    def apply_styles(self):
        """应用全局样式表"""
        style_sheet = """
        /* 主窗口样式 */
        QMainWindow {
            background-color: #f5f5f5;
            border-radius: 8px;
        }
        
        /* 标题样式 */
        QLabel#title_label {
            color: #1976d2;
            margin-bottom: 10px;
        }
        
        /* 标签页样式 */
        QTabWidget#main_tab_widget::pane {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
        }
        
        QTabBar::tab {
            background-color: #f0f0f0;
            color: #666666;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 14px;
            font-weight: 500;
        }
        
        QTabBar::tab:hover {
            background-color: #e8e8e8;
            color: #333333;
        }
        
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom-color: #ffffff;
            color: #1976d2;
            border-bottom: 2px solid #1976d2;
        }
        
        /* 按钮样式 */
        QPushButton {
            background-color: #4caf50;
            color: black;
            border: 1px solid #1976d2;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #1976d2;
        }
        
        QPushButton:pressed {
            background-color: #1565c0;
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        
        /* 删除按钮特殊样式 */
        QPushButton#delete_button {
            background-color: #e53935;
            color: black;
            border: 1px solid #c62828;
        }
        
        QPushButton#delete_button:hover {
            background-color: #f44336;
        }
        
        QPushButton#delete_button:pressed {
            background-color: #c62828;
        }
        
        /* 表格样式 */
        QTableWidget {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            alternate-background-color: #f9f9f9;
            gridline-color: #e0e0e0;
            font-size: 14px;
        }
        
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        QTableWidget::item:selected {
            background-color: #e3f2fd;
            color: #1565c0;
            border-bottom: 1px solid #1976d2;
        }
        
        QHeaderView::section {
            background-color: #f5f5f5;
            padding: 10px;
            border: 1px solid #e0e0e0;
            font-weight: 600;
            color: #333333;
        }
        
        QHeaderView::section:hover {
            background-color: #eeeeee;
        }
        
        /* 输入框样式 */
        QLineEdit, QComboBox, QDateEdit {
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 8px 12px;
            background-color: #ffffff;
            font-size: 14px;
        }
        
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
            border-color: #1e88e5;
            background-color: #f5f7fa;
        }
        
        /* 文本编辑框样式 */
        QTextEdit {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 12px;
            background-color: #ffffff;
            font-size: 14px;
        }
        
        QTextEdit:focus {
            border-color: #1e88e5;
        }
        
        /* 分组框样式 */
        QGroupBox {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 15px;
            padding: 15px;
            background-color: #fafafa;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px 0 10px;
            background-color: transparent;
            font-weight: 600;
            color: #333333;
        }
        
        /* 状态栏样式 */
        QStatusBar#status_bar {
            background-color: #f5f5f5;
            border-top: 1px solid #e0e0e0;
            padding: 5px 10px;
            color: #666666;
        }
        
        /* 统计标签样式 */
        QLabel#stat_label {
            font-size: 14px;
            font-weight: 500;
            margin: 0 15px;
        }
        
        /* 工具提示样式 */
        QToolTip {
            background-color: #333333;
            color: white;
            border-radius: 4px;
            padding: 8px;
        }
        """
        
        self.setStyleSheet(style_sheet)
    
    def create_records_tab(self):
        """创建记录列表标签页"""
        records_widget = GradientBackgroundWidget()
        records_layout = QVBoxLayout(records_widget)
        records_layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建按钮布局和统计信息
        top_layout = QVBoxLayout()
        
        # 统计信息布局
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        stats_layout.setContentsMargins(0, 0, 0, 15)
        
        self.income_label = QLabel("总收入: ¥0.00")
        self.income_label.setObjectName("stat_label")
        self.income_label.setStyleSheet("color: #4caf50; font-weight: 600;")
        
        self.expense_label = QLabel("总支出: ¥0.00")
        self.expense_label.setObjectName("stat_label")
        self.expense_label.setStyleSheet("color: #f44336; font-weight: 600;")
        
        self.balance_label = QLabel("余额: ¥0.00")
        self.balance_label.setObjectName("stat_label")
        self.balance_label.setStyleSheet("color: #1976d2; font-weight: 600;")
        
        stats_layout.addStretch()
        stats_layout.addWidget(self.income_label)
        stats_layout.addWidget(self.expense_label)
        stats_layout.addWidget(self.balance_label)
        stats_layout.addStretch()
        
        top_layout.addLayout(stats_layout)
        
        # 按钮布局
        buttons_layout = QHBoxLayout()
        
        # 查询布局
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索描述:")
        search_label.setMinimumWidth(80)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索...")
        self.search_input.setMinimumHeight(36)
        self.search_input.setMinimumWidth(200)
        
        self.search_button = QPushButton("搜索")
        self.search_button.setMinimumHeight(36)
        self.search_button.clicked.connect(self.search_records)
        
        self.reset_button = QPushButton("重置")
        self.reset_button.setMinimumHeight(36)
        self.reset_button.clicked.connect(self.reset_query)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.reset_button)
        
        # 操作按钮
        self.refresh_button = QPushButton("刷新数据")
        self.refresh_button.setObjectName("refresh_button")
        self.refresh_button.setMinimumHeight(36)
        self.refresh_button.clicked.connect(self.load_records)
        
        self.delete_button = QPushButton("删除选中记录")
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setMinimumHeight(36)
        self.delete_button.clicked.connect(self.delete_selected_record)
        
        buttons_layout.addLayout(search_layout)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.setSpacing(10)
        
        top_layout.addLayout(buttons_layout)
        records_layout.addLayout(top_layout)
        records_layout.addSpacing(10)
        
        # 创建表格
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels(["ID", "金额", "类型", "日期", "描述", "创建时间"])
        self.records_table.setAlternatingRowColors(True)
        self.records_table.setSortingEnabled(True)
        self.records_table.horizontalHeader().setHighlightSections(False)
        self.records_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.records_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.records_table.setMinimumHeight(400)
        
        # 设置表格列宽
        header = self.records_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        # 设置表格行高
        self.records_table.verticalHeader().setDefaultSectionSize(36)
        
        records_layout.addWidget(self.records_table)
        
        self.tab_widget.addTab(records_widget, "记账记录")
    
    def reset_query(self):
        """重置查询条件"""
        self.search_input.clear()
        self.load_records()
    
    def search_records(self):
        """根据关键词搜索记录"""
        keyword = self.search_input.text()
        self.load_records(search_keyword=keyword)
        
        # 更新状态信息
        if keyword:
            self.statusBar().showMessage(f"已搜索关键词: '{keyword}'")
        else:
            self.statusBar().showMessage("已加载所有记录")
    
    def create_add_record_tab(self):
        """创建添加记录标签页"""
        add_widget = GradientBackgroundWidget()
        add_layout = QVBoxLayout(add_widget)
        add_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建表单布局
        form_group = QGroupBox("添加新记录")
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(20)
        form_layout.setHorizontalSpacing(20)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # 设置表单字段大小
        for field_name in ["金额:", "类型:", "日期:", "描述:"]:
            label = QLabel(field_name)
            font = label.font()
            font.setBold(True)
            font.setPointSize(14)
            label.setFont(font)
            form_layout.setWidget(form_layout.rowCount(), QFormLayout.ItemRole.LabelRole, label)
        
        # 金额输入
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("请输入金额")
        self.amount_input.setMinimumHeight(40)
        self.amount_input.setObjectName("amount_input")
        self.amount_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.amount_input)
        
        # 类型选择
        self.type_combo = QComboBox()
        self.type_combo.addItems(["收入", "支出"])
        self.type_combo.setMinimumHeight(40)
        self.type_combo.setMinimumWidth(200)
        form_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.type_combo)
        
        # 日期选择
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumHeight(40)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        # 简化设置，避免枚举错误
        # self.date_edit.calendarWidget().setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        form_layout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.date_edit)
        
        # 描述输入
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("请输入描述")
        self.description_input.setMinimumHeight(40)
        form_layout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.description_input)
        
        form_group.setLayout(form_layout)
        form_group.setMinimumWidth(500)
        
        # 居中表单
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(form_group)
        center_layout.addStretch()
        
        add_layout.addLayout(center_layout)
        add_layout.addSpacing(30)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.add_button = QPushButton("添加记录")
        self.add_button.setMinimumHeight(48)
        self.add_button.setMinimumWidth(150)
        self.add_button.setObjectName("add_button")
        self.add_button.clicked.connect(self.add_new_record)
        
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()
        
        add_layout.addLayout(button_layout)
        add_layout.addStretch()
        
        self.tab_widget.addTab(add_widget, "添加记录")
    
    def create_analysis_tab(self):
        """创建分析标签页"""
        analysis_widget = GradientBackgroundWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        analysis_layout.setContentsMargins(20, 20, 20, 20)
        analysis_layout.setSpacing(20)
        
        # 创建摘要标签
        summary_label = QLabel("本功能将根据您的收支记录生成详细的经济分析报告，帮助您了解个人消费习惯和经济状况。")
        summary_label.setWordWrap(True)
        summary_label.setObjectName("summary_label")
        summary_label.setStyleSheet("color: #666666; font-style: italic;")
        analysis_layout.addWidget(summary_label)
        
        # 创建分析按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.analysis_button = QPushButton("生成经济分析")
        self.analysis_button.setMinimumHeight(48)
        self.analysis_button.setMinimumWidth(180)
        self.analysis_button.setObjectName("analysis_button")
        self.analysis_button.clicked.connect(self.generate_analysis)
        
        button_layout.addWidget(self.analysis_button)
        button_layout.addStretch()
        
        analysis_layout.addLayout(button_layout)
        
        # 创建分析结果区域
        analysis_group = QGroupBox("经济分析报告")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(15, 15, 15, 15)
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setPlainText("点击上方按钮生成经济分析报告...")
        self.analysis_text.setObjectName("analysis_text")
        self.analysis_text.setMinimumHeight(400)
        # 使用默认换行模式
        # self.analysis_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.analysis_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 设置字体 - 使用系统默认等宽字体
        font = QFont()
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(11)
        # 移除可能有问题的字体设置
        # font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.analysis_text.setFont(font)
        
        group_layout.addWidget(self.analysis_text)
        analysis_group.setLayout(group_layout)
        
        analysis_layout.addWidget(analysis_group)
        
        self.tab_widget.addTab(analysis_widget, "经济分析")
    
    def create_prediction_tab(self):
        """创建预测标签页"""
        prediction_widget = GradientBackgroundWidget()
        prediction_layout = QVBoxLayout(prediction_widget)
        prediction_layout.setContentsMargins(20, 20, 20, 20)
        prediction_layout.setSpacing(20)
        
        # 创建摘要标签
        summary_label = QLabel("基于历史收支数据，系统可以预测未来一段时间的收支趋势，帮助您进行财务规划。")
        summary_label.setWordWrap(True)
        summary_label.setObjectName("summary_label")
        summary_label.setStyleSheet("color: #666666; font-style: italic;")
        prediction_layout.addWidget(summary_label)
        
        # 创建时间区间选择区域
        time_range_group = QGroupBox("选择历史数据时间区间")
        time_range_layout = QFormLayout()
        time_range_layout.setVerticalSpacing(20)
        time_range_layout.setHorizontalSpacing(20)
        time_range_layout.setContentsMargins(20, 20, 20, 20)
        
        # 设置标签字体
        for field_name in ["开始日期:", "结束日期:", "预测天数:"]:
            label = QLabel(field_name)
            font = label.font()
            font.setBold(True)
            font.setPointSize(14)
            label.setFont(font)
            time_range_layout.setWidget(time_range_layout.rowCount(), QFormLayout.ItemRole.LabelRole, label)
        
        # 开始日期
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setMinimumHeight(40)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setCalendarPopup(True)
        # 简化设置，避免枚举错误
        # self.start_date_edit.calendarWidget().setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        # 设置默认开始日期为一个月前
        one_month_ago = QDate.currentDate().addMonths(-1)
        self.start_date_edit.setDate(one_month_ago)
        time_range_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.start_date_edit)
        
        # 结束日期
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setMinimumHeight(40)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        time_range_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.end_date_edit)
        
        # 预测天数
        self.prediction_days_input = QLineEdit("30")
        self.prediction_days_input.setMinimumHeight(40)
        self.prediction_days_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_range_layout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.prediction_days_input)
        
        time_range_group.setLayout(time_range_layout)
        prediction_layout.addWidget(time_range_group)
        
        # 创建预测按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.prediction_button = QPushButton("生成预测")
        self.prediction_button.setMinimumHeight(48)
        self.prediction_button.setMinimumWidth(180)
        self.prediction_button.setObjectName("prediction_button")
        self.prediction_button.clicked.connect(self.generate_prediction)
        
        button_layout.addWidget(self.prediction_button)
        button_layout.addStretch()
        
        prediction_layout.addLayout(button_layout)
        
        # 创建预测结果区域
        prediction_group = QGroupBox("收支预测结果")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(15, 15, 15, 15)
        
        self.prediction_text = QTextEdit()
        self.prediction_text.setReadOnly(True)
        self.prediction_text.setPlainText("选择时间区间并点击上方按钮生成预测...")
        self.prediction_text.setObjectName("prediction_text")
        self.prediction_text.setMinimumHeight(300)
        # 使用默认换行模式
        # self.prediction_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # 设置字体 - 使用系统默认等宽字体
        font = QFont()
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(11)
        # 移除可能有问题的字体设置
        # font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.prediction_text.setFont(font)
        
        group_layout.addWidget(self.prediction_text)
        prediction_group.setLayout(group_layout)
        
        prediction_layout.addWidget(prediction_group)
        
        self.tab_widget.addTab(prediction_widget, "收支预测")
    
    def load_records(self, search_keyword=None):
        """加载记账记录到表格，支持搜索关键词过滤"""
        try:
            # 显示加载中状态
            self.statusBar().showMessage("正在加载记录...")
            
            records = self.account_model.get_all_records()
            
            # 如果提供了搜索关键词，进行过滤
            if search_keyword:
                filtered_records = []
                keyword = search_keyword.lower().strip()
                for record in records:
                    # 在描述、金额、日期等字段中搜索关键词
                    if (keyword in str(record['description']).lower() or
                        keyword in str(record['amount']) or
                        keyword in record['date'] or
                        keyword in record['created_at'] or
                        (record['type'] == 'income' and '收入' in keyword) or
                        (record['type'] == 'expense' and '支出' in keyword)):
                        filtered_records.append(record)
                records = filtered_records
            
            # 清空表格
            self.records_table.setRowCount(0)
            
            # 添加数据并计算统计信息
            total_income = 0.0
            total_expense = 0.0
            
            if not records:
                self.statusBar().showMessage("暂无记录")
                # 更新统计信息
                self.income_label.setText(f"总收入: ¥{total_income:.2f}")
                self.expense_label.setText(f"总支出: ¥{total_expense:.2f}")
                self.balance_label.setText(f"余额: ¥0.00")
                self.balance_label.setStyleSheet("color: #1976d2;")
                return
            
            for record in records:
                row_position = self.records_table.rowCount()
                self.records_table.insertRow(row_position)
                
                # 类型转换为中文
                type_text = "收入" if record['type'] == 'income' else "支出"
                
                # 设置行数据
                id_item = QTableWidgetItem(str(record['id']))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.records_table.setItem(row_position, 0, id_item)
                
                # 为金额设置不同的颜色
                amount_item = QTableWidgetItem(f"¥{record['amount']:.2f}")
                if type_text == '收入':
                    amount_item.setForeground(QColor(76, 175, 80))  # 绿色
                    total_income += float(record['amount'])
                else:
                    amount_item.setForeground(QColor(244, 67, 54))  # 红色
                    total_expense += float(record['amount'])
                
                amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.records_table.setItem(row_position, 1, amount_item)
                
                # 为类型设置不同的颜色和背景
                type_item = QTableWidgetItem(type_text)
                if type_text == '收入':
                    type_item.setForeground(QColor(76, 175, 80))
                    type_item.setBackground(QColor(241, 248, 233))
                else:
                    type_item.setForeground(QColor(244, 67, 54))
                    type_item.setBackground(QColor(253, 236, 234))
                type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.records_table.setItem(row_position, 2, type_item)
                
                # 设置其他列
                date_item = QTableWidgetItem(record['date'])
                date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.records_table.setItem(row_position, 3, date_item)
                
                desc_item = QTableWidgetItem(record['description'])
                desc_item.setToolTip(record['description'])  # 添加工具提示
                self.records_table.setItem(row_position, 4, desc_item)
                
                time_item = QTableWidgetItem(record['created_at'])
                time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.records_table.setItem(row_position, 5, time_item)
            
            # 更新统计信息
            balance = total_income - total_expense
            self.income_label.setText(f"总收入: ¥{total_income:,.2f}")
            self.expense_label.setText(f"总支出: ¥{total_expense:,.2f}")
            self.balance_label.setText(f"余额: ¥{balance:,.2f}")
            
            # 根据余额设置不同颜色和样式
            if balance >= 0:
                self.balance_label.setStyleSheet("color: #1976d2; font-weight: 600; font-size: 16px;")
            else:
                self.balance_label.setStyleSheet("color: #f44336; font-weight: 600; font-size: 16px;")
            
            self.statusBar().showMessage(f"已加载 {len(records)} 条记录")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载记录失败: {str(e)}")
            self.statusBar().showMessage("加载记录失败")
    
    def add_new_record(self):
        """添加新记录"""
        try:
            # 获取输入值
            amount_text = self.amount_input.text()
            if not amount_text:
                QMessageBox.warning(self, "输入错误", "请输入金额")
                self.amount_input.setFocus()
                return
            
            amount = float(amount_text)
            if amount <= 0:
                QMessageBox.warning(self, "输入错误", "金额必须大于0")
                self.amount_input.setFocus()
                return
            
            # 获取类型
            type_index = self.type_combo.currentIndex()
            record_type = "income" if type_index == 0 else "expense"
            
            # 获取日期
            date = self.date_edit.date().toString("yyyy-MM-dd")
            
            # 获取描述
            description = self.description_input.text().strip()
            if not description:
                QMessageBox.warning(self, "输入错误", "请输入描述")
                self.description_input.setFocus()
                return
            
            # 添加按钮动画反馈
            self.add_button.setEnabled(False)
            self.add_button.setText("添加中...")
            
            # 添加记录
            success, _ = self.account_model.add_record(amount, record_type, date, description)
            
            if success:
                # 成功动画效果
                self.add_button.setText("添加成功!")
                QMessageBox.information(self, "成功", "记录添加成功")
                
                # 清空输入
                self.amount_input.clear()
                self.description_input.clear()
                # 刷新记录列表
                self.load_records()
                # 切换到记录标签页
                self.tab_widget.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "失败", "记录添加失败")
                
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的金额")
        finally:
            # 恢复按钮状态
            self.add_button.setEnabled(True)
            self.add_button.setText("添加记录")
            self.amount_input.setFocus()
    
    def delete_selected_record(self):
        """删除选中的记录"""
        selected_row = self.records_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的记录")
            return
        
        # 获取记录ID
        item = self.records_table.item(selected_row, 0)
        if item is not None:
            record_id = item.text()
            
            # 确认删除
            reply = QMessageBox.question(self, "确认", f"确定要删除ID为 {record_id} 的记录吗？", 
                                        QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.account_model.delete_record(record_id)
                    self.records_table.removeRow(selected_row)
                    QMessageBox.information(self, "成功", "记录已成功删除")
                    self.statusBar().showMessage("记录已成功删除")
                    # 重新加载数据以更新统计信息
                    self.load_records()
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"删除记录失败: {str(e)}")
                    self.statusBar().showMessage("删除记录失败")
    
    def generate_analysis(self):
        """生成经济分析报告"""
        profile = self.prediction_model.get_economic_profile()
        
        if not profile:
            QMessageBox.warning(self, "提示", "暂无足够数据生成经济画像，请先添加更多收支记录")
            return
        
        # 格式化分析结果
        indicators = profile['indicators']
        analysis_text = "===== 经济水平画像 =====\n\n"
        analysis_text += f"恩格尔系数: {indicators['engel_coefficient']:.2%}\n"
        analysis_text += f"平均消费倾向 (APC): {indicators['avg_propensity_consumption']:.2%}\n"
        analysis_text += f"边际消费倾向 (MPC): {indicators['marginal_propensity_consumption']:.2%}\n\n"
        
        analysis_text += "===== 分析报告 =====\n\n"
        for i, text in enumerate(profile['analysis'], 1):
            analysis_text += f"{i}. {text}\n"
        
        # 显示结果
        self.analysis_text.setPlainText(analysis_text)
    
    def generate_prediction(self):
        """根据时间区间生成收支预测"""
        try:
            # 获取时间区间
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            
            # 验证日期顺序
            if start_date > end_date:
                QMessageBox.warning(self, "日期错误", "开始日期不能晚于结束日期")
                return
            
            # 获取预测天数
            days_ahead = int(self.prediction_days_input.text())
            if days_ahead <= 0:
                QMessageBox.warning(self, "输入错误", "预测天数必须大于0")
                return
            
            # 生成预测
            prediction = self.prediction_model.predict_future_by_time_range(start_date, end_date, days_ahead)
            
            if not prediction:
                QMessageBox.warning(self, "提示", f"在 {start_date} 到 {end_date} 期间没有足够的收支数据进行预测")
                return
            
            # 格式化预测结果
            prediction_text = f"===== 基于 {start_date} 到 {end_date} 的收支预测 =====\n\n"
            prediction_text += f"区间内平均收入: {prediction['period_avg_income']:.2f} 元/笔\n"
            prediction_text += f"区间内平均支出: {prediction['period_avg_expense']:.2f} 元/笔\n"
            prediction_text += f"区间内日均收入: {prediction['period_daily_avg_income']:.2f} 元/天\n"
            prediction_text += f"区间内日均支出: {prediction['period_daily_avg_expense']:.2f} 元/天\n\n"
            
            # 计算总预测
            total_predicted_income = sum(prediction['income_prediction'])
            total_predicted_expense = sum(prediction['expense_prediction'])
            total_predicted_net = total_predicted_income - total_predicted_expense
            
            prediction_text += f"===== 未来 {days_ahead} 天预测 =====\n\n"
            prediction_text += f"预计总收入: {total_predicted_income:.2f} 元\n"
            prediction_text += f"预计总支出: {total_predicted_expense:.2f} 元\n"
            prediction_text += f"预计净收支: {total_predicted_net:.2f} 元\n\n"
            
            # 添加建议
            if total_predicted_net < 0:
                prediction_text += "建议: 预计未来将出现收支不平衡，建议适当控制支出。\n"
            else:
                prediction_text += "建议: 预计未来收支状况良好，可以考虑适当的投资或储蓄计划。\n"
            
            # 显示结果
            self.prediction_text.setPlainText(prediction_text)
            
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的预测天数")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"生成预测时出错: {str(e)}")