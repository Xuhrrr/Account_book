import json
import os
from datetime import datetime

class AccountModel:
    def __init__(self, data_file='data/account_records.json'):
        self.data_file = data_file
        self.ensure_data_directory()
        self.records = self.load_records()
    
    def ensure_data_directory(self):
        """确保数据目录存在"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def load_records(self):
        """从文件加载记录"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"加载记录时出错: {e}")
            return []
    
    def save_records(self):
        """保存记录到文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"保存记录时出错: {e}")
            return False
    
    def add_record(self, amount, record_type, date, description=''):
        """添加一条收支记录"""
        record = {
            'id': self._generate_id(),
            'amount': float(amount),
            'type': record_type,  # 'income' 或 'expense'
            'date': date,
            'description': description,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.records.append(record)
        return self.save_records(), record
    
    def delete_record(self, record_id, delete_reason=''):
        """删除一条收支记录"""
        for i, record in enumerate(self.records):
            if record['id'] == record_id:
                deleted_record = self.records.pop(i)
                # 保存删除原因（可以用于恢复或记录）
                deleted_record['deleted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                deleted_record['delete_reason'] = delete_reason
                return self.save_records(), deleted_record
        return False, None
    
    def get_all_records(self):
        """获取所有记录"""
        return self.records
    
    def get_records_by_date_range(self, start_date=None, end_date=None):
        """根据日期范围获取记录"""
        filtered_records = self.records.copy()
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            filtered_records = [r for r in filtered_records if datetime.strptime(r['date'], '%Y-%m-%d') >= start]
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            filtered_records = [r for r in filtered_records if datetime.strptime(r['date'], '%Y-%m-%d') <= end]
        
        return filtered_records
    
    def get_incomes_and_expenses(self, records=None):
        """获取收入和支出的汇总数据"""
        if records is None:
            records = self.records
        
        total_income = sum(r['amount'] for r in records if r['type'] == 'income')
        total_expense = sum(r['amount'] for r in records if r['type'] == 'expense')
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense
        }
    
    def _generate_id(self):
        """生成唯一ID"""
        if not self.records:
            return 1
        return max(r['id'] for r in self.records) + 1