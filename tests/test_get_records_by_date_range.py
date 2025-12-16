import pytest
import os
from src.models.account_model import AccountModel

class TestGetRecordsByDateRange:
    """测试AccountModel.get_records_by_date_range函数"""
    
    def setup_method(self):
        """每个测试方法执行前初始化"""
        # 使用临时数据文件
        self.temp_data_file = 'data/test_date_range_records.json'
        if os.path.exists(self.temp_data_file):
            os.remove(self.temp_data_file)
        # 创建AccountModel实例
        self.account_model = AccountModel(self.temp_data_file)
        # 添加测试数据
        self._add_test_records()
    
    def teardown_method(self):
        """每个测试方法执行后清理"""
        if os.path.exists(self.temp_data_file):
            os.remove(self.temp_data_file)
    
    def _add_test_records(self):
        """添加测试记录"""
        test_records = [
            (1000, 'income', '2023-01-01', '工资1月'),
            (500, 'expense', '2023-01-15', '房租1月'),
            (200, 'expense', '2023-01-20', '餐饮1月'),
            (1200, 'income', '2023-02-01', '工资2月'),
            (550, 'expense', '2023-02-15', '房租2月'),
            (250, 'expense', '2023-02-20', '餐饮2月'),
            (1500, 'income', '2023-03-01', '工资3月'),
            (600, 'expense', '2023-03-15', '房租3月'),
            (300, 'expense', '2023-03-20', '餐饮3月'),
            (1800, 'income', '2023-04-01', '工资4月'),
        ]
        
        for amount, record_type, date, description in test_records:
            self.account_model.add_record(amount, record_type, date, description)
    
    def test_empty_records(self):
        """测试空记录集"""
        # 清空记录
        self.account_model.records = []
        # 测试查询
        result = self.account_model.get_records_by_date_range('2023-01-01', '2023-01-31')
        assert len(result) == 0
    
    def test_only_start_date(self):
        """测试只有开始日期"""
        result = self.account_model.get_records_by_date_range(start_date='2023-03-01')
        # 应该返回3月和4月的记录
        assert len(result) == 4
        for record in result:
            assert record['date'] >= '2023-03-01'
    
    def test_only_end_date(self):
        """测试只有结束日期"""
        result = self.account_model.get_records_by_date_range(end_date='2023-01-31')
        # 应该返回1月的记录
        assert len(result) == 3
        for record in result:
            assert record['date'] <= '2023-01-31'
    
    def test_both_dates(self):
        """测试同时有开始和结束日期"""
        result = self.account_model.get_records_by_date_range('2023-02-01', '2023-02-28')
        # 应该返回2月的记录
        assert len(result) == 3
        for record in result:
            assert '2023-02' in record['date']
    
    def test_date_range_contains_all(self):
        """测试日期范围包含所有记录"""
        result = self.account_model.get_records_by_date_range('2022-12-01', '2023-05-01')
        # 应该返回所有10条记录
        assert len(result) == 10
    
    def test_date_range_contains_none(self):
        """测试日期范围不包含任何记录"""
        result = self.account_model.get_records_by_date_range('2022-01-01', '2022-12-31')
        # 应该返回0条记录
        assert len(result) == 0
    
    def test_start_date_equal_end_date(self):
        """测试开始日期等于结束日期"""
        result = self.account_model.get_records_by_date_range('2023-01-01', '2023-01-01')
        # 应该返回1月1日的记录
        assert len(result) == 1
        assert result[0]['date'] == '2023-01-01'
    
    def test_start_date_greater_than_end_date(self):
        """测试开始日期大于结束日期"""
        result = self.account_model.get_records_by_date_range('2023-03-01', '2023-02-01')
        # 应该返回0条记录
        assert len(result) == 0
    
    def test_boundary_dates(self):
        """测试边界日期"""
        # 测试开始日期边界
        result1 = self.account_model.get_records_by_date_range('2023-01-15', '2023-02-15')
        # 应该返回1月15日、1月20日、2月1日、2月15日的记录
        assert len(result1) == 4
        
        # 测试结束日期边界
        result2 = self.account_model.get_records_by_date_range('2023-02-01', '2023-02-20')
        # 应该返回2月1日、2月15日、2月20日的记录
        assert len(result2) == 3
    
    def test_multiple_records_per_date(self):
        """测试同一日期多条记录"""
        # 添加同一日期的多条记录
        self.account_model.add_record(100, 'expense', '2023-01-01', '早餐')
        self.account_model.add_record(200, 'expense', '2023-01-01', '午餐')
        self.account_model.add_record(300, 'expense', '2023-01-01', '晚餐')
        
        result = self.account_model.get_records_by_date_range('2023-01-01', '2023-01-01')
        # 应该返回4条记录（原工资记录+3条新添加的记录）
        assert len(result) == 4
    
    def test_different_record_types(self):
        """测试不同类型记录"""
        result = self.account_model.get_records_by_date_range('2023-01-01', '2023-04-01')
        # 统计收入和支出记录数量
        income_count = sum(1 for r in result if r['type'] == 'income')
        expense_count = sum(1 for r in result if r['type'] == 'expense')
        # 应该有4条收入记录和6条支出记录
        assert income_count == 4
        assert expense_count == 6
