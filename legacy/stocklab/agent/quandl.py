import quandl

quandl.ApiConfig.api_key = ""
data=quandl.get('BCHARTS/BITFLYERSD', start_date='2019-03-07', end_date=''2019-03-07)

print(data)
