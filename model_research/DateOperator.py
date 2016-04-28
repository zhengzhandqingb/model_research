# -*- coding: utf-8 -*-
__author__ = 'Administrator'
import time
import datetime
import calendar


class DateOperator(object):

    def months(self, time1, months):  # 这里的months 参数传入的是正数表示往后 ，负数表示往前
        dt=datetime.date(int(time1[0:4]), int(time1[5:7]), int(time1[8:10]))
        month = dt.month - 1 + months
        year = dt.year + month / 12
        month = month % 12 + 1
        day = min(dt.day,calendar.monthrange(int(year),int(month))[1])
        dt = dt.replace(year=int(year), month=int(month), day=int(day))
        return str(dt)

    def days(self, date, dayLengh):
        dateDate = time.strptime(date, "%Y-%m-%d")
        y,m,d = dateDate[0:3]
        dateDate = datetime.datetime(y, m, d)
        dayAgo = (dateDate + datetime.timedelta(days=dayLengh))
        dateStr = dayAgo.strftime("%Y-%m-%d")
        return dateStr

    def string_to_date(self,date_str):
        date_str = time.strptime(date_str, '%Y-%m-%d')
        y,m,d = date_str[0:3]
        date_str = datetime.datetime(y, m, d)
        return date_str

    def is_same_week(self, date_time1, date_time2):
        # year1 = date_time1[0:4]
        # year2 = date_time2[0:4]
        date_time1 = self.string_to_date(date_time1)
        date_time2 = self.string_to_date(date_time2)
        year1 = date_time1.year
        year2 = date_time2.year
        month1 = date_time1.month
        month2 = date_time2.month
        week1 = date_time1.isocalendar()[1]
        week2 = date_time2.isocalendar()[1]
        sub_year = year1 - year2
        if sub_year == 0:
            if week1 == week2:
                return 1
        elif sub_year == 1 and month2 == 12:
            if week1 == week2:
                return 1
        elif sub_year == -1 and month1 == 12:
            if week1 == week2:
                return 1
        return 0

