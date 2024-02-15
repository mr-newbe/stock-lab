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
