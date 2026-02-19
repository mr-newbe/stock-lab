import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from stocklab.agent.ebest import EBest
from stocklab.db_handler.mongodb_handler import MongoDBHandler
from multiprocessing import Process

ebest_demo = EBest("DEMO")
ebest_demo.login()
mongo = MongoDBHandler()


def run_process_trading_scenario(code_list):
  p = Process(target=trading_scenario, args=(code_list,))
  p.start()
  p.join()
  print("run process join")

#매수완료 데이터를 가져오고 호가 * 10으로 매도주문
def check_buy_completed_order(code):
  """
  매수완료된 주문은 매도 주문
  """
  buy_completed_order_list = list(mongo.find_items({"&and":[
                                                  {"code":code},
                                                  {"status":"buy_completed"}
                                                ]},
                                                  "stocklab_demo", "order"))

  """
  매도주문
  """
  for buy_completed_order in buy_completed_order_list:
    buy_price = buy_completed_order["매수완료"]["주문가격"]
    buy_order_no = buy_completed_order["매수완료"]["주문번호"]
    tick_size = ebest_demo.get_tick_size(int(buy_price))
    print("tick_size", tick_size)
    #위에서 가져온 항목에 대하여 수량만큼 +10호가로 매도주문을 합니다.
    sell_price = int(buy_price) + tick_size*10
    sell_order = ebest_demo.order_stock(code, "2", str(sell_price), "1", "00")
    print("order_stock", sell_order)
    mongo.update_item({"매수완료.주문번호":buy_order_no},
                     {"&set":{"매도주문":sell_order[0], "status":"sell_ordered"}},
                     "stocklab_demo", "order")



#order_check 메서드를 이용해 체결수량이 주문 수량과 동일한지 확인, 같으면 매수완료료 Mongodb에 데이터 업데이트
def check_buy_order(code):
    """
    매수주문 완료 체크
    """
    #MongoDB에서 매수주문 데이터를 가져옵니다.
    order_list = list(mongo.find_items({"$and":[
                                        {"code":code},
                                        {"status":"buy_ordered"}]
                                       },
                                      "stocklab_demo", "order"))

    for order in order_list:
      time.sleep(1)
      code = order["code"]
      order_no = order["매수주문"]["주문번호"]
      order_cnt = order["매수주문"]["실물주문수량"]
      check_result = ebest_demo.order_check(order_no)
      print("check buy order result", check_result)
      result_cnt = check_result["체결수량"]
      if order_cnt == result_cnt:
        mongo.update_item({"매도주문.주무번호":order_no},
                         {"&set":{"매수완료":check_result, "status":"buy_completed"}},
                         "stocklab_demo", "order")
        print("매수완료", check_result)
    
    
    return len(order_list)

#매도주문이 수량만큼 체결되었는지 확인하고, 
#체결되었다면 매도 완료로 체결 정보를 저장합니다.
def check_sell_order(code):
    """
    매도주문 완료 체크
    """
    sell_order_list = list(mongo.find_items({"$and":[
                                        {"code":code},
                                        {"status":"sell_ordered"}]
                                       },
                                      "stocklab_demo", "order"))

    #체결되었다면 sell_completed로 업데이트(100line 참고)
    for order in sell_order_list:
      time.sleep(1)
      code = order["code"]
      order_no = order["매도주문"]["주문번호"]
      order_cnt = order["매도주문"]["실물주문수량"]
      check_result = ebest_demo.order_check(order_no)
      print("check sell order result", check_result)
      result_cnt = check_result["체결수량"]
      if order_cnt == result_cnt:
        mongo.update_item({"매도주문.주문번호":order_no},
                         {"&set":{"매도완료":check_result, "status":"sell_completed"}},
                         "stocklab_demo", "order")
        print("매도완료", check_result)
    
    return len(sell_order_list)



def trading_scenario(code_list):
  #3번 반복한다. code_list는 요소가 3가지이니
  for code in code_list:
    time.sleep(1)
    print(code)
    result = ebest_domo.get_current_call_price_by_code(code)
    current_price = result[0]["현재가"]
    print("current_price", current_price)
    """
    매수주문 체결확인
    """
    buy_order_cnt = check_buy_order(code)
    check_buy_completed_order(code)
    if buy_order_cnt == 0:
      """
      종목을 보유하고 있지 않는 경우 매수
      """
      order = ebest_demo.order_stock(code, "2", current_price, "2", "00")
      print("order_stock", order)
      order_doc = order[0]
      mongo.insert_item({"매수주문":order_doc, "code":code, "status":"buy_ordered"},
                       "stocklab_demo", "order")
    
    check_sell_order(code)


#시나리오 실행을 위하여 "python -m stocklab.scheduler.trading_5m"로
#시나리오를 실행한 다음에 mongo를 실행해 database를 확인해봅니다.
if __name__ == '__main__':
  scheduler = BackgroundScheduler()
  day = datetime.now() - timedelta(days=4)
  today = day.strftime("%Y%m%d")
  code_list = ["180640", "005930", "091990"]
  print("today:", today)
  #run_process_trading_scenario에 code_list 전달
  #interval이라고 적혀있는데, interval 5분 주기는 cron과 달리 
  #프로그램 시작 후 5분 뒤에 실행되는 차이점 있음
  scheduler.add_job(func=run_process_trading_scenario,
                   trigger="interval", minites=5, id="demo",
                   kwargs={"code_list":code_list})
  scheduler.start()
  while True:
    print("waiting...", datetime.now())
    time.sleep(1)
