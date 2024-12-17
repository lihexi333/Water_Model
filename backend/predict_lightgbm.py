import numpy as np
import pandas as pd
import lightgbm as lgb
import datetime
import urllib,urllib3
import json
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

def calculate_changes(data):
    """计算水位变化量"""
    return np.diff(data)

def create_dataset(data, lookback=14, forecast=7):
    """
    创建滑动窗口数据集
    data: 水位变化量数据
    lookback: 用于预测的历史天数 
    forecast: 预测未来的天数
    """
    X, y = [], []
    for i in range(len(data) - lookback - forecast + 1):
        X.append(data[i:(i + lookback)])
        y.append(data[(i + lookback):(i + lookback + forecast)])
    return np.array(X), np.array(y)

def train_predict(data_path):
    """
    训练LightGBM模型预测水位变化量
    data_path: 数据文件路径,包含日期和水位两列的CSV文件
    """
    # 读取数据
    df = pd.read_csv(data_path)
    water_levels = df['water_level'].values  # 假设水位列名为'water_level'
    
    # 计算水位变化量
    changes = calculate_changes(water_levels)
    
    # 创建数据集
    X, y = create_dataset(changes)
    
    # 检查 X 和 y 的长度是否匹配
    if len(X) != len(y):
        raise ValueError(f"X 和 y 的长度不匹配: X 长度 = {len(X)}, y 长度 = {len(y)}")
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 确保 y_train 和 y_test 是一维数组
    y_train = y_train.flatten()
    y_test = y_test.flatten()
    
    # 检查 y_train 和 y_test 的长度是否匹配 X_train 和 X_test
    if len(y_train) != len(X_train) or len(y_test) != len(X_test):
        raise ValueError(f"y_train 和 y_test 的长度与 X_train 和 X_test 不匹配: y_train 长度 = {len(y_train)}, X_train 长度 = {len(X_train)}, y_test 长度 = {len(y_test)}, X_test 长度 = {len(X_test)}")
    
    # 确保 X_train 和 y_train 的长度匹配
    if len(X_train) != len(y_train):
        raise ValueError(f"训练数据长度不匹配: X_train 长度 = {len(X_train)}, y_train 长度 = {len(y_train)}")
    
    # 确保 X_test 和 y_test 的长度匹配
    if len(X_test) != len(y_test):
        raise ValueError(f"测试数据长度不匹配: X_test 长度 = {len(X_test)}, y_test 长度 = {len(y_test)}")
    
    # 定义LightGBM参数 - 针对变化量预测调整
    params = {
        'objective': 'regression',
        'metric': 'mse',
        'learning_rate': 0.05,  # 降低学习率以获得更稳定的预测
        'num_leaves': 31,
        'min_data_in_leaf': 20,
        'feature_fraction': 0.8,
        'bagging_fraction': 0.8,  # 添加bagging以减少过拟合
        'bagging_freq': 5
    }
    
    # 创建数据集格式
    train_data = lgb.Dataset(X_train, y_train)
    valid_data = lgb.Dataset(X_test, y_test, reference=train_data)
    
    # 训练模型
    callbacks = [lgb.early_stopping(stopping_rounds=20)]
    model = lgb.train(params,
                      train_data,
                      num_boost_round=200,  # 增加迭代次数
                      valid_sets=[valid_data],
                      callbacks=callbacks)
    
    # 预测并评估
    predictions = model.predict(X_test)
    
    mse = mean_squared_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    
    print(f'变化量预测的均方误差: {mse:.4f}')
    print(f'变化量预测的平均绝对误差: {mae:.4f}')
    
    return model

def predict_next_week(model, last_14_days_levels):
    """
    预测未来7天的水位变化量
    model: 训练好的模型
    last_14_days_levels: 最近14天的水位数据
    """
    # 计算最近14天的变化量
    changes = calculate_changes(last_14_days_levels)
    
    # 预测未来7天的变化量
    changes = changes.reshape(1, -1)
    predicted_changes = model.predict(changes)[0]
    
    # 根据最后一天的水位和预测的变化量计算未来7天的水位
    last_level = last_14_days_levels[-1]
    predicted_levels = [last_level]
    for change in predicted_changes:
        predicted_levels.append(predicted_levels[-1] + change)
    
    return predicted_levels[1:], predicted_changes



if __name__ == "__main__":
    # 修正文件扩展名和路径格式
    data_path = "D:/360MoveData/Users/bradlynn/Desktop/学校事务/大创/water_model/backend/reservoir_data.csv"
    model = train_predict(data_path)
    
    # 假设这是最近14天的水位数据
    last_14_days = [60.16, 60.14, 60.22, 60.43, 60.46, 60.4, 60.33, 60.33, 60.15, 60.07, 59.39, 59.92, 60.33, 60.14]
    predicted_levels, predicted_changes = predict_next_week(model, last_14_days)
    
    print("\n预测结果:")
    print("未来7天预测的水位变化量:", [f"{x:.2f}" for x in predicted_changes])
    print("未来7天预测的水位:", [f"{x:.2f}" for x in predicted_levels])
