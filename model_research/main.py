# -*- coding: utf-8 -*-
__author__ = 'Administrator'

from RedisOperator import *
from AssetDataOperator import *
import numpy as np
import matplotlib.pyplot as plt
import cvxopt as opt
from cvxopt import blas, solvers
import math


redisOperator = RedisOperator()
assetDateOperator = AssetDataOperator()
dateOperator = DateOperator()


def updateRedis(assetType, lengh):
    lengh1 = lengh
    currentDate = datetime.datetime.now()
    endDateStr = currentDate.strftime("%Y-%m-%d")
    startDateStr = ''
    assetData = dict()
    subAssetData = dict()
    while lengh1 > 0:
        lengh1 = lengh1 - 1
        startDateStr = dateOperator.months(endDateStr, -12)
        if lengh1 == 0:
            startDateStr = dateOperator.days(startDateStr, 2)
        subAssetData = assetDateOperator.get_portfolio_data(assetType, startDateStr, endDateStr)
        if subAssetData != None:
            for d, x in subAssetData.items():
                assetData[d] = x
            subAssetData.clear()
        endDateStr = dateOperator.days(startDateStr, -1)

    # 做相应资产的所有数据构成一个大的字符串
    asset_data_all_str = '['
    i = 0
    for d, x in assetData.items():
        i = i + 1
        asset_data_all_str = asset_data_all_str + '{' + '\"Date\"' + ':' + '\"' + d + '\"' + ',' + '\"Adj_Close\"' + ':' + '\"' + x + '\"' + '}'
        if i < len(assetData):
            asset_data_all_str = asset_data_all_str + ','
    asset_data_all_str = asset_data_all_str + ']'
    # redisOperator.batch_write_hashed(assetType)
    redisOperator.write_all(assetType, asset_data_all_str)


def extract_points(returns1, risks1, point_number):
    return_min = returns1[0]
    return_max = returns1[0]

    returns_point = [0.0] * point_number
    risks_point = [0.0] * point_number
    i = 0
    j = 0
    for x in range(len(returns1)):
        if return_min > returns1[x]:
            return_min = returns1[x]
            i = x
        if return_max < returns1[x]:
            return_max = returns1[x]
            j = x
    span1 = (return_max - return_min)/(point_number-1)
    returns_point[0] = returns1[i]
    risks_point[0] = risks1[i]
    returns_point[point_number - 1] = returns1[j]
    risks_point[point_number - 1] = risks1[j]
    for x in range(point_number-2):
        temp_point = return_min + span1 * (x+1)
        temp_distance = return_max - return_min  # 设为最大
        temp_index = 0
        for y in range(len(returns1)):  # 找到离temp_point距离最小的点
            if abs(temp_point - returns1[y]) < temp_distance:
                temp_distance = abs(temp_point - returns1[y])
                temp_index = y
        returns_point[x+1] = returns1[temp_index]
        risks_point[x+1] = risks1[temp_index]

    return returns_point, risks_point


def extract_one_point_weight(asset_size, returns1, weights1, point_number, point_no):
    return_min = returns1[0]
    return_max = returns1[0]

    weight_one_point = [0.] * asset_size
    i = 0
    j = 0
    for x in range(len(returns1)):
        if return_min > returns1[x]:
            return_min = returns1[x]
            i = x
        if return_max < returns1[x]:
            return_max = returns1[x]
            j = x
    span1 = (return_max - return_min)/(point_number-1)
    # returns_point[0] = returns1[i]
    # risks_point[0] = risks1[i]
    # returns_point[point_number - 1] = returns1[j]
    # risks_point[point_number - 1] = risks1[j]

    temp_point = return_min + span1 * point_no
    temp_distance = return_max - return_min  # 设为最大
    temp_index = 0
    for y in range(len(returns1)):  # 找到离temp_point距离最小的点
        if abs(temp_point - returns1[y]) < temp_distance:
            temp_distance = abs(temp_point - returns1[y])
            temp_index = y
    weight_one_point = weights1[temp_index]

    return weight_one_point.T


def fun1(asset_type_str, end_date, year_len, point_number, point_no):

    asset_number = asset_type_str.__len__()
    assetDatas = [dict() for i in range(asset_number)]  # 资产数据
    asset_weekend_data = [dict() for i in range(asset_number)]  # 资产周末数据
    asset_week_rate = [dict() for i in range(asset_number)]  # 资产周末收益率
    asset_expected_rate = [0.0] * asset_number  # 资产周收益率的期望
    asset_cov = [[0.]*asset_number for x in range(asset_number)]

    # 获取资产数量
    start_date = dateOperator.months(end_date, -12*year_len)

    for x in range(len(asset_type_str)):
        # 从redis读取数据
        assetDatas[x] = redisOperator.read_from_redis(asset_type_str[x], start_date, end_date)
        # 获取每个周末的收盘价
        asset_weekend_data[x] = assetDateOperator.compute_weekend_data(assetDatas[x])
        # 计算每个资产的周收益率
        asset_week_rate[x] = assetDateOperator.compute_asset_return_rate(asset_weekend_data[x])
        # 计算每个资产的期望收益率
        asset_expected_rate[x] = assetDateOperator.compute_expect_rate(asset_week_rate[x])

    # 计算协方差矩阵
    asset_number2 = asset_number
    for x in range(asset_number):
        for y in range(asset_number2):
            asset_cov[x][y] = assetDateOperator.compute_asset_variance(asset_weekend_data[x], asset_weekend_data[y])
        # if x < asset_number-1:
        #     continue

    # 计算markowitz 优化模型
    # Turn off progress printing
    solvers.options['show_progress'] = False

    n = asset_number
    N = 100
    mus = [10**(5.0 * t/N - 1.0) for t in range(N)]

    # Convert to cvxopt matrices
    S = opt.matrix(asset_cov)

    pbar = opt.matrix(asset_expected_rate)

    G = -opt.matrix(0.0, (n*2, n))
    y = 0
    for x in range(n*2):
        if x % 2 != 0:
            G[x-1, y] = 1.0
            G[x, y] = -1.0
            y = y + 1

    # 设置每个资产的权重范围
    h = [0.4,-0.05, 0.4,-0.05, 0.4,-0.05, 0.4,-0.0, 0.4,-0.05, 0.4,-0.05, 0.4,-0.05, 0.4,-0.05]
    h = opt.matrix(h)

    A = opt.matrix(1.0, (1, n))
    b = opt.matrix(1.0)

    # Calculate efficient frontier weights using quadratic programming
    portfolios = [solvers.qp(mu*S, -pbar, G, h, A, b)['x'] for mu in mus]
    ## CALCULATE RISKS AND RETURNS FOR FRONTIER
    returns = [blas.dot(pbar, x) for x in portfolios]
    risks = [np.sqrt(blas.dot(x, S*x)) for x in portfolios]

    portfolio_return_year = [0.] * len(returns)
    portfolio_variance_Year = [0.] * len(risks)

    for x in range(len(returns)):
        portfolio_return_year[x] = math.pow(returns[x] + 1, 52) - 1
    for x in range(len(risks)):
        portfolio_variance_Year[x] = risks[x] * math.sqrt(52)

    # 提取相应序号的点的权重向量
    weight_point = extract_one_point_weight(asset_number, portfolio_return_year, portfolios, point_number, point_no)

    return weight_point


