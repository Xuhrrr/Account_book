import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

class PredictionModel:
    def __init__(self, account_model):
        self.account_model = account_model
    
    def prepare_data_for_prediction(self, records=None):
        """准备预测数据"""
        if records is None:
            records = self.account_model.get_all_records()
        
        if not records:
            return None, None
        
        # 转换为DataFrame进行处理
        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_year'] = df['date'].dt.dayofyear
        
        # 按日期分组，计算每日收支
        daily_income = df[df['type'] == 'income'].groupby('date')['amount'].sum().reset_index()
        daily_expense = df[df['type'] == 'expense'].groupby('date')['amount'].sum().reset_index()
        
        # 确保有数据用于预测
        if len(daily_income) < 2 or len(daily_expense) < 2:
            return None, None
        
        return daily_income, daily_expense
    
    def predict_future(self, days_ahead=30, records=None):
        """预测未来的收支情况"""
        daily_income, daily_expense = self.prepare_data_for_prediction(records)
        
        if daily_income is None or daily_expense is None:
            return None
        
        # 预测收入
        income_prediction = self._predict_using_regression(daily_income, days_ahead)
        # 预测支出
        expense_prediction = self._predict_using_regression(daily_expense, days_ahead)
        
        return {
            'income_prediction': income_prediction,
            'expense_prediction': expense_prediction,
            'net_prediction': [i - e for i, e in zip(income_prediction, expense_prediction)]
        }
        
    def predict_future_by_time_range(self, start_date_str, end_date_str, days_ahead=30):
        """根据指定时间区间的历史数据预测未来收支情况
        
        Args:
            start_date_str: 开始日期，格式 'YYYY-MM-DD'
            end_date_str: 结束日期，格式 'YYYY-MM-DD'
            days_ahead: 预测未来的天数
            
        Returns:
            包含预测结果的字典，或None（如果没有足够的数据）
        """
        # 获取所有记录
        all_records = self.account_model.get_all_records()
        
        if not all_records:
            return None
        
        # 筛选指定时间区间内的记录
        start_date = pd.to_datetime(start_date_str)
        end_date = pd.to_datetime(end_date_str)
        
        filtered_records = []
        for record in all_records:
            record_date = pd.to_datetime(record['date'])
            if start_date <= record_date <= end_date:
                filtered_records.append(record)
        
        if not filtered_records:
            return None
        
        # 计算时间区间内的平均收入和支出
        income_records = [r for r in filtered_records if r['type'] == 'income']
        expense_records = [r for r in filtered_records if r['type'] == 'expense']
        
        if not income_records or not expense_records:
            return None
        
        avg_income = sum(r['amount'] for r in income_records) / len(income_records)
        avg_expense = sum(r['amount'] for r in expense_records) / len(expense_records)
        
        # 计算日均收入和支出
        date_range_days = (end_date - start_date).days + 1
        daily_avg_income = sum(r['amount'] for r in income_records) / date_range_days
        daily_avg_expense = sum(r['amount'] for r in expense_records) / date_range_days
        
        # 生成未来预测
        future_income_prediction = [daily_avg_income] * days_ahead
        future_expense_prediction = [daily_avg_expense] * days_ahead
        
        return {
            'period_start_date': start_date_str,
            'period_end_date': end_date_str,
            'period_avg_income': avg_income,
            'period_avg_expense': avg_expense,
            'period_daily_avg_income': daily_avg_income,
            'period_daily_avg_expense': daily_avg_expense,
            'income_prediction': future_income_prediction,
            'expense_prediction': future_expense_prediction,
            'net_prediction': [i - e for i, e in zip(future_income_prediction, future_expense_prediction)]
        }
    
    def _predict_using_regression(self, daily_data, days_ahead):
        """使用线性回归进行预测"""
        try:
            # 准备特征和目标变量
            X = np.array(range(len(daily_data))).reshape(-1, 1)
            y = daily_data['amount'].values
            
            # 训练模型
            model = LinearRegression()
            model.fit(X, y)
            
            # 预测未来
            future_X = np.array(range(len(daily_data), len(daily_data) + days_ahead)).reshape(-1, 1)
            predictions = model.predict(future_X)
            
            # 确保预测值非负
            predictions = [max(0, p) for p in predictions]
            
            return predictions
        except Exception as e:
            print(f"预测时出错: {e}")
            # 返回简单的平均值作为备选方案
            avg_amount = daily_data['amount'].mean()
            return [avg_amount] * days_ahead
    
    def calculate_economic_indicators(self, records=None):
        """计算经济指标：恩格尔系数、APC、MPC"""
        if records is None:
            records = self.account_model.get_all_records()
        
        if not records:
            return None
        
        # 计算总收入和总支出
        summary = self.account_model.get_incomes_and_expenses(records)
        total_income = summary['total_income']
        total_expense = summary['total_expense']
        
        # 计算恩格尔系数（食品支出占总支出的比例）
        # 这里简单模拟，实际应用中需要更精确的分类
        food_expense = sum(r['amount'] for r in records 
                          if r['type'] == 'expense' and 
                          any(keyword in r['description'].lower() for keyword in ['food', '餐饮', '吃饭', '食品', '超市']))
        
        # 平均消费倾向 APC = 消费/收入
        apc = total_expense / total_income if total_income > 0 else 0
        
        # 恩格尔系数
        engel_coefficient = food_expense / total_expense if total_expense > 0 else 0
        
        # 简化的边际消费倾向计算
        # 按时间排序记录
        sorted_records = sorted(records, key=lambda x: x['date'])
        
        # 按月分组计算
        monthly_data = {}
        for record in sorted_records:
            month_key = record['date'][:7]  # YYYY-MM
            if month_key not in monthly_data:
                monthly_data[month_key] = {'income': 0, 'expense': 0}
            if record['type'] == 'income':
                monthly_data[month_key]['income'] += record['amount']
            else:
                monthly_data[month_key]['expense'] += record['amount']
        
        # 计算MPC（简化版）
        mpc = 0
        if len(monthly_data) > 1:
            # 计算收入变化和支出变化
            months = sorted(monthly_data.keys())
            income_changes = []
            expense_changes = []
            
            for i in range(1, len(months)):
                income_change = monthly_data[months[i]]['income'] - monthly_data[months[i-1]]['income']
                expense_change = monthly_data[months[i]]['expense'] - monthly_data[months[i-1]]['expense']
                
                if income_change > 0:  # 只有收入增加时才计算
                    income_changes.append(income_change)
                    expense_changes.append(expense_change)
            
            if income_changes:
                # MPC = 支出变化/收入变化
                mpc = sum(expense_changes) / sum(income_changes) if sum(income_changes) > 0 else 0
        
        return {
            'engel_coefficient': engel_coefficient,
            'avg_propensity_consumption': apc,
            'marginal_propensity_consumption': mpc
        }
    
    def get_economic_profile(self, records=None):
        """获取用户经济水平画像"""
        indicators = self.calculate_economic_indicators(records)
        
        if not indicators:
            return None
        
        # 生成经济画像描述
        profile = {
            'indicators': indicators,
            'analysis': self._generate_economic_analysis(indicators)
        }
        
        return profile
    
    def _generate_economic_analysis(self, indicators):
        """生成经济分析描述"""
        analysis = []
        
        # 恩格尔系数分析
        engel = indicators['engel_coefficient']
        if engel > 0.59:
            analysis.append(f"恩格尔系数为{engel:.2%}，处于贫困水平。食品支出占总支出比例较高，建议适当控制食品支出。")
        elif engel > 0.5:
            analysis.append(f"恩格尔系数为{engel:.2%}，处于温饱水平。食品支出占比较高，生活水平有待提高。")
        elif engel > 0.4:
            analysis.append(f"恩格尔系数为{engel:.2%}，处于小康水平。生活水平较为稳定。")
        elif engel > 0.3:
            analysis.append(f"恩格尔系数为{engel:.2%}，处于富裕水平。生活质量较高。")
        else:
            analysis.append(f"恩格尔系数为{engel:.2%}，处于最富裕水平。生活质量很高。")
        
        # APC分析
        apc = indicators['avg_propensity_consumption']
        if apc > 1:
            analysis.append(f"平均消费倾向为{apc:.2%}，消费超过收入，存在入不敷出的风险。")
        elif apc > 0.8:
            analysis.append(f"平均消费倾向为{apc:.2%}，消费比例较高，储蓄能力有限。")
        elif apc > 0.5:
            analysis.append(f"平均消费倾向为{apc:.2%}，消费和储蓄比例较为合理。")
        else:
            analysis.append(f"平均消费倾向为{apc:.2%}，消费比例较低，储蓄能力较强。")
        
        # MPC分析
        mpc = indicators['marginal_propensity_consumption']
        analysis.append(f"边际消费倾向为{mpc:.2%}，表示收入每增加1元，消费将增加{mpc:.2f}元。")
        
        return analysis