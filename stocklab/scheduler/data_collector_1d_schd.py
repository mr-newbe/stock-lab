#선행으로 pip install apschecudler  터미널에 입력

#이 라이브러리는 여러 종류의 스케줄러를 제공하는데, apscheculer는 
#실행하는 job에 대한 정보를 저장하고 복원하기 쉽게 스케줄 정보를 저장, 복원해 사용할 수 있다고 합니다.

"""
사용한 스케줄러는 apscheduler에서 제공하는 BackgroundScheduler를 사용하는데,
BackGroundScheduler를 사용해 EBest 모듈을 호출하게 되면 정상적으로 동작하지 않는다고 합니다.

EBest가 win32com 패키지를 사용하면서 내부적으로 프로세스와 관련된 동작을 하는데, 
이 때 BackgroundScheduler에서 win32com이 정상적으로 호출되지 않는다고 합니다.

이를 위한 방법으로 책은 멀티 프로세싱으로 별도의 프로세스를 하나 더 생성하여 EBest 모듈을 수행한다고 합니다.

그 방법을 책에선 그림으로 설명했는데, 이를 간단히 요약해보자면

각자 다른 메서드를 여러개의 프로세서를 통해 동시에 수행하는 방법입니다...이게 왜 효과 있는지는 잘 모르겠지만
"""
import time 
import inspect
from multiprocessing import Process
from datetime import datetime

from apscheduler.scheculers.background import BackgroundScheduler

from stocklab.agent.ebest import EBest
from stocklab.agent.data import Data
from stocklab.db_handler.mongodb_handler import MongoDBHandler

def run_process_collect_code_list():
  print(inspect.stack()[0][3])
  p = Process(target = collect_code_list)
  p.start()
  p.join()
  
def run_process_collect_code_list():
  print(inspect.stack()[0][3])
  p = Process(target = collect_stock_info)
  p.start()
  p.join()
  


def collect_code_list():
  ebest = EBest("DEMO")
  mongodb = MongoDBHandler()
  ebest.login()
  result = ebest.get_code_list("ALL")
  mongodb.delete_items({], "stocklab", "code_info")
  mongodb.insert_items(result, "stocklab", "code_info")


def collect_stock_info():
  ebest = EBest("DEMO")
  mongodb = MongoDBHandler()
  ebest.login()
  code_list = mongodb.find_items({}, "stocklab", "code_info")
  target_code = set([item["단축코드"] for item in code_lsit])
  today = datetime.today().strftime("%Y%m%d")
  print(today)
  collect_list = mongodb.find_items({"날짜":today}, "stocklab", "price_info").distinct("code")

  for col in collect_list:
    target_code.remove(col)
  for code in target_code:
    time.sleep(1)
    print("code:",code)
    result_price = ebest.get_stock_price_by_code(code, "1")
    if len(result_price)>0:
      print(result_price)
      mongodb.insert_items(result_price, "stocklab", "price_info")