def fun2():
    # 获取资产数量
    asset_number = asset_type_str.__len__()

    assetDatas = [dict() for i in range(asset_number)]  # 资产数据
    asset_weekend_data = [dict() for i in range(asset_number)]  # 资产周末数据
    asset_week_rate = [dict() for i in range(asset_number)]  # 资产周末收益率
    asset_expected_rate = [0.0] * asset_number  # 资产周收益率的期望
    asset_cov = [[0.]*asset_number for x in range(asset_number)]

    for x in range(asset_type_str.__len__()):
        # 从redis读取数据
        assetDatas[x] = getdataFromRedis(asset_type_str[x], '2013-04-22', '2016-04-22')
        # 获取每个周末的收盘价
        asset_weekend_data[x] = assetDateOperator.compute_weekend_data(assetDatas[x])
        # 计算每个资产的周收益率
        asset_week_rate[x] = assetDateOperator.compute_asset_return_rate(asset_weekend_data[x])
        # 计算每个资产的期望收益率
        asset_expected_rate[x] = assetDateOperator.compute_expect_rate(asset_week_rate[x])

    # 计算协方差矩阵
    for x in range(asset_number):
        for y in range(asset_number):
            asset_cov[x][y] = assetDateOperator.compute_asset_variance(asset_weekend_data[x], asset_weekend_data[y])
        if x < asset_number-1:
            continue

    # ----------------------计算markowitz 优化模型---------------------------
    # Turn off progress printing
    solvers.options['show_progress'] = False

    n = asset_number
    #returns = np.asmatrix(returns)

    N = 1000
    mus = [10**(5.0 * t/N - 1.0) for t in range(N)]

    # Convert to cvxopt matrices
    S = opt.matrix(asset_cov)

    # print('协方差矩阵：')
    # print(S)

    pbar = opt.matrix(asset_expected_rate)
    # print('期望收益：')
    # print(pbar)

    # Create constraint matrices
    # G = -opt.matrix(np.eye(n))   # negative n x n identity matrix
    # G = -opt.matrix(np.eye(n*2))
    # G = [[0.0]*n for x in range(n*2)]
    G = -opt.matrix(0.0, (n*2, n))
    y = 0
    for x in range(n*2):
        if x % 2 != 0:
            G[x-1, y] = 1.0
            G[x, y] = -1.0
            y = y + 1

    # print('G值：')
    # print(G)


    #h = opt.matrix(0.0, (n ,1))
    # 设置每个资产的权重范围
    h = [0.4,-0.05, 0.4,-0.05, 0.4,-0.05, 0.4,-0.0, 0.4,-0.05, 0.4,-0.05, 0.4,-0.05, 0.4,-0.05]
    h = opt.matrix(h)

    # print('H值：')
    # print(h)

    A = opt.matrix(1.0, (1, n))
    b = opt.matrix(1.0)

    # Calculate efficient frontier weights using quadratic programming
    portfolios = [solvers.qp(mu*S, -pbar, G, h, A, b)['x'] for mu in mus]
    ## CALCULATE RISKS AND RETURNS FOR FRONTIER
    returns = [blas.dot(pbar, x) for x in portfolios]
    risks = [np.sqrt(blas.dot(x, S*x)) for x in portfolios]

    portfolio_return_year = [0.] * len(returns)
    portfolio_variance_Year = [0.] * len(risks)

    for x in range(len(returns)):
        portfolio_return_year[x] = math.pow(returns[x] + 1, 52) - 1
    for x in range(len(risks)):
        portfolio_variance_Year[x] = risks[x] * math.sqrt(52)

    # portfolio_return_year = Math.pow(1+portfolioMean,52)-1;
    # portfolio_variance_Year = portfolioVariance*Math.sqrt(52);

    # print(portfolio_return_year)
    # print(portfolio_variance_Year)

    for x in portfolios:
        print(x)

    # 提取分布均匀的9个点
    return_points, risk_points = extract_points(portfolio_return_year, portfolio_variance_Year, 9)

    #plt.plot(stds, means, 'o')
    plt.ylabel('mean')
    plt.xlabel('std')
    plt.plot(portfolio_variance_Year, portfolio_return_year, 'y-o')
    plt.plot(risk_points, return_points, 'o')
    plt.show()


  # assetTypeStr = ['VTI','VEA','VWO','VTIP','VCIT','BNDX','VNQ','FXI']
    # lengh1 = 5
    #
    # # /////////////////更新redis//////////////////
    # # for x in assetTypeStr:
    # #     updateRedis(x, lengh1)
    #
    # date_time = ['2015-03-01', '2015-06-01', '2015-09-01', '2015-12-01', '2016-03-01']
    # year_len = 3
    # point_number = 9
    # point_no = 0
    #
    # weights_date_time = [0.]*len(date_time)
    #
    # for x in range(len(date_time)):
    #     weights_date_time[x] = fun1(assetTypeStr, date_time[x], year_len, point_number, point_no)

    # for x in weights_date_time:
    #     for y in range(len(x)):
    #         print(x[y])

    # print('successful!!')


























