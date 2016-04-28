__author__ = 'Administrator'
import redis


class RedisOperator(object):

    def __init__(self):
        # self.host = '10.100.138.13'
        self.host = 'localhost'
        self.port = 6379
        self.write_pool = {}

    def add_write(self, date, value):
        key = date
        val = value
        self.write_pool[key] = val

    def batch_write(self):
        try:
            r = redis.StrictRedis(host=self.host, port=self.port)
            r.mset(self.write_pool)
        except Exception as exception:
            print(exception)

    def read(self, date):
        try:
            key = date
            r = redis.StrictRedis(host=self.host, port=self.port)
            value = r.get(key)
            return value
        except Exception as exception:
            print(exception)

    def batch_write_hashed(self, type1):
        try:
            r = redis.StrictRedis(host=self.host, port=self.port)
            r.hmset(type1, self.write_pool)
        except Exception as exception:
            print(exception)

    def read_hashed(self, type1, startTime, endTime):
        try:
            r = redis.StrictRedis(host=self.host, port=self.port)
            oneFinanceData = r.hgetall(type1)
            financeData = dict()
            for d, x in oneFinanceData.items():
                d = d.decode()
                x = x.decode()
                if  d >= startTime and d <= endTime:
                    financeData[d] = x
            return financeData
        except Exception as exception:
            print(exception)

