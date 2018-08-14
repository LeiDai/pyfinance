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
import fund as fd
import performance as pf
import stock as stk


if __name__=='__main__':

    codes = ['002399', '000021', '600681']
    year_start = '19890101'
    k_indexs = ['get_profit_data', 'get_report_data', 'get_operation_data',
               'get_growth_data', 'get_debtpaying_data', 'get_cashflow_data']
    for code in codes:
        for k_index in k_indexs:
            a = stk.single_stock_report(code, year_start, k_index)
            a.to_excel("report\%s_%s_%s_to_today.xlsx" % (code, k_index, year_start))

    """
    f = ts.get_nav_open(fund_type='qdii')
    codes = f['symbol']
    n = len(codes)
    jjjc = []
    codes_new = []
    TotReturn = []
    mreturn = []
    sharpe = []
    cagr = []
    max_drawdown = []
    for i in range(1):
        code = codes[i]
        start = '20100101'
        #end = du.today()
        end = '20180805'
        s = fd.Fund(code, start, end)
        value = s.net_value()
        jjjc.append(s.jjjc()[0])
        perf = pf.Performance(value)
        codes_new.append(code)
        TotReturn.append(perf.total_ret())
        sharpe.append(perf.sharpe(periods=252, rf=0.))
        cagr.append(perf.cagr())
        max_drawdown.append(perf.max_drawdown())

    result = pd.concat([pd.DataFrame({"code": codes_new}),
                        pd.DataFrame({"total return": TotReturn}),
                        pd.DataFrame({"daily sharpe": sharpe}),
                        pd.DataFrame({"cagr": cagr}),
                        pd.DataFrame({"max_drawdown": max_drawdown})], axis=1)
    result.to_excel('the performance for all fund type of qdii.xlsx')
    """