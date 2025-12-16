import sys
import os
import random
import string
import time
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.account_model import AccountModel
from src.models.prediction_model import PredictionModel

class FuzzTester:
    """简单的模糊测试工具"""
    
    def __init__(self):
        self.crash_count = 0
        self.crash_cases = []
        self.test_count = 0
        self.start_time = time.time()
    
    def generate_random_string(self, length=10):
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))
    
    def generate_random_float(self, min_val=0.01, max_val=10000.0):
        """生成随机浮点数"""
        return random.uniform(min_val, max_val)
    
    def generate_random_date(self):
        """生成随机日期字符串"""
        year = random.randint(2000, 2025)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # 避免月日不合法
        return f"{year}-{month:02d}-{day:02d}"
    
    def fuzz_account_model(self):
        """模糊测试AccountModel"""
        # 创建临时数据文件
        temp_file = f"data/test_fuzz_{random.randint(1000, 9999)}.json"
        
        try:
            # 初始化AccountModel
            account_model = AccountModel(temp_file)
            
            # 测试add_record
            for _ in range(5):
                amount = self.generate_random_float()
                record_type = random.choice(['income', 'expense'])
                date = self.generate_random_date()
                description = self.generate_random_string(random.randint(0, 50))
                success, record = account_model.add_record(amount, record_type, date, description)
                
            # 测试get_all_records
            all_records = account_model.get_all_records()
            
            # 测试get_records_by_date_range
            start_date = self.generate_random_date()
            end_date = self.generate_random_date()
            records_by_date = account_model.get_records_by_date_range(start_date, end_date)
            
            # 测试get_incomes_and_expenses
            incomes_expenses = account_model.get_incomes_and_expenses()
            
            # 测试delete_record
            if all_records:
                record_id = random.choice(all_records)['id']
                success, deleted_record = account_model.delete_record(record_id, self.generate_random_string(20))
            
            # 测试save_records
            saved = account_model.save_records()
            
        except Exception as e:
            self.crash_count += 1
            crash_info = {
                "function": "AccountModel",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "test_count": self.test_count
            }
            self.crash_cases.append(crash_info)
            print(f"\n===== 崩溃 #{self.crash_count} =====")
            print(f"函数: AccountModel")
            print(f"错误: {e}")
            print(f"测试次数: {self.test_count}")
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def fuzz_prediction_model(self):
        """模糊测试PredictionModel"""
        # 创建临时数据文件
        temp_file = f"data/test_fuzz_pred_{random.randint(1000, 9999)}.json"
        
        try:
            # 初始化AccountModel和PredictionModel
            account_model = AccountModel(temp_file)
            prediction_model = PredictionModel(account_model)
            
            # 添加一些记录用于预测
            for _ in range(10):
                amount = self.generate_random_float()
                record_type = random.choice(['income', 'expense'])
                date = self.generate_random_date()
                description = self.generate_random_string(random.randint(0, 50))
                account_model.add_record(amount, record_type, date, description)
            
            # 测试prepare_data_for_prediction
            daily_income, daily_expense = prediction_model.prepare_data_for_prediction()
            
            # 测试predict_future
            future_prediction = prediction_model.predict_future(days_ahead=random.randint(1, 365))
            
            # 测试calculate_economic_indicators
            indicators = prediction_model.calculate_economic_indicators()
            
            # 测试get_economic_profile
            profile = prediction_model.get_economic_profile()
            
            # 测试predict_future_by_time_range
            start_date = self.generate_random_date()
            end_date = self.generate_random_date()
            future_by_range = prediction_model.predict_future_by_time_range(start_date, end_date, random.randint(1, 30))
            
        except Exception as e:
            self.crash_count += 1
            crash_info = {
                "function": "PredictionModel",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "test_count": self.test_count
            }
            self.crash_cases.append(crash_info)
            print(f"\n===== 崩溃 #{self.crash_count} =====")
            print(f"函数: PredictionModel")
            print(f"错误: {e}")
            print(f"测试次数: {self.test_count}")
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def run(self, test_count=10000, timeout_hours=5):
        """运行模糊测试"""
        print(f"开始模糊测试...")
        print(f"目标测试次数: {test_count}")
        print(f"超时时间: {timeout_hours}小时")
        print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        
        timeout_seconds = timeout_hours * 3600
        
        while self.test_count < test_count and (time.time() - self.start_time) < timeout_seconds:
            self.test_count += 1
            
            # 随机选择测试目标
            if random.random() < 0.5:
                self.fuzz_account_model()
            else:
                self.fuzz_prediction_model()
            
            # 每100次测试输出一次进度
            if self.test_count % 100 == 0:
                elapsed = time.time() - self.start_time
                hours, remainder = divmod(elapsed, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f"\n进度: {self.test_count}/{test_count} 测试")
                print(f"耗时: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
                print(f"崩溃数: {self.crash_count}")
        
        self.end_time = time.time()
        self._print_summary()
    
    def _print_summary(self):
        """打印测试摘要"""
        print("\n" + "="*50)
        print("模糊测试摘要")
        print("="*50)
        print(f"总测试次数: {self.test_count}")
        print(f"崩溃数: {self.crash_count}")
        
        elapsed = self.end_time - self.start_time
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"总耗时: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
        
        print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}")
        print(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.end_time))}")
        
        if self.crash_count > 0:
            print(f"\n崩溃详情:")
            for i, crash in enumerate(self.crash_cases):
                print(f"\n崩溃 #{i+1}:")
                print(f"  函数: {crash['function']}")
                print(f"  错误: {crash['error']}")
                print(f"  测试次数: {crash['test_count']}")
                print(f"  堆栈跟踪:")
                print(crash['traceback'])
        else:
            print(f"\n没有发现崩溃!")
        
        # 保存测试结果到文件
        with open("fuzz_test_results.txt", "w", encoding="utf-8") as f:
            f.write("模糊测试结果\n")
            f.write("="*50 + "\n")
            f.write(f"总测试次数: {self.test_count}\n")
            f.write(f"崩溃数: {self.crash_count}\n")
            f.write(f"总耗时: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}\n")
            f.write(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}\n")
            f.write(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.end_time))}\n")
            
            if self.crash_count > 0:
                f.write(f"\n崩溃详情:\n")
                for i, crash in enumerate(self.crash_cases):
                    f.write(f"\n崩溃 #{i+1}:\n")
                    f.write(f"  函数: {crash['function']}\n")
                    f.write(f"  错误: {crash['error']}\n")
                    f.write(f"  测试次数: {crash['test_count']}\n")
                    f.write(f"  堆栈跟踪:\n")
                    f.write(crash['traceback'] + "\n")
            else:
                f.write(f"\n没有发现崩溃!\n")
        
        print(f"\n测试结果已保存到: fuzz_test_results.txt")

if __name__ == "__main__":
    # 运行模糊测试
    tester = FuzzTester()
    # 运行10000次测试，或者5小时，以先到者为准
    tester.run(test_count=10000, timeout_hours=5)
