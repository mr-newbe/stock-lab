#이 코드는 기능별 유닛 테스트를 위한 코드입니다.

import unittest
from stocklab.agent.ebest import EBest
import inspect
import time

class TestEBest(unittest.TestCase):
  def setUp(self): #테스트케이스 호출 전
    self.ebest = EBest("DEMO")
    self.ebest.login()

  def tearDown(self): #테스트 케이스 수행 후 
    self.ebest.logout()
  #C:\stock-lab>workon stocklab
  #C:\stock-lab>python -m unittest tests.test_agent_ebest
  #로 단위 테스트 진행이 가능합니다. 
  def test_code_list(self):
    print(inspect.stack()[0][3])
    all_result = self.ebest.get_code_list("ALL")
    assert all_result is not None
    kosdaq_result = self.ebest.get_code_list("KOSDAQ")
    assert kosdaq_result is not None
    kospi_result = self.ebest.get_code_list("KOSPI")
    assert kospi_result is not None
    try:
      error_result = self.ebest.get_code_list("KOS")
    except:
      error_result = None
    assert error_result is None
    print("result:", len(all_result),len(kosdaq_result),len(kospi_result))

  #get_stock_price_list_by_code 메서드의 단위 테스트
  def test_get_stock_price_list_by_code(self):
    print(inspect.stack()[0][3])
    result =self.ebest.get_stock_price_by_code("005930","2")
    assert result is not None
    print(result)

  # 신용거래 동향 테스트(t1921)
  def test_get_credit_trend_by_code(self):
    print(inspect.stack()[0][3])
    result = self.ebest.get_credit_by_code("005930", "20190222")
    assert result is not None
    print(result)
  # 외인 기관별 종목별 동향 테스트(t1717)
  def test_get_short_trend_by_code(self):
    print(inspect.stack()[0][3])
    result = self.ebest.get_short_by_code("005930", sdate="20181201",edate="20181231")
    assert result is not None
    print(result)
  # 공매도 추이 테스트 (t1927)
  def test_get_agent_trend_by_code(self):
    print(inspect.stack()[0][3])
    result = self.ebest.get_agent_by_code("005930", fromdt="20181201", todt="20181231")
    assert result is not None
    print(result)
  
