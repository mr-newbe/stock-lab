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
