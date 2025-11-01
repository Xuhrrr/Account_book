import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class MainView(tk.Tk):
    def __init__(self, account_model, prediction_model):
        super().__init__()
        self.account_model = account_model
        self.prediction_model = prediction_model
        
        # 设置窗口标题和大小
        self.title("智能记账本")
        self.geometry("800x600")
        self['bg'] = "#f0f0f0"
        
        # 设置窗口图标（可选）
        # self.iconbitmap("icon.ico")
        
        # 创建主界面
        self.create_main_frame()
    
    def create_main_frame(self):
        """创建主界面"""
        # 清空当前所有窗口组件
        for widget in self.winfo_children():
            widget.destroy()
        
        # 创建背景海报效果的框架
        poster_frame = tk.Frame(self, bg="#3498db", height=200)
        poster_frame.pack(fill=tk.X)
        
        # 海报标题
        title_label = tk.Label(poster_frame, text="智能记账本", font=("SimHei", 36, "bold"), 
                              bg="#3498db", fg="white")
        title_label.pack(pady=30)
        
        subtitle_label = tk.Label(poster_frame, text="记录生活，掌控未来", font=("SimHei", 14),
                                 bg="#3498db", fg="white")
        subtitle_label.pack()
        
        # 创建功能按钮框架
        button_frame = tk.Frame(self, bg="#f0f0f0", padx=50, pady=50)
        button_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建三个主要功能按钮
        button_width = 20
        button_height = 3
        button_font = ("SimHei", 14)
        
        # 收支编辑按钮
        edit_button = tk.Button(button_frame, text="收支编辑", font=button_font,
                               width=button_width, height=button_height,
                               bg="#2ecc71", fg="white",
                               command=self.open_edit_view)
        edit_button.pack(pady=20)
        
        # 收支预测按钮
        predict_button = tk.Button(button_frame, text="收支预测", font=button_font,
                                  width=button_width, height=button_height,
                                  bg="#e74c3c", fg="white",
                                  command=self.open_predict_view)
        predict_button.pack(pady=20)
        
        # 经济画像按钮
        profile_button = tk.Button(button_frame, text="经济画像", font=button_font,
                                  width=button_width, height=button_height,
                                  bg="#9b59b6", fg="white",
                                  command=self.open_profile_view)
        profile_button.pack(pady=20)
    
    def open_edit_view(self):
        """打开收支编辑界面"""
        EditView(self, self.account_model)
    
    def open_predict_view(self):
        """打开收支预测界面"""
        PredictView(self, self.account_model, self.prediction_model)
    
    def open_profile_view(self):
        """打开经济画像界面"""
        ProfileView(self, self.account_model, self.prediction_model)

