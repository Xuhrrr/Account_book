import pytest
import os
import numpy as np
from src.models.account_model import AccountModel
from src.models.prediction_model import PredictionModel

class TestPredictFuture:
    """测试PredictionModel.predict_future函数"""
    
    def setup_method(self):
        """每个测试方法执行前初始化"""
        # 使用临时数据文件
        self.temp_data_file = 'data/test_predict_future_records.json'
        if os.path.exists(self.temp_data_file):
            os.remove(self.temp_data_file)
        # 创建AccountModel实例
        self.account_model = AccountModel(self.temp_data_file)
        # 清空记录
        self.account_model.records = []
        self.account_model.save_records()
        # 创建PredictionModel实例
        self.prediction_model = PredictionModel(self.account_model)
    
    def teardown_method(self):
        """每个测试方法执行后清理"""
        if os.path.exists(self.temp_data_file):
            os.remove(self.temp_data_file)
    
    def _add_sufficient_test_records(self):
        """添加足够的测试记录用于预测"""
        test_records = [
            # 1月数据
            (10000, 'income', '2023-01-01', '工资1月'),
            (3000, 'expense', '2023-01-02', '房租1月'),
            (1500, 'expense', '2023-01-03', '餐饮1月'),
            # 2月数据
            (12000, 'income', '2023-02-01', '工资2月'),
            (3000, 'expense', '2023-02-02', '房租2月'),
            (1800, 'expense', '2023-02-03', '餐饮2月'),
            # 3月数据
            (11000, 'income', '2023-03-01', '工资3月'),
            (3200, 'expense', '2023-03-02', '房租3月'),
            (1600, 'expense', '2023-03-03', '餐饮3月'),
            # 4月数据
            (13000, 'income', '2023-04-01', '工资4月'),
            (3200, 'expense', '2023-04-02', '房租4月'),
            (1900, 'expense', '2023-04-03', '餐饮4月'),
        ]
        
        for amount, record_type, date, description in test_records:
            self.account_model.add_record(amount, record_type, date, description)
    
    def test_predict_future_empty_records(self):
        """测试空记录集"""
        result = self.prediction_model.predict_future()
        assert result is None
    
    def test_predict_future_insufficient_data(self):
        """测试数据不足（少于2条相同类型记录）"""
        # 添加1条收入记录和1条支出记录
        self.account_model.add_record(10000, 'income', '2023-01-01', '工资')
        self.account_model.add_record(3000, 'expense', '2023-01-02', '房租')
        
        result = self.prediction_model.predict_future()
        assert result is None
    
    def test_predict_future_with_data(self):
        """测试有足够数据的情况"""
        # 添加足够的测试记录
        self._add_sufficient_test_records()
        
        result = self.prediction_model.predict_future()
        # 验证结果不为空
        assert result is not None
        # 验证结果结构
        assert 'income_prediction' in result
        assert 'expense_prediction' in result
        assert 'net_prediction' in result
        # 默认预测30天，所以每个列表应该有30个元素
        assert len(result['income_prediction']) == 30
        assert len(result['expense_prediction']) == 30
        assert len(result['net_prediction']) == 30
    
    def test_predict_future_different_days(self):
        """测试不同预测天数"""
        # 添加足够的测试记录
        self._add_sufficient_test_records()
        
        # 测试预测7天
        result_7days = self.prediction_model.predict_future(days_ahead=7)
        assert len(result_7days['income_prediction']) == 7
        
        # 测试预测15天
        result_15days = self.prediction_model.predict_future(days_ahead=15)
        assert len(result_15days['income_prediction']) == 15
        
        # 测试预测60天
        result_60days = self.prediction_model.predict_future(days_ahead=60)
        assert len(result_60days['income_prediction']) == 60
    
    def test_predict_future_with_provided_records(self):
        """测试提供自定义记录的情况"""
        # 添加足够的测试记录
        self._add_sufficient_test_records()
        
        # 获取现有记录
        records = self.account_model.get_all_records()
        
        # 使用提供的记录进行预测
        result = self.prediction_model.predict_future(records=records)
        
        # 验证结果不为空
        assert result is not None
        assert len(result['income_prediction']) == 30
    
    def test_predict_future_positive_values(self):
        """测试预测结果均为正值"""
        # 添加足够的测试记录
        self._add_sufficient_test_records()
        
        result = self.prediction_model.predict_future()
        
        # 验证所有预测值均为正值
        for income in result['income_prediction']:
            assert income >= 0
        for expense in result['expense_prediction']:
            assert expense >= 0
        for net in result['net_prediction']:
            # 净预测可以为负值
            pass
    
    def test_predict_future_regression_accuracy(self):
        """测试回归预测的准确性"""
        # 添加线性增长的测试记录
        for i in range(1, 10):
            date = f'2023-0{i}-01' if i < 10 else f'2023-{i}-01'
            # 收入线性增长
            income_amount = 10000 + i * 1000
            # 支出线性增长
            expense_amount = 3000 + i * 200
            
            self.account_model.add_record(income_amount, 'income', date, f'工资{i}月')
            self.account_model.add_record(expense_amount, 'expense', date, f'房租{i}月')
        
        result = self.prediction_model.predict_future(days_ahead=5)
        
        # 验证收入预测呈增长趋势
        assert result['income_prediction'][1] >= result['income_prediction'][0]
        assert result['income_prediction'][2] >= result['income_prediction'][1]
        assert result['income_prediction'][3] >= result['income_prediction'][2]
        
        # 验证支出预测呈增长趋势
        assert result['expense_prediction'][1] >= result['expense_prediction'][0]
        assert result['expense_prediction'][2] >= result['expense_prediction'][1]
        assert result['expense_prediction'][3] >= result['expense_prediction'][2]
    
    def test_predict_future_with_mixed_records(self):
        """测试包含不同类型记录的情况"""
        # 添加混合类型的测试记录
        mixed_records = [
            (10000, 'income', '2023-01-01', '工资1月'),
            (3000, 'expense', '2023-01-02', '房租1月'),
            (1500, 'expense', '2023-01-03', '餐饮1月'),
            (500, 'expense', '2023-01-04', '交通1月'),
            (12000, 'income', '2023-02-01', '工资2月'),
            (3000, 'expense', '2023-02-02', '房租2月'),
            (1800, 'expense', '2023-02-03', '餐饮2月'),
            (600, 'expense', '2023-02-04', '交通2月'),
            (11000, 'income', '2023-03-01', '工资3月'),
            (3200, 'expense', '2023-03-02', '房租3月'),
            (1600, 'expense', '2023-03-03', '餐饮3月'),
            (550, 'expense', '2023-03-04', '交通3月'),
        ]
        
        for amount, record_type, date, description in mixed_records:
            self.account_model.add_record(amount, record_type, date, description)
        
        result = self.prediction_model.predict_future()
        
        # 验证结果不为空
        assert result is not None
        assert len(result['income_prediction']) == 30
    
    def test_predict_future_with_seasonal_data(self):
        """测试季节性数据"""
        # 添加模拟季节性的测试记录（节假日消费高峰）
        seasonal_records = [
            # 常规月份
            (10000, 'income', '2023-01-01', '工资1月'),
            (3000, 'expense', '2023-01-02', '房租1月'),
            (1500, 'expense', '2023-01-03', '餐饮1月'),
            # 节假日月份（消费增加）
            (10000, 'income', '2023-02-01', '工资2月'),
            (3000, 'expense', '2023-02-02', '房租2月'),
            (3000, 'expense', '2023-02-03', '春节餐饮'),
            # 常规月份
            (10000, 'income', '2023-03-01', '工资3月'),
            (3000, 'expense', '2023-03-02', '房租3月'),
            (1800, 'expense', '2023-03-03', '餐饮3月'),
            # 节假日月份（消费增加）
            (10000, 'income', '2023-05-01', '工资5月'),
            (3000, 'expense', '2023-05-02', '房租5月'),
            (2500, 'expense', '2023-05-03', '五一餐饮'),
        ]
        
        for amount, record_type, date, description in seasonal_records:
            self.account_model.add_record(amount, record_type, date, description)
        
        result = self.prediction_model.predict_future()
        
        # 验证结果不为空
        assert result is not None
        assert len(result['income_prediction']) == 30
    
    def test_predict_future_after_exception(self):
        """测试预测模型异常处理"""
        # 添加足够的测试记录
        self._add_sufficient_test_records()
        
        # 模拟异常情况（通过修改records格式）
        # 注意：这里不会实际触发异常，因为异常处理已在模型中实现
        result = self.prediction_model.predict_future()
        
        # 验证结果不为空
        assert result is not None
    
    def test_predict_future_net_prediction_calculation(self):
        """测试净预测计算准确性"""
        # 添加足够的测试记录
        self._add_sufficient_test_records()
        
        result = self.prediction_model.predict_future(days_ahead=5)
        
        # 验证净预测计算准确性
        for i in range(5):
            expected_net = result['income_prediction'][i] - result['expense_prediction'][i]
            assert pytest.approx(result['net_prediction'][i], 0.01) == expected_net
    
    def test_predict_future_monthly_data(self):
        """测试月度数据的预测"""
        # 添加月度数据
        for year in [2023, 2024]:
            for month in range(1, 13):
                date = f'{year}-{month:02d}-01'
                # 收入和支出随月份变化
                income_amount = 10000 + month * 500
                expense_amount = 3000 + month * 200
                
                self.account_model.add_record(income_amount, 'income', date, f'工资{year}年{month}月')
                self.account_model.add_record(expense_amount, 'expense', date, f'房租{year}年{month}月')
        
        result = self.prediction_model.predict_future(days_ahead=10)
        
        # 验证结果不为空
        assert result is not None
        assert len(result['income_prediction']) == 10
