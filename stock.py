# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 16:46:52 2018

@author: Ronald.Dai
"""

import tushare as ts
import pandas as pd
from tushare.util import dateu as du
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import ffn as ffn
import sys
import datetime
import time
import calendar
import re


class Stock:
    """

        Methods:

        Attributes:

        Usage:

        """

    def __init__(self, code, start, end, k_type, src):
        self.code = code
        self.start = start
        self.end = end
        self.k_type = k_type
        self.src = src
        self.stock_hist_data = ts.get_k_data(code=self.code, start=self.start, end=self.end, ktype=self.k_type)
        self.stock_hist_single_data = ts.get_tick_data(code=self.code, date=self.end, src=self.src)

    def stock_data(self, k_index):
        """
        :param k_index: the k_index can be:
                   1: open
                   2: high
                   3: close
                   4: low
                   5: volume
                   6: amount
                   7: turnoverratio
                   8: code
        :return: the data to be captured for k_index and code during start to end
        """
        index_list = ['open', 'high', 'close','low', 'volume', 'amount', 'turnoveratio', 'code']
        if k_index not in index_list:
            raise Exception('invalid k_index - the setting is not in the scope')
        data = self.stock_hist_data
        data['date'] = pd.to_datetime(data['date'])
        new_data = data.set_index(['date'])
        return new_data['%s'  % k_index]

    def single_stock_data(self, k_index):
        """
        :param k_index:
                   1: time
                   2: price
                   3: change
                   4: volume
                   5: amount
                   6: type
        :return: the result based on the setting of k_index
        """
        index_list = ['price', 'change', 'volume', 'amount', 'type']
        if k_index not in index_list:
            raise Exception('invalid k_index - the setting is not in the scope')
        data = self.stock_hist_single_data
        data['time'] = pd.to_datetime(data['time'])
        new_data = data.set_index(['time'])
        return new_data['%s'  % k_index]


def stock_list(k_index):
    """
    :param k_index: the k_index can be:
    1: name
    2: industry
    3: area
    4: pe
    5: outstanding
    6: totals
    7: totalAssets
    :return: the data to be captured for k_index and for all codes, code is the index of return results
    """

    index_list = ['name', 'industry',
                  'area', 'pe', 'outstanding',
                  'totals', 'totalAssets', 'liquidAssets',
                  'fixedAssets', 'reserved', 'reservedPerShare',
                  'eps', 'bvps', 'pb', 'timeToMarket']
    if k_index not in index_list:
        raise Exception('invalid k_index - the setting is not in the scope')
    data = ts.get_stock_basics()
    return data[k_index]


def stock_report(year, quarter, k_index):
    """
        :param k_index: the k_index can be:
        1: name
        2: eps
        3: eps_yoy
        4: bvps
        5: roe
        6: epcf
        7: net_profits
        8: profits_yoy
        9: distrib
        10: report_data
        :return: the data to be captured for k_index and for all code, code is the index of return result
    """

    index_list = ['name', 'eps', 'eps_yoy', 'bvps', 'roe', 'epcf',
                  'net_profits', 'profits_yoy', 'distrib', 'report_date']
    if k_index not in index_list:
        raise Exception('invalid k_index - the setting is not in the scope')
    if  year <= 0:
        raise Exception('invalid year that should be larger than 0')
    if quarter <= 0 and quarter > 4:
        raise Exception('invalid quarter that we just 4 quarter in market')
    data = ts.get_report_data(year, quarter)
    new_data = data.set_index(['code'])
    return new_data[k_index]


def single_stock_report(code, year_start, k_index):
    """
    :param code: the valid stock code, for example '002146'
    :param year_start: the start date that we want to check the stock report, for example '201801'
    :param k_index: the performance of report we want to check
    :return: DataFrame table: the index is the quarter from start to end, the
    """

    if code is None:
        raise ValueError('please assign code')
    if year_start is None:
        raise ValueError('please assign year')
    if k_index is None:
        raise ValueError('please assign index')

    year_to_market = stock_list('timeToMarket')
    ytm = year_to_market[year_to_market.index == code]
    ytm = str(ytm.iloc[0])
    if ytm >= year_start:
        qs = getBetweenQuarter(ytm)
    else:
        qs = getBetweenQuarter(year_start)
    j = len(qs)-1
    results = pd.DataFrame()
    new_index = []
    for i in range(j):
        year = int(qs[i].split('Q')[0])
        q = int(qs[i].split('Q')[1])
        n = 1
        data = []
        while n < 10:
            if k_index == 'get_profit_data':
                data = ts.get_profit_data(int(year), q)
            elif k_index == 'get_report_data':
                data = ts.get_report_data(int(year), q)
            elif k_index == 'get_operation_data':
                data = ts.get_operation_data(int(year), q)
            elif k_index == 'get_growth_data':
                data = ts.get_growth_data(int(year), q)
            elif k_index == 'get_debtpaying_data':
                data = ts.get_debtpaying_data(int(year), q)
            elif k_index == 'get_cashflow_data':
                data = ts.get_cashflow_data(int(year), q)
            else:
                raise Exception('the k_indexs is not correct')
            result = data[data['code'] == code]
            if len(result) >= 1:
                new_index.append('%d0%d' % (year, q))
                results = results.append(result[0:1], ignore_index=True)
                print(results)
                break
            elif len(result) == 0:
                n += 1
                continue
    new_index_1 = pd.DataFrame({"Y_Q":new_index})
    frames = [results, new_index_1]
    return pd.concat(frames, axis=1)


def getBetweenMonth(begin_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y%m%d")
    end_date = datetime.datetime.strptime(time.strftime('%Y%m%d', time.localtime(time.time())), "%Y%m%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y%m")
        date_list.append(date_str)
        begin_date = add_months(begin_date, 1)
    return date_list


def add_months(dt, months):
    month = dt.month - 1 + months
    year = dt.year + month / 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def getBetweenQuarter(begin_date):
    quarter_list = []
    month_list = getBetweenMonth(begin_date)
    for value in month_list:
        if value[4:6] in ['01', '02', '03']:
            quarter_list.append(value[0:4] + "Q1")
        elif value[4:6] in ['04', '05', '06']:
            quarter_list.append(value[0:4] + "Q2")
        elif value[4:6] in ['07', '08', '09']:
            quarter_list.append(value[0:4] + "Q3")
        elif value[4:6] in ['10', '11', '12']:
            quarter_list.append(value[0:4] + "Q4")
    quarter_set = set(quarter_list)
    quarter_list = list(quarter_set)
    quarter_list.sort()
    return quarter_list

