import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入模型
from src.models.account_model import AccountModel
from src.models.prediction_model import PredictionModel

# 确保导入PySide6时出现问题不会导致整个程序崩溃
try:
    from PySide6.QtWidgets import QApplication
    from src.views.pyqt_main_view import PyQtMainView
    has_gui = True
except ImportError:
    has_gui = False
    print("警告: PySide6库未安装。请安装PySide6库以使用图形界面。")
    print("安装命令: pip install PySide6")

def main():
    """主函数"""
    # 初始化模型
    account_model = AccountModel()
    prediction_model = PredictionModel(account_model)
    
    # 尝试启动图形界面
    if has_gui:
        try:
            print("正在启动图形界面...")
            app = QApplication(sys.argv)
            window = PyQtMainView(account_model, prediction_model)
            window.show()
            sys.exit(app.exec())
        except Exception as e:
            print(f"启动图形界面时出错: {str(e)}")
            print("请确保PySide6已正确安装: pip install PySide6")
            print("尝试使用终端界面...")
    
    # 如果图形界面启动失败，启动终端界面
    print("\n===== 智能记账本（终端版） =====")
    print("\n提示：如果您想使用图形界面，请确保安装了PySide6库。")
    print("可以通过以下命令安装：pip install PySide6")
    print("\n现在启动功能完整的终端界面版本...")
    run_terminal_interface(account_model, prediction_model)

def run_terminal_interface(account_model, prediction_model):
    """终端界面版本"""
    while True:
        print("\n请选择操作：")
        print("1. 查看所有记录")
        print("2. 新增记录")
        print("3. 删除记录")
        print("4. 查看经济指标")
        print("5. 退出")
        
        choice = input("请输入选择 (1-5): ")
        
        if choice == '1':
            show_all_records(account_model)
        elif choice == '2':
            add_new_record(account_model)
        elif choice == '3':
            delete_record(account_model)
        elif choice == '4':
            show_economic_profile(prediction_model)
        elif choice == '5':
            print("感谢使用智能记账本！")
            break
        else:
            print("无效的选择，请重新输入。")

def show_all_records(account_model):
    """显示所有记录"""
    records = account_model.get_all_records()
    if not records:
        print("暂无记录。")
        return
    
    print("\n===== 所有记录 =====")
    print(f"{'ID':<5} {'金额':<10} {'类型':<8} {'日期':<12} {'描述':<20} {'创建时间':<20}")
    print("-" * 85)
    
    for record in records:
        type_text = "收入" if record['type'] == 'income' else "支出"
        print(f"{record['id']:<5} {record['amount']:<10.2f} {type_text:<8} {record['date']:<12} {record['description'][:18]:<20} {record['created_at'][:19]:<20}")

def add_new_record(account_model):
    """新增记录"""
    print("\n===== 新增记录 =====")
    try:
        amount = float(input("请输入金额: "))
        if amount <= 0:
            print("金额必须大于0！")
            return
        
        type_choice = input("请选择类型 (1: 收入, 2: 支出): ")
        record_type = 'income' if type_choice == '1' else 'expense'
        
        date = input("请输入日期 (YYYY-MM-DD，默认今天): ")
        if not date:
            from datetime import datetime
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            # 验证日期格式
            try:
                from datetime import datetime
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                print("日期格式不正确，请使用YYYY-MM-DD格式！")
                return
        
        description = input("请输入描述: ")
        
        success, _ = account_model.add_record(amount, record_type, date, description)
        if success:
            print("记录添加成功！")
        else:
            print("记录添加失败！")
    except ValueError:
        print("请输入有效的金额！")

def delete_record(account_model):
    """删除记录"""
    print("\n===== 删除记录 =====")
    try:
        record_id = int(input("请输入要删除的记录ID: "))
        reason = input("请输入删除原因 (可选): ")
        
        success, _ = account_model.delete_record(record_id, reason)
        if success:
            print("记录删除成功！")
        else:
            print("找不到指定的记录ID！")
    except ValueError:
        print("请输入有效的记录ID！")

def show_economic_profile(prediction_model):
    """显示经济画像"""
    profile = prediction_model.get_economic_profile()
    
    if not profile:
        print("暂无足够数据生成经济画像，请先添加更多收支记录。")
        return
    
    print("\n===== 经济水平画像 =====")
    indicators = profile['indicators']
    
    print(f"恩格尔系数: {indicators['engel_coefficient']:.2%}")
    print(f"平均消费倾向 (APC): {indicators['avg_propensity_consumption']:.2%}")
    print(f"边际消费倾向 (MPC): {indicators['marginal_propensity_consumption']:.2%}")
    
    print("\n===== 分析报告 =====")
    for i, text in enumerate(profile['analysis']):
        print(f"{i+1}. {text}")

if __name__ == "__main__":
    main()