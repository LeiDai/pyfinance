import tushare as ts
import pandas as pd
from tushare.util import dateu as du
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import ffn as ffn
import sys

class Fund:
    """

    Methods:

    Attributes:

    Usage:

    """
    
    def __init__(self, code, start, end):
        self.code = code
        self.start = start
        self.end = end
        self.result = ts.get_nav_history(code=self.code, start=self.start, end=self.end)
        self.info = ts.get_fund_info(code=self.code)

    def net_value(self):
        value = self.result['value'][::-1]
        return value
    
    def total_value(self):
        value = self.result['total'][::-1]
        return value

    def clrq(self):
        value = self.info['clrq']
        return value

    def jjqc(self):
        return self.info['jjqc']

    def jjjc(self):
        return self.info['jjjc']

    def ssrq(self):
        return self.info['ssrq']