class EditView(tk.Toplevel):
    def __init__(self, parent, account_model):
        super().__init__(parent)
        self.account_model = account_model
        self.transient(parent)
        self.title("收支编辑")
        self.geometry("700x500")
        self['bg'] = "#f0f0f0"
        
        # 创建编辑框架
        self.create_edit_frame()
        # 显示当前记录
        self.show_records()
    
    def create_edit_frame(self):
        """创建编辑框架"""
        # 操作选择框架
        action_frame = tk.Frame(self, bg="#f0f0f0", pady=20)
        action_frame.pack(fill=tk.X, padx=20)
        
        # 新增按钮
        add_button = tk.Button(action_frame, text="新增记录", font=("SimHei", 12),
                              bg="#2ecc71", fg="white", width=15,
                              command=self.show_add_dialog)
        add_button.pack(side=tk.LEFT, padx=10)
        
        # 删除按钮
        delete_button = tk.Button(action_frame, text="删除记录", font=("SimHei", 12),
                                bg="#e74c3c", fg="white", width=15,
                                command=self.show_delete_dialog)
        delete_button.pack(side=tk.LEFT, padx=10)
        
        # 提示标签
        tip_label = tk.Label(action_frame, text="请选择操作类型", font=("SimHei", 10),
                           bg="#f0f0f0", fg="#7f8c8d")
        tip_label.pack(side=tk.LEFT, padx=10)
    
    def show_records(self):
        """显示所有记录"""
        # 创建记录显示框架
        records_frame = tk.Frame(self, bg="#f0f0f0")
        records_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建表格
        columns = ("id", "amount", "type", "date", "description", "created_at")
        tree = ttk.Treeview(records_frame, columns=columns, show="headings")
        
        # 设置列标题
        tree.heading("id", text="ID")
        tree.heading("amount", text="金额")
        tree.heading("type", text="类型")
        tree.heading("date", text="日期")
        tree.heading("description", text="描述")
        tree.heading("created_at", text="创建时间")
        
        # 设置列宽
        tree.column("id", width=50)
        tree.column("amount", width=100)
        tree.column("type", width=80)
        tree.column("date", width=100)
        tree.column("description", width=200)
        tree.column("created_at", width=120)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(records_frame, orient=tk.VERTICAL, command=tree.yview)
        tree['yscrollcommand'] = scrollbar.set
        
        # 填充数据
        records = self.account_model.get_all_records()
        for record in records:
            # 转换类型显示
            type_text = "收入" if record['type'] == 'income' else "支出"
            tree.insert("", tk.END, values=(
                record['id'],
                record['amount'],
                type_text,
                record['date'],
                record['description'],
                record['created_at']
            ))
        
        # 布局
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_add_dialog(self):
        """显示新增记录对话框"""
        dialog = AddRecordDialog(self, self.account_model)
        if dialog.result:
            # 重新显示记录
            self.show_records()
    
    def show_delete_dialog(self):
        """显示删除记录对话框"""
        dialog = DeleteRecordDialog(self, self.account_model)
        if dialog.result:
            # 重新显示记录
            self.show_records()

class AddRecordDialog(tk.Toplevel):
    def __init__(self, parent, account_model):
        super().__init__(parent)
        self.account_model = account_model
        self.result = False
        self.transient(parent)
        self.title("新增记录")
        self.geometry("400x300")
        self['bg'] = "#f0f0f0"
        
        self.create_widgets()
    
    def create_widgets(self):
        # 金额
        tk.Label(self, text="金额:", bg="#f0f0f0").grid(row=0, column=0, padx=20, pady=10, sticky=tk.E)
        self.amount_var = tk.StringVar()
        tk.Entry(self, textvariable=self.amount_var, width=30).grid(row=0, column=1, padx=20, pady=10)
        
        # 类型
        tk.Label(self, text="类型:", bg="#f0f0f0").grid(row=1, column=0, padx=20, pady=10, sticky=tk.E)
        self.type_var = tk.StringVar(value="income")
        tk.Radiobutton(self, text="收入", variable=self.type_var, value="income", bg="#f0f0f0").grid(row=1, column=1, sticky=tk.W)
        tk.Radiobutton(self, text="支出", variable=self.type_var, value="expense", bg="#f0f0f0").grid(row=1, column=1, sticky=tk.E)
        
        # 日期
        tk.Label(self, text="日期:", bg="#f0f0f0").grid(row=2, column=0, padx=20, pady=10, sticky=tk.E)
        self.date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(self, textvariable=self.date_var, width=30).grid(row=2, column=1, padx=20, pady=10)
        
        # 描述
        tk.Label(self, text="描述:", bg="#f0f0f0").grid(row=3, column=0, padx=20, pady=10, sticky=tk.NE)
        self.description_var = tk.Text(self, width=23, height=3)
        self.description_var.grid(row=3, column=1, padx=20, pady=10)
        
        # 按钮
        button_frame = tk.Frame(self, bg="#f0f0f0")
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="确定", command=self.save_record).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=10)
    
    def save_record(self):
        """保存记录"""
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showerror("错误", "金额必须大于0")
                return
            
            record_type = self.type_var.get()
            date = self.date_var.get()
            description = self.description_var.get("1.0", tk.END).strip()
            
            # 验证日期格式
            try:
                datetime.datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("错误", "日期格式不正确，请使用YYYY-MM-DD格式")
                return
            
            # 保存记录
            success, _ = self.account_model.add_record(amount, record_type, date, description)
            
            if success:
                messagebox.showinfo("成功", "记录添加成功")
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("错误", "记录添加失败")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的金额")

