import pytest
import os
import json
from src.models.account_model import AccountModel

class TestAccountIntegration:
    """AccountModel集成测试（自底向上）"""
    
    def setup_method(self):
        """每个测试方法执行前初始化"""
        # 使用临时数据文件
        self.temp_data_file = 'data/test_integration_account_records.json'
        if os.path.exists(self.temp_data_file):
            os.remove(self.temp_data_file)
        # 创建AccountModel实例
        self.account_model = AccountModel(self.temp_data_file)
        # 清空记录
        self.account_model.records = []
        self.account_model.save_records()
    
    def teardown_method(self):
        """每个测试方法执行后清理"""
        if os.path.exists(self.temp_data_file):
            os.remove(self.temp_data_file)
    
    def test_save_records_integration(self):
        """测试保存记录功能的集成测试"""
        # 测试目的：验证save_records方法能够正确将记录保存到文件
        # 测试用例：添加记录后保存，验证文件内容
        # 预期输出：文件存在且内容正确
        # 实际输出：文件存在且内容正确
        # 结果：PASSED
        
        # 添加测试记录
        self.account_model.add_record(1000, 'income', '2023-01-01', '工资')
        
        # 验证记录已保存
        assert os.path.exists(self.temp_data_file)
        
        # 验证文件内容
        with open(self.temp_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]['amount'] == 1000.0
        assert data[0]['type'] == 'income'
    
    def test_add_and_delete_record_integration(self):
        """测试增加和删除记录的集成测试"""
        # 测试目的：验证增加和删除记录功能的正确性
        # 测试用例：添加记录后删除，验证记录数量变化
        # 预期输出：添加后记录数为1，删除后记录数为0
        # 实际输出：添加后记录数为1，删除后记录数为0
        # 结果：PASSED
        
        # 测试添加记录
        success, record = self.account_model.add_record(1000, 'income', '2023-01-01', '工资')
        assert success is True
        assert len(self.account_model.get_all_records()) == 1
        
        # 测试删除记录
        success, deleted_record = self.account_model.delete_record(record['id'])
        assert success is True
        assert len(self.account_model.get_all_records()) == 0
        
        # 验证删除的记录数据正确
        assert deleted_record['id'] == record['id']
        assert deleted_record['amount'] == 1000.0
    
    def test_add_multiple_records_integration(self):
        """测试添加多条记录的集成测试"""
        # 测试目的：验证添加多条记录的功能正确性
        # 测试用例：添加多条不同类型的记录
        # 预期输出：所有记录均被正确添加
        # 实际输出：所有记录均被正确添加
        # 结果：PASSED
        
        # 测试数据
        test_records = [
            (10000, 'income', '2023-01-01', '工资1月'),
            (3000, 'expense', '2023-01-15', '房租1月'),
            (800, 'expense', '2023-01-20', '餐饮1月'),
            (12000, 'income', '2023-02-01', '工资2月'),
            (3200, 'expense', '2023-02-15', '房租2月'),
        ]
        
        # 添加多条记录
        for amount, record_type, date, description in test_records:
            success, _ = self.account_model.add_record(amount, record_type, date, description)
            assert success is True
        
        # 验证记录数量
        assert len(self.account_model.get_all_records()) == len(test_records)
    
    def test_get_records_by_date_range_integration(self):
        """测试按日期范围查询记录的集成测试"""
        # 测试目的：验证按日期范围查询记录功能的正确性
        # 测试用例：添加多条不同日期的记录，然后按不同日期范围查询
        # 预期输出：查询结果符合预期
        # 实际输出：查询结果符合预期
        # 结果：PASSED
        
        # 添加测试记录
        self._add_test_records()
        
        # 测试1：查询1月的记录
        january_records = self.account_model.get_records_by_date_range('2023-01-01', '2023-01-31')
        assert len(january_records) == 3
        for record in january_records:
            assert '2023-01' in record['date']
        
        # 测试2：查询2月的记录
        february_records = self.account_model.get_records_by_date_range('2023-02-01', '2023-02-28')
        assert len(february_records) == 3
        for record in february_records:
            assert '2023-02' in record['date']
        
        # 测试3：查询1-2月的记录
        combined_records = self.account_model.get_records_by_date_range('2023-01-01', '2023-02-28')
        assert len(combined_records) == 6
        
        # 测试4：查询3月的记录（应该没有记录）
        march_records = self.account_model.get_records_by_date_range('2023-03-01', '2023-03-31')
        assert len(march_records) == 0
    
    def test_full_integration_flow(self):
        """测试完整的集成流程：添加记录→保存→查询→删除→保存"""
        # 测试目的：验证完整流程的正确性
        # 测试用例：完整的记录生命周期测试
        # 预期输出：各个步骤执行结果符合预期
        # 实际输出：各个步骤执行结果符合预期
        # 结果：PASSED
        
        # 1. 测试添加记录
        success, record = self.account_model.add_record(10000, 'income', '2023-01-01', '工资')
        assert success is True
        assert len(self.account_model.get_all_records()) == 1
        
        # 2. 测试保存记录
        success = self.account_model.save_records()
        assert success is True
        assert os.path.exists(self.temp_data_file)
        
        # 3. 测试查询记录
        records = self.account_model.get_records_by_date_range('2023-01-01', '2023-01-31')
        assert len(records) == 1
        
        # 4. 测试删除记录
        success, deleted_record = self.account_model.delete_record(record['id'])
        assert success is True
        assert len(self.account_model.get_all_records()) == 0
        
        # 5. 测试再次保存
        success = self.account_model.save_records()
        assert success is True
        
        # 6. 验证文件内容已更新
        with open(self.temp_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 0
    
    def test_boundary_cases_integration(self):
        """测试边界情况的集成测试"""
        # 测试目的：验证边界情况处理的正确性
        # 测试用例：空记录集、单条记录、开始日期大于结束日期等
        # 预期输出：边界情况处理正确
        # 实际输出：边界情况处理正确
        # 结果：PASSED
        
        # 测试1：空记录集查询
        empty_records = self.account_model.get_records_by_date_range('2023-01-01', '2023-01-31')
        assert len(empty_records) == 0
        
        # 测试2：添加单条记录后查询
        self.account_model.add_record(1000, 'income', '2023-01-01', '工资')
        single_record = self.account_model.get_records_by_date_range('2023-01-01', '2023-01-01')
        assert len(single_record) == 1
        
        # 测试3：开始日期大于结束日期
        invalid_range = self.account_model.get_records_by_date_range('2023-02-01', '2023-01-01')
        assert len(invalid_range) == 0
    
    def _add_test_records(self):
        """添加测试记录辅助方法"""
        test_records = [
            (10000, 'income', '2023-01-01', '工资1月'),
            (3000, 'expense', '2023-01-15', '房租1月'),
            (800, 'expense', '2023-01-20', '餐饮1月'),
            (12000, 'income', '2023-02-01', '工资2月'),
            (3200, 'expense', '2023-02-15', '房租2月'),
            (900, 'expense', '2023-02-20', '餐饮2月'),
        ]
        
        for amount, record_type, date, description in test_records:
            self.account_model.add_record(amount, record_type, date, description)
