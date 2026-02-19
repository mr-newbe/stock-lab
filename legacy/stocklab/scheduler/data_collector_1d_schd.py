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


#스케줄러에서 실행할 메서드들, 이 둘은 프로세스를 생성합니다.
#p.start()를 호출하는 순간부터 각 프로세스는 개별로, 다른 스레드에서 동작하게 됩니다.
#멀티프로세싱에 대해서는 나중에 더 찾아보고 공부하도록 합시다.
def run_process_collect_code_list():
  print(inspect.stack()[0][3])
  p = Process(target = collect_code_list)
  p.start()
  p.join()
  
def run_process_collect_stock_list():
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

    result_credit = ebest.get_credit_trend_by_code(code, today)
    if len(result_credit) > 0:
      mongodb.insert_items(result_price, "stocklab", "credit_info")

    result_short = ebest.get_short_trend_by_code(code, sdate=today, edate=today)
    if len(result_short)>0:
      mongodb.insert_items(result_short, "stocklab", "short_info")

    result_agent = ebest.get_agent_trend_trend_by_code(code, fromdt=today, todt=today)
    if len(result_agent)>0:
      mongodb.insert_items(result_agent, "stocklab", "agent_info")

#BackgroundScheduler 객체를 생성하고 add_jog 메서드를 통해 실행할 함수를 지정합니다. 
#실행할 함수는 보다시피,  run_process_collect_code_list, run_process_collect_stock_info 입니다.
#블로그에 작성한 것처럼 스케줄러가 시간을 인지하는 방법인 cron 을 인식시켜주고 입력합시다. 
# "python -m stocklab.scheduler.data_collector_1d_schd"로 실행하고 크론으로 지정한 시간이 되면 데이터를 수집하는 코드를 실행함
if __name__=='__main__':
  scheduler = BackgroundScheculer()
  scheculer.add_job(func=run_process_collect_code_list, trigger="cron",
                   day_of_week="mon-fri", hour="22", minute="36", id="1")
  scheduler.add_job(func=run_process_collect_stock_info, trigger="cron",
                   day_of_week="mon-fri", hour="19", minute="00", id="2")
  scheduler.start()
  #프로세스가 정상적으로 동작하고 있는지 확인하기 위한 while 문
  while True:
    print("running", datetime.now())
    time.sleep(1)