class DeleteRecordDialog(tk.Toplevel):
    def __init__(self, parent, account_model):
        super().__init__(parent)
        self.account_model = account_model
        self.result = False
        self.transient(parent)
        self.title("删除记录")
        self.geometry("400x250")
        self['bg'] = "#f0f0f0"
        
        self.create_widgets()
    
    def create_widgets(self):
        # ID
        tk.Label(self, text="记录ID:", bg="#f0f0f0").grid(row=0, column=0, padx=20, pady=10, sticky=tk.E)
        self.id_var = tk.StringVar()
        tk.Entry(self, textvariable=self.id_var, width=30).grid(row=0, column=1, padx=20, pady=10)
        
        # 删除原因
        tk.Label(self, text="删除原因:", bg="#f0f0f0").grid(row=1, column=0, padx=20, pady=10, sticky=tk.NE)
        self.reason_var = tk.Text(self, width=23, height=3)
        self.reason_var.grid(row=1, column=1, padx=20, pady=10)
        
        # 按钮
        button_frame = tk.Frame(self, bg="#f0f0f0")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="删除", bg="#e74c3c", fg="white", command=self.delete_record).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=10)
    
    def delete_record(self):
        """删除记录"""
        try:
            record_id = int(self.id_var.get())
            reason = self.reason_var.get("1.0", tk.END).strip()
            
            success, _ = self.account_model.delete_record(record_id, reason)
            
            if success:
                messagebox.showinfo("成功", "记录删除成功")
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("错误", "找不到指定的记录ID")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的记录ID")

