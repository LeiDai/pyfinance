import tushare as ts
import pandas as pd
from tushare.util import dateu as du
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import ffn as ffn
import sys

class Performance:
    def __init__(self, prices):
        self.prices = prices.dropna()
        self.daily_prices = self.prices.resample('D').last()       #resamples the prices as day
        self.monthly_prices = self.prices.resample('M').last()     #resamples the prices as month
        self.yearly_prices = self.prices.resample('A').last()      #resamples the prices as year
        self._name = self.prices.name
        self._start = self.prices.index[0]
        self._end = self.prices.index[-1]
        self._start_value = self.daily_prices[0]
        self._end_value = self.daily_prices[-1]
        self.ret = (self.prices / self.prices.shift(1) - 1).fillna(0)
        self.logret = np.log(self.daily_prices / self.daily_prices.shift(1))

    def total_ret(self):
        """
        :return: the return between end day to start day
        """
        return fmtp(self._end_value / self._start_value - 1)

    def daily_ret(self):
        """
        :return: day to day return
        """
        return self.ret

    def daily_cums_ret(self):

        return self.ret.cumsum()

    def utility(self, A):
        """
        refer to book: python for finance (2017)
        utility function: U = E(R) - 1/2 * A * sigma^2
        U is the utility function
        E(R) is the expected portfolio return and we could use its mean to approximate
        A is the risk-averse coefficient
        sigma^2 is the variance of the portfolio
        :param A: the risk-averse coefficient
        :return: the utility function
        """
        daily_ret_mean = sp.mean(self.ret)
        daily_ret_var = sp.var(self.ret)
        mean_annual = (1+daily_ret_mean)**252
        var_anaual = daily_ret_var*252
        U = mean_annual - 0.5 * A * var_anaual
        return U

    def log_ret(self):
        """
        :return: day to day log return
        """
        return fmtp(self.logret)

    def monthly_ret(self):
        """
        :return: the monthly return
        """
        _logret = self.logret.fillna(0)
        d = self.daily_prices.index
        n = len(d)
        ym = []
        logret_new = []
        for i in range(n):
            y = d[i].strftime("%Y")
            m = d[i].strftime("%m")
            ym.append(''.join([y, m]))
            logret_new.append(float(_logret[i]))
        result = pd.DataFrame(logret_new, ym, columns=['ret_monthly'])
        monthly_ret = result['ret_monthly'].astype(float).groupby(result.index).sum()
        return monthly_ret

    def yearly_ret(self):
        """
        :return: the yearly return
        """
        _logret = self.logret.fillna(0)
        d = self.daily_prices.index
        n = len(_logret)
        ym = []
        logret_new = []
        for i in range(n):
            y = d[i].strftime("%Y")
            ym.append(y)
            logret_new.append(float(_logret[i]))
        result = pd.DataFrame(logret_new, ym, columns=['ret_yearly'])
        yearly_ret = np.exp(result['ret_yearly'].astype(float).groupby(result.index).sum())-1
        return yearly_ret

    def sharpe(self, periods, rf=0.):
        """
        :param periods: it is the periods for sharp, 252 is for daily sharp, 12 is for month sharp
        :return: sharp
        """
        ret = self.ret
        if type(rf) is float and rf != 0 and periods is None:
            raise Exception('Must provide nperiods if rf != 0')
        elif type(rf) is float and periods is not None:
            _rf = np.power(1 + ret, 1. / periods) - 1.
        else:
            _rf = rf

        er = ret - _rf
        std = np.std(ret, ddof=1)
        if len(ret) < 2:
            srp = "----"
        else:
            srp = np.divide(er.mean(), std) * np.sqrt(periods)
        return fmtn(srp)

    def cagr(self):
        """
        Calculates the `CAGR (compound annual growth rate) <https://www.investopedia.com/terms/c/cagr.asp>`_ for a given price series.
        """
        return fmtp((self.daily_prices.iloc[-1] / self.daily_prices.iloc[0]) ** (1 / year_frac(self._start, self._end)) - 1)

    def max_drawdown(self):
        return fmtp(to_drawdown_series(self.daily_prices).min())

    def moving_average(self, window):
        ma = self.prices.rolling(window).mean()
        return ma


def fmtp(number):
    """
    Formatting helper - percent
    """
    if np.isnan(number):
        return '-'
    return format(number, '.2%')


def fmtpn(number):
    """
    Formatting helper - percent no % sign
    """
    if np.isnan(number):
        return '-'
    return format(number * 100, '.2f')


def fmtn(number):
    """
    Formatting helper - float
    """
    if np.isnan(number):
        return '-'
    return format(number, '.2f')


def year_frac(start, end):
    """
    Similar to excel's yearfrac function. Returns
    a year fraction between two dates (i.e. 1.53 years).

    Approximation using the average number of seconds
    in a year.

    Args:
        * start (datetime): start date
        * end (datetime): end date

    """
    if start > end:
        raise ValueError('start cannot be larger than end')

    # obviously not perfect but good enough
    return (end - start).total_seconds() / (31557600)


def to_drawdown_series(prices):
    """
    Calculates the `drawdown <https://www.investopedia.com/terms/d/drawdown.asp>`_ series.

    This returns a series representing a drawdown.
    When the price is at all time highs, the drawdown
    is 0. However, when prices are below high water marks,
    the drawdown series = current / hwm - 1

    The max drawdown can be obtained by simply calling .min()
    on the result (since the drawdown series is negative)

    Method ignores all gaps of NaN's in the price series.

    Args:
        * prices (Series or DataFrame): Series of prices.

    """
    # make a copy so that we don't modify original data
    drawdown = prices.copy()

    # Fill NaN's with previous values
    drawdown = drawdown.fillna(method='ffill')

    # Ignore problems with NaN's in the beginning
    drawdown[np.isnan(drawdown)] = -np.Inf

    # Rolling maximum
    roll_max = np.maximum.accumulate(drawdown)
    drawdown = drawdown / roll_max - 1.
    return drawdown
