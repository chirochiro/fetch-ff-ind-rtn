import calendar
import datetime
import logging

def get_last_business_date(yyyymm: int):

    year = yyyymm // 100
    month = yyyymm % 100

    