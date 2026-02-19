from datetime time datetime
from stocklab.agent.ebest import EBest
from stocklab.db_handler.mongodb_handler import MongoDBHandler

#Ebest 커넥션 생성
ebest = EBest("DEMO")
ebest.login()

#MongoDB 커넥션 생성
mongodb = MongoDBHandler()

#mongoDB의 code_info 컬렉션을 모두 삭제하고 새로히 정보를 ebest에서 가져와 삽입
def collect_code_list():
  result = ebest.get_code_list("ALL")
  mongodb.delete_items({}, "stocklab", "code_info")
  mongodb.insert_items(result, "stocklab", "code_info")

#주식 가격을 수집하는 코드
def collect_stock_info():
  code_list = mongodb.find_items({}, "stocklab", "code_info")
  target_code = set([item["단축코드"] for item in code_list])
  
  #오늘 날짜로 수집된 데이터가 있다면 target_code에서 제외함
  #또한 최종 수집해야 하는 종목코드는 target_code에 저장됨
  today = datetime.today().strftime("%Y%m%d")
  collect_list = mongodb.find_items({"날짜":today}, "stocklab", "price_info").distinct("code")
  for col in collect_list:
    target_code.remove(col)
  #1일치 데이터를 가져온다. 그리고 수집된 데이터는 insert_items를 통해 price_info에 들어감
  for code in target_code:
    result_price = ebest.get_stock_price_by_code(code, "1")
    if len(result_price) > 0:
      mongodb.insert_items(result_price, "stocklab", "price_info")

if __name__ == '__main__':
  collect_code_list()
  collect_stock_info()
