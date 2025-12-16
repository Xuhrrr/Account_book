import pytest
import os
import pandas as pd
from src.models.account_model import AccountModel
from src.models.prediction_model import PredictionModel

class TestPredictionIntegration:
    """PredictionModel集成测试（自底向上）"""
    
    def setup_method(self):
        """每个测试方法执行前初始化"""
        # 使用临时数据文件
        self.temp_data_file = 'data/test_integration_prediction_records.json'
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
    
    def test_prepare_data_for_prediction_integration(self):
        """测试数据准备功能的集成测试"""
        # 测试目的：验证prepare_data_for_prediction方法能够正确处理数据
        # 测试用例：添加记录后，调用数据准备方法
        # 预期输出：返回处理后的收入和支出数据
        # 实际输出：返回处理后的收入和支出数据
        # 结果：PASSED
        
        # 测试1：空记录集
        daily_income, daily_expense = self.prediction_model.prepare_data_for_prediction()
        assert daily_income is None
        assert daily_expense is None
        
        # 测试2：数据不足
        self.account_model.add_record(10000, 'income', '2023-01-01', '工资')
        self.account_model.add_record(3000, 'expense', '2023-01-02', '房租')
        daily_income, daily_expense = self.prediction_model.prepare_data_for_prediction()
        assert daily_income is None
        assert daily_expense is None
        
        # 测试3：数据充足
        self._add_sufficient_test_records()
        daily_income, daily_expense = self.prediction_model.prepare_data_for_prediction()
        
        # 验证返回结果
        assert daily_income is not None
        assert daily_expense is not None
        
        # 验证数据结构
        assert isinstance(daily_income, pd.DataFrame)
        assert isinstance(daily_expense, pd.DataFrame)
        assert 'date' in daily_income.columns
        assert 'amount' in daily_income.columns
        assert 'date' in daily_expense.columns
        assert 'amount' in daily_expense.columns
        
        # 验证数据行数
        assert len(daily_income) >= 2
        assert len(daily_expense) >= 2
    
    def test_predict_using_regression_integration(self):
        """测试回归预测功能的集成测试"""
        # 测试目的：验证回归预测方法能够正确预测未来数据
        # 测试用例：准备数据后，调用回归预测方法
        # 预期输出：返回预测结果
        # 实际输出：返回预测结果
        # 结果：PASSED
        
        # 添加足够的测试记录
        self._add_sufficient_test_records()
        
        # 准备数据
        daily_income, daily_expense = self.prediction_model.prepare_data_for_prediction()
        
        # 测试收入预测
        income_predictions = self.prediction_model._predict_using_regression(daily_income, 7)
        assert len(income_predictions) == 7
        for pred in income_predictions:
            assert pred >= 0
        
        # 测试支出预测
        expense_predictions = self.prediction_model._predict_using_regression(daily_expense, 7)
        assert len(expense_predictions) == 7
        for pred in expense_predictions:
            assert pred >= 0
        
        # 测试不同预测天数
        predictions_30days = self.prediction_model._predict_using_regression(daily_income, 30)
        assert len(predictions_30days) == 30
        
        predictions_90days = self.prediction_model._predict_using_regression(daily_income, 90)
        assert len(predictions_90days) == 90
    
    def test_predict_future_integration(self):
        """测试未来预测功能的集成测试"""
        # 测试目的：验证未来预测方法能够正确预测未来收支情况
        # 测试用例：添加足够记录后，调用未来预测方法
        # 预期输出：返回包含预测结果的字典
        # 实际输出：返回包含预测结果的字典
        # 结果：PASSED
        
        # 测试1：空记录集
        result_empty = self.prediction_model.predict_future()
        assert result_empty is None
        
        # 测试2：数据不足
        self.account_model.add_record(10000, 'income', '2023-01-01', '工资')
        self.account_model.add_record(3000, 'expense', '2023-01-02', '房租')
        result_insufficient = self.prediction_model.predict_future()
        assert result_insufficient is None
        
        # 测试3：数据充足
        self._add_sufficient_test_records()
        result = self.prediction_model.predict_future()
        
        # 验证结果结构
        assert result is not None
        assert 'income_prediction' in result
        assert 'expense_prediction' in result
        assert 'net_prediction' in result
        
        # 验证预测天数
        assert len(result['income_prediction']) == 30
        assert len(result['expense_prediction']) == 30
        assert len(result['net_prediction']) == 30
        
        # 验证预测值为正数
        for income in result['income_prediction']:
            assert income >= 0
        for expense in result['expense_prediction']:
            assert expense >= 0
    
    def test_predict_future_different_days_integration(self):
        """测试不同预测天数的集成测试"""
        # 测试目的：验证不同预测天数功能的正确性
        # 测试用例：使用不同的预测天数调用predict_future方法
        # 预期输出：返回对应天数的预测结果
        # 实际输出：返回对应天数的预测结果
        # 结果：PASSED
        
        # 添加足够的测试记录
        self._add_sufficient_test_records()
        
        # 测试预测7天
        result_7days = self.prediction_model.predict_future(days_ahead=7)
        assert len(result_7days['income_prediction']) == 7
        assert len(result_7days['expense_prediction']) == 7
        assert len(result_7days['net_prediction']) == 7
        
        # 测试预测15天
        result_15days = self.prediction_model.predict_future(days_ahead=15)
        assert len(result_15days['income_prediction']) == 15
        assert len(result_15days['expense_prediction']) == 15
        assert len(result_15days['net_prediction']) == 15
        
        # 测试预测60天
        result_60days = self.prediction_model.predict_future(days_ahead=60)
        assert len(result_60days['income_prediction']) == 60
        assert len(result_60days['expense_prediction']) == 60
        assert len(result_60days['net_prediction']) == 60
    
    def test_predict_future_with_provided_records_integration(self):
        """测试提供自定义记录的集成测试"""
        # 测试目的：验证提供自定义记录时预测功能的正确性
        # 测试用例：提供自定义记录调用predict_future方法
        # 预期输出：返回预测结果
        # 实际输出：返回预测结果
        # 结果：PASSED
        
        # 添加足够的测试记录
        self._add_sufficient_test_records()
        
        # 获取现有记录
        records = self.account_model.get_all_records()
        
        # 使用提供的记录进行预测
        result = self.prediction_model.predict_future(records=records)
        
        # 验证结果
        assert result is not None
        assert len(result['income_prediction']) == 30
        assert len(result['expense_prediction']) == 30
        assert len(result['net_prediction']) == 30
    
    def test_net_prediction_calculation_integration(self):
        """测试净预测计算的集成测试"""
        # 测试目的：验证净预测计算的准确性
        # 测试用例：验证净预测值是否等于收入预测减去支出预测
        # 预期输出：净预测值等于收入预测减去支出预测
        # 实际输出：净预测值等于收入预测减去支出预测
        # 结果：PASSED
        
        # 添加足够的测试记录
        self._add_sufficient_test_records()
        
        # 调用预测方法
        result = self.prediction_model.predict_future(days_ahead=5)
        
        # 验证净预测计算
        for i in range(5):
            expected_net = result['income_prediction'][i] - result['expense_prediction'][i]
            assert pytest.approx(result['net_prediction'][i], 0.01) == expected_net
    
    def test_full_prediction_workflow_integration(self):
        """测试完整预测工作流的集成测试"""
        # 测试目的：验证完整预测工作流的正确性
        # 测试用例：从添加记录到生成预测结果的完整流程
        # 预期输出：完整流程执行成功，返回预测结果
        # 实际输出：完整流程执行成功，返回预测结果
        # 结果：PASSED
        
        # 1. 添加测试记录
        self._add_sufficient_test_records()
        
        # 2. 准备数据
        daily_income, daily_expense = self.prediction_model.prepare_data_for_prediction()
        assert daily_income is not None
        assert daily_expense is not None
        
        # 3. 执行回归预测
        income_predictions = self.prediction_model._predict_using_regression(daily_income, 7)
        expense_predictions = self.prediction_model._predict_using_regression(daily_expense, 7)
        assert len(income_predictions) == 7
        assert len(expense_predictions) == 7
        
        # 4. 执行完整预测
        result = self.prediction_model.predict_future(days_ahead=7)
        assert result is not None
        
        # 5. 验证预测结果
        assert len(result['income_prediction']) == 7
        assert len(result['expense_prediction']) == 7
        assert len(result['net_prediction']) == 7
        
        # 6. 验证净预测计算
        for i in range(7):
            expected_net = result['income_prediction'][i] - result['expense_prediction'][i]
            assert pytest.approx(result['net_prediction'][i], 0.01) == expected_net
    
    def test_prediction_with_seasonal_data_integration(self):
        """测试季节性数据预测的集成测试"""
        # 测试目的：验证季节性数据预测的正确性
        # 测试用例：添加季节性数据后进行预测
        # 预期输出：返回预测结果
        # 实际输出：返回预测结果
        # 结果：PASSED
        
        # 添加模拟季节性的测试记录
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
        
        # 执行预测
        result = self.prediction_model.predict_future(days_ahead=10)
        
        # 验证结果
        assert result is not None
        assert len(result['income_prediction']) == 10
        assert len(result['expense_prediction']) == 10
        assert len(result['net_prediction']) == 10
    
    def test_prediction_error_handling_integration(self):
        """测试预测错误处理的集成测试"""
        # 测试目的：验证预测过程中的错误处理
        # 测试用例：在各种异常情况下调用预测方法
        # 预期输出：能够正确处理异常，返回合理结果
        # 实际输出：能够正确处理异常，返回合理结果
        # 结果：PASSED
        
        # 测试1：空记录集
        result_empty = self.prediction_model.predict_future()
        assert result_empty is None
        
        # 测试2：数据不足
        self.account_model.add_record(10000, 'income', '2023-01-01', '工资')
        result_insufficient = self.prediction_model.predict_future()
        assert result_insufficient is None
        
        # 测试3：添加足够数据后测试
        self._add_sufficient_test_records()
        result = self.prediction_model.predict_future()
        assert result is not None
        assert 'income_prediction' in result
        assert 'expense_prediction' in result
        assert 'net_prediction' in result
