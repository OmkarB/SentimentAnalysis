from yahoo_finance import Share
import connect_to_mongo
import time
import datetime

index = '^GSPC'

db = connect_to_mongo.db


def rate_limit(max_per_second):
    min_int = 1.0 / float(max_per_second)

    def decorate(func):
        last_called = [0.0]

        def rate_limiter(*args, **kargs):
            elapsed = time.clock() - last_called[0]
            wait = min_int - elapsed
            if wait > 0:
                time.sleep(wait)
            ret = func(*args, **kargs)
            last_called[0] = time.clock()
            return ret

        return rate_limiter

    return decorate


@rate_limit(1 / 30)
def grab_finance_data():
    day_of_week = datetime.datetime.today().weekday()
    weekend_flag = False
    open_time = datetime.datetime(2015, 12, 4, 9, 30).time()
    close_time = datetime.datetime(2015, 12, 16).time()
    now = datetime.datetime.now().time()

    if day_of_week < 5:
        weekend_flag = True
        print("It's a weekday", day_of_week)

    while  open_time < now < close_time and weekend_flag:
        sp = Share(index)
        price = sp.get_price()
        timestamp = sp.get_trade_datetime()
        print(price, timestamp)
        db.SP500.insert({'time': timestamp, 'price': price})

grab_finance_data()

