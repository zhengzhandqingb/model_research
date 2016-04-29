# -*- coding: utf-8 -*-
__author__ = 'Administrator'


import requests
import json
from DateOperator import *
import numpy as np


class AssetDataOperator(object):

    def __init__(self):
        self.date_operator = DateOperator()

    # 获取资产数据
    def get_portfolio_data(self, assetStr, startDate, endDate):
        portfolioStr = requests.get('http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20%20%20'
                                    'yahoo.finance.historicaldata%20where%20%20'
                                    'symbol%20%20%20%20=%20%22'+assetStr+'%22%20and%20%20%20%20'
                                    'startDate%20=%20%22'+startDate+'%22%20and%20%20%20%20'
                                    'endDate%20%20%20=%20%22'+endDate+'%22&format=json&diagnostics=true&env='
                                    'store://datatables.org/alltableswithkeys&callback=')
        financeStr = json.loads(portfolioStr.text)
        financeDict = dict()
        financeSize = 0
        print(assetStr)
        if financeStr['query']['results'] == None:
            return None
        else:
            financeStr2 = financeStr['query']['results']['quote']
            financeSize = financeStr2.__len__()

        for x in range(financeSize):
            financeDict[financeStr['query']['results']['quote'][x]['Date']] = financeStr['query']['results']['quote'][x]['Adj_Close']
        return financeDict

     # 计算资产的周末收盘价
    def compute_weekend_data(self, asset_data):
        asset_data = sorted(asset_data.items())
        asset_weekend_date = dict()
        i = 0
        date1 = asset_data[i][0]
        i = i + 1
        while i < len(asset_data):
            date2 = asset_data[i][0]
            if self.date_operator.is_same_week(date1, date2) == 1:  # 如果是同一周
                date1 = date2
                i = i + 1
                continue
            else: # 如果不在同一周
                asset_weekend_date[date1] = asset_data[i-1][1]
                date1 = date2
            i = i + 1
        date2_1 = self.date_operator.string_to_date(date2)
        if date2_1.weekday() == 5:  # 如果最后一天是星期五
             asset_weekend_date[date2] = asset_data[len(asset_data)-1][1]
        return asset_weekend_date

    # 计算机资产收益率, 参数类型是字典dict
    def compute_asset_return_rate(self, asset_data):
        asset_rate = dict()
        # 如果资产数据是dict类型的话，需要对其进行排序；如果是list，就不需要。
        if type(asset_data) == dict:
            asset_data = sorted(asset_data.items())
        i = 0
        former_value = float(asset_data[i][1])
        i = i + 1
        while i < len(asset_data):
            current_value = float(asset_data[i][1])
            asset_rate[asset_data[i][0]] = (current_value - former_value)/former_value
            former_value = current_value
            i = i + 1
        return asset_rate

    # 计算资产的期望收益率
    def compute_expect_rate(self, asset_data):
        sum_data = 0
        for d, x in asset_data.items():
            sum_data = sum_data + x
        excepted_data = sum_data/len(asset_data)
        return excepted_data

    # 调整资产数据，使进行方差计算的两个资产的数据时间保持一致
    def adjust_data(self, asset_data1, asset_data2):
         asset_data1 = sorted(asset_data1.items())
         asset_data2 = sorted(asset_data2.items())
         i = 0
         j = 0
         position2 = []
         position1 = []
         while i < len(asset_data1) and j < len(asset_data2):
             date1 = asset_data1[i][0]
             date2 = asset_data2[j][0]
             if self.date_operator.is_same_week(date1, date2):
                 i = i + 1
                 j = j + 1
                 continue
             else:
                 if date1 > date2:
                     position2.append(j)
                     j = j + 1
                 else:
                     position1.append(i)
                     i = i + 1
         while i < len(asset_data1):
             position1.append(i)
             i = i + 1
         while j <len(asset_data2):
             position2.append(j)
             j = j + 1

         # 删除不匹配的数据
         x1 = 0
         y1 = 0
         for x in range(len(position1)):
             if x > 0:
                 position1[x] = position1[x] - x1
             asset_data1.pop(position1[x])
             x1 = x1 + 1
         for y in range(len(position2)):
             if y > 0:
                 position2[y] = position2[y] - y1
             asset_data2.pop(position2[y])
             y1 = y1 + 1

         return asset_data1, asset_data2

    # 计算资产协方差
    def compute_asset_variance(self, asset_data1, asset_data2):

        # asset_data11 = asset_data1.copy()
        # asset_data22 = asset_data2.copy()

        asset_list1, asset_list2 = self.adjust_data(asset_data1, asset_data2)  # 调整资产数据

        asset_rate1 = self.compute_asset_return_rate(asset_list1)  # 计算调整后的资产收益率
        asset_rate2 = self.compute_asset_return_rate(asset_list2)

        asset_rate_list1 = []
        asset_rate_list2 = []
        for d, x in asset_rate1.items():
            asset_rate_list1.append(x)
        for d, x in asset_rate2.items():
            asset_rate_list2.append(x)

        cov_matrix = np.cov(asset_rate_list1, asset_rate_list2)

        return cov_matrix[0][1]

