class PredictView(tk.Toplevel):
    def __init__(self, parent, account_model, prediction_model):
        super().__init__(parent)
        self.account_model = account_model
        self.prediction_model = prediction_model
        self.transient(parent)
        self.title("收支预测")
        self.geometry("800x600")
        self['bg'] = "#f0f0f0"
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建预测界面组件"""
        # 日期范围选择框架
        date_frame = tk.Frame(self, bg="#f0f0f0", pady=20)
        date_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(date_frame, text="开始日期:", bg="#f0f0f0").grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)
        self.start_date_var = tk.StringVar()
        tk.Entry(date_frame, textvariable=self.start_date_var, width=20).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(date_frame, text="结束日期:", bg="#f0f0f0").grid(row=0, column=2, padx=10, pady=10, sticky=tk.E)
        self.end_date_var = tk.StringVar()
        tk.Entry(date_frame, textvariable=self.end_date_var, width=20).grid(row=0, column=3, padx=10, pady=10)
        
        tk.Button(date_frame, text="开始预测", command=self.run_prediction).grid(row=0, column=4, padx=10, pady=10)
        
        # 预测结果框架
        self.result_frame = tk.Frame(self, bg="#f0f0f0")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 初始提示
        tk.Label(self.result_frame, text="请点击开始预测按钮生成预测结果", font=("SimHei", 12),
                bg="#f0f0f0", fg="#7f8c8d").pack(pady=50)
    
    def run_prediction(self):
        """运行预测"""
        # 获取日期范围
        start_date = self.start_date_var.get() if self.start_date_var.get() else None
        end_date = self.end_date_var.get() if self.end_date_var.get() else None
        
        # 过滤记录
        records = self.account_model.get_records_by_date_range(start_date, end_date)
        
        if not records:
            messagebox.showinfo("提示", "在指定日期范围内没有记录，请添加更多数据")
            return
        
        # 清空结果框架
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        # 运行预测
        prediction = self.prediction_model.predict_future(days_ahead=30, records=records)
        
        if not prediction:
            messagebox.showinfo("提示", "数据量不足，无法进行预测")
            return
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        
        # 预测未来30天
        future_dates = [(datetime.datetime.now() + datetime.timedelta(days=i)).strftime("%m-%d") for i in range(30)]
        
        # 收入预测图
        ax1.plot(future_dates, prediction['income_prediction'], 'b-', label='预测收入')
        ax1.set_title('未来30天收入预测')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('金额')
        ax1.grid(True)
        ax1.legend()
        ax1.tick_params(axis='x', rotation=45)
        
        # 支出预测图
        ax2.plot(future_dates, prediction['expense_prediction'], 'r-', label='预测支出')
        ax2.set_title('未来30天支出预测')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('金额')
        ax2.grid(True)
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # 显示图表
        canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 显示汇总信息
        summary_frame = tk.Frame(self.result_frame, bg="#f0f0f0")
        summary_frame.pack(fill=tk.X, pady=20)
        
        total_income = sum(prediction['income_prediction'])
        total_expense = sum(prediction['expense_prediction'])
        net_amount = total_income - total_expense
        
        tk.Label(summary_frame, text=f"预测总收入: ¥{total_income:.2f}", font=("SimHei", 12),
                bg="#f0f0f0", fg="blue").pack(side=tk.LEFT, padx=20)
        tk.Label(summary_frame, text=f"预测总支出: ¥{total_expense:.2f}", font=("SimHei", 12),
                bg="#f0f0f0", fg="red").pack(side=tk.LEFT, padx=20)
        tk.Label(summary_frame, text=f"预测净余额: ¥{net_amount:.2f}", font=("SimHei", 12),
                bg="#f0f0f0", fg="green" if net_amount >= 0 else "red").pack(side=tk.LEFT, padx=20)

class ProfileView(tk.Toplevel):
    def __init__(self, parent, account_model, prediction_model):
        super().__init__(parent)
        self.account_model = account_model
        self.prediction_model = prediction_model
        self.transient(parent)
        self.title("经济画像")
        self.geometry("700x500")
        self['bg'] = "#f0f0f0"
        
        self.create_widgets()
        self.show_profile()
    
    def create_widgets(self):
        """创建经济画像界面组件"""
        # 头部标签
        header_label = tk.Label(self, text="您的经济水平画像", font=("SimHei", 16, "bold"),
                              bg="#f0f0f0", fg="#2c3e50")
        header_label.pack(pady=20)
        
        # 指标框架
        self.indicators_frame = tk.Frame(self, bg="#f0f0f0")
        self.indicators_frame.pack(fill=tk.X, padx=50, pady=10)
        
        # 分析框架
        self.analysis_frame = tk.Frame(self, bg="#f0f0f0")
        self.analysis_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
    
    def show_profile(self):
        """显示经济画像"""
        # 获取经济画像
        profile = self.prediction_model.get_economic_profile()
        
        if not profile:
            tk.Label(self.indicators_frame, text="暂无足够数据生成经济画像，请先添加更多收支记录",
                    font=("SimHei", 12), bg="#f0f0f0", fg="#e74c3c").pack(pady=20)
            return
        
        # 显示指标
        indicators = profile['indicators']
        
        indicator_labels = [
            f"恩格尔系数: {indicators['engel_coefficient']:.2%}",
            f"平均消费倾向 (APC): {indicators['avg_propensity_consumption']:.2%}",
            f"边际消费倾向 (MPC): {indicators['marginal_propensity_consumption']:.2%}"
        ]
        
        for i, text in enumerate(indicator_labels):
            frame = tk.Frame(self.indicators_frame, bg="white", pady=10, padx=20, relief=tk.RAISED)
            frame.pack(fill=tk.X, pady=5)
            tk.Label(frame, text=text, font=("SimHei", 12), bg="white").pack(side=tk.LEFT)
        
        # 显示分析
        analysis = profile['analysis']
        
        analysis_text = tk.Text(self.analysis_frame, wrap=tk.WORD, font=("SimHei", 12),
                              bg="white", padx=20, pady=20, relief=tk.RAISED)
        analysis_text.pack(fill=tk.BOTH, expand=True)
        
        for i, text in enumerate(analysis):
            analysis_text.insert(tk.END, f"{i+1}. {text}\n\n")
        
        analysis_text['state'] = tk.DISABLED  # 设置为只读