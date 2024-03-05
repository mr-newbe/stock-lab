import configparser #config.ini 파일을 읽기 쉽게 해주고 만드는것도 해주는 라이브러리
import win32com.client
import pythoncom

#이 객체는 사용자의 연결 상태정보를 관리하기 위한 객체입니다.
class XASession : 
  #TR의 xingAPI를 사용한 조회 횟수 제한
  #10분에 200회의 제한이 있다
  QUERY_LIMIT_10MIN = 200
  LIMIT_SECONDS = 600 #10MIN


  
  #로그인 상태를 확인하기 위함
  login_state = 0

  #두가지 이벤트 구현
  def OnLogin(self, code, msg):
    #로그인 시도 후 호출되는 이벤트, code=0000은 로그인 성공
    if code == "0000":
      print(code, msg)
      XASession.login_state = 1
    else:
      #실패시 원인 분석
      print(code, msg)
  
  def OnDisconnect(self):
    #서버 연결 끊어지면 발생
    print("Session disconnected")
    XASession.login_state = 0
  


class EBest:

  def __init__(self,mode=None):
    """
    config.ini파일을 로드해 사용자 및 서버 정보 저정
    query_cnt는 10분당 200개의 TR 수행을 관리하기 위한 리스트
    xa_session_client는 XASession객체
    :param mode:str - 모의서버는 DEMO 실서버는 PROD로 구분
    """
    if mode not in ["PROD","DEMO"]:
      raise Exception("Need to run_mode(PROD OR DEMO)")


    run_mode = "EBESt_"+mode
    config = configparser.ConfigParser()
    config.read('conf/config.ini')
    self.user = config[run_mode]['user']
    self.passwd = config[run_mode]
    self.cert_passwd = config[run_mode]['cert_passwd']
    self.host = config[run_mode]['host']
    self.port = config[run_mode]['port']
    self.account = config[run_mode]['account']



    self.xa_session_client = win32com.client.DispatchWithEvents("XA_Session.XASession",XASession)
    self.query_cnt = []


  def _execute_query(self, res, in_block_name, out_block_name, *out_fields, **set_fields): #가변적으로 인자 전달하기 위한 위치 인자 *
   # **는 키워드 인자로서 키-값 형태의 인자를 전달할 때 사용합니다. set_fields = {"a":1,"b":2,"c":3} 일 때 **set_fields 로 받아온 여기에서 set_field["c"] == 3이 되는 것입니다.
    
    """
     TR 코드를 실행하기 위한 메서드이다.
     :param res:str 리소스 이름(TR)
     :param in_block_name:str 인 블록 이름
     :param out_block_name:str 인 아웃블록 이름
     :param out_params:list 출력 필드 리스트
     :param in_params:dict 인 블록에 설정할 필드 딕셔너리
     :return result:list 결과를 list에 담아서 반환
    """
    time.sleep(1)

    print("current query cnt:",len(self.query_cnt))
    print(res, in_block_name, out_block_name)

    #현재 리스트의 갯수, query_cnt가 QUERY_LIMIT_10MIN = 200을 넘었다면 time.sleep으로 1초간 정지
    while len(self.query_cnt) >= EBest.QUERY_LIMIT_10MIN:
      time.sleep(1)
      print("waiting for execute query... current query cnt:", len(self.query_cnt))

      #갯수가 초과되어 일시정지 되었다면 리스트 내부에 대해 filter를 통해 600가 넘지 않는 요소들만 query_cnt에 담습니다.
      #방법은 filter(lambda x : a - x < n, t)을 통해서 t라는 배열의 각 요소의 값에 대해 a에서 뺀 값이 n 보다 작으면 살려준다는 코드입니다.
      #기능을 정리하자면 리스트 개수가 200개를 넘지 않으면 while을 통과, 코드가 진행되지만 넘는다면 ==> 1초 기다리고 호출된지 10분 지난 시각 정보를 제거하는 과정을 반복합니다.
      self.query_cnt = list(filter(lambda x:(datetime.today() - x).total_seconds() < EBest.LIMIT_SECONDS, self.query_cnt)) 
      
    #xaQuery 객체를 만들고 LoadFromResFile 메서드를 이용해 리소스 파일을 불러옴
    xa_query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQuery)
    xa_query.LoadFromResFile(XAQuery.RES_PATH + res + ".res")

    #in_block_name 세팅
    #tr을 하기 전에 필요한 값들을 채우는 과정
    for key, value in set_fields.items():
      xa_query.SetFieldData(in_block_name, key, 0, value)
    errorCode = xa_query.Request(0)

    waiting_cnt = 0
    # TR의 실행을 기다리는 while 문의 실행 10000번 당 한번씩 기다리란 문구 출력
    while xa_query.tr_tun_state == 0:
      waiting_cnt += 1
      if waiting_cnt % 100000 == 0:
        print("Waiting....", self.xa_session_client.GetLastError())
      pythoncom.PumpWaitingMessage()
    
    #결과 블록
    # 결과가 몇개인지 확인한다.
    result= []
    count = xa_query.GetBlockCount(out_block_name)

    # out_fields(이 메서드의 매개변수)에 정의해놓은 필드의 값들만을 가져오는 코드
    for i in range(count):
      item={}
      for field in out_fields:
        value = xa_query.GetFieldData(out_block_name, field, i)
        item[field] = value
      result.append(item)
    
    #제약 시간 체크
    XAQuery.tr_run_state = 0
    self.query_cnt.append(datetime.today())

    #영문 필드명을 한글 필드명으로 변환
    #결과의 item별로, 그리고 각 항목의 필드명을 리스트로 가져옴
    for item in result:
      for field in list(item.keys())
      # TR별 필드명을 정의해놓은 Field에서 res라는 영문 필드명이 보인다면 그 값을, 없다면 None을...
        if getattr(Field, res, None):
          res_field = getattr(Field, res, None)
          #getattr 메서드로 수행하려는 res가 Field 속성에 있는지 확인하고 있다면 field_hname으로 저장
          if out_block_name in res_field:
            field_hname = res_field[out_block_name]
            #item의 각 영문 필드명인 field가 field_hname에 있는지 확인하고, 있으면 field_hname[field]로 item에 한글 필드명을 저장함
            if field in field_hname:
              item[field_hname[field]] = item[field]
              item.pop(field)

    return result



  #t8436 주식 종목 조회 메서드
  def get_code_list(self, markey=None):
    """
    TR : t8436  코스피, 코스닥의 종목 리스트를 가져온다
    : param market : str 전체(0), 코스피(1), 코스닥(2)
    """
    if market != "ALL" and market != "KOSPI" and market != "KOSDAQ":
      raise Exception("Need to market param(All, Kospi, Kosdaq)")

    market_code = {"ALL":"0", "KOSPI":"1","KOSDAQ":"2"}
    in_params = {"gubun":market_code[market]}
    out_params = ['hname', 'shcode', 'expcode', 'etfgubun', 'memedam', 'gubun', 'spac_guban']
    result = self._execute_query("t8436",
                                 "t8436InBlock",
                                 "t8436OutBlock",
                                 *out_params,
                                 **in_params
                                )
    return result

  #t1305 기간별 주가 메서드
  def get_stock_price_by_code(self, code=None, cnt="1"):
    """
    TR : t1305 현재 날짜를 기준으로 cnt 만큼 전일의 데이터를 가져온다.
    :param code:str
    :param cnt:str 이전 데이터 조회 범위(일단위)
    :return result:list 종목의 최근 가격 정보
    """
    in_params = {"shcode":code, "dwmcode":"1", "date":"","cnt":cnt}
    out_params = ['date', 'open','high', 'low', 'close', 'sign',
                  'change', 'diff', 'volume', 'diff_vol', 'chdegree',
                  'value', 'ppvolume', 'o_sign', 'o_change', 'o_diff',
                  'h_sign', 'h_change', 'h_diff', 'l_sign', 'l_change',
                  'l_diff', 'marketcap']
    result = self._execute_query("t1305",
                                "t1305InBlock",
                                "t1305OutBlock1",
                                *out_params,
                                **in_params)
    for item in result:
      #밑의 코드를 대체하는 방법으론 
      #item.update({'code':code})
      #item.update(code=code) 등이 있다고 합니다.
      item["code"] = code
    return result

  #신용거래 동향(t1921)
  def get_credit_trend_by_code(self, code=None, date=None):
    """
    TR:t1921 신용거래 동향
    :param code:str 종목코드
    :param date:str 날짜 ex/20231213
    """
    in_params = {"gubun":"0", "shcode":code, "date":date, "idx" :"0"}
    out_params = ["mmdate","close","sign","jchange","diff","nvolume",
                 "svolume","jvolume","price","change","gyrate","jkrate",
                 "shcode"]

    result = self._execute_query("t1921", 
                                 "t1921InBlock",
                                 "t1921OutBlock1",
                                 *out_params,
                                 **in_params)

    for item in result:
      item["code"] = code
    return result

  
  #외인 기관별 종목별 동향(t1717)
  def get_agent_trend_by_code(self, code=none, fromdt=None, todt=None):
    """
    TR : t1717 외인 기관별 종목별 동향
    :param code:str 종목 코드
    :param fromdt:str 조회 시작 날짜
    :param todt:str 조회 종료 날짜
    :return result:list 시장별 종목 리스트
    """
    in_params = {"gubun":"0","fromdt":fromdt, "todt":todt,"shcode":code}
    outparams = ["date","close", "sign","change","diff","volume",
                "tjj0000_vol","tjj0001_vol","tjj0002_vol","tjj0003_vol","tjj0004_vol",
                "tjj0005_vol","tjj0006_vol","tjj0007_vol","tjj0008_vol",
                "tjj0009_vol","tjj0010_vol","tjj00011_vol","tjj0012_vol",
                "tjj0013_vol","tjj0014_vol","tjj0015_vol","tjj0016_vol","tjj0017_vol",
                "tjj0000_dan","tjj0001_dan","tjj0002_dan","tjj0003_dan","tjj0004_dan",
                "tjj0005_dan","tjj0006_dan","tjj0007_dan","tjj0008_dan",
                "tjj0009_dan","tjj0010_dan","tjj00011_dan","tjj0012_dan",
                "tjj0013_dan","tjj0014_dan","tjj0015_dan","tjj0016_dan","tjj0017_dan"]
    result = self._execute_query("t1717",
                                "t1717InBlock",
                                "t1717OutBlock",
                                *out_params,
                                **in_params)
    for item in result:
      item["code"] = code
    return result

  #공매도 추이(t1927) 메서드
  def get_short_trend_by_code(self, code=None, sdate=None, edate=None):
    """
    TR: t1927 공매도 일별 추이
    :param code:str 종목 코드
    :param sdate:str 시작 일자
    :param edate:str 종료 일자
    :return result:list 시장 별 종목 리스트
    """
    in_params = {"date":sdate, "sdate":sdate, "edate":edate, "shcode":code}
    out_params = ["date","price","sign","change","diff","volume","value",
                 "gm_vo","gm_va","gm_per","gm_avg","gm_vo_sum"]

    result = self._execute_query("t1927",
                                "t1927InBlock",
                                "t1927OutBlock",
                                *out_params,
                                **in_params)

    for item in result:
      item["code"] = code
    return result

  def get_account_info(self):
    """
    TR: CSPAQ12200 현물계좌 예수금/주문가능금액/총평가
    :return result:list Field SCPAQ12200 참고
    """

    in_params = {"RecCnt":1, "AcntNo":self.account, "Pwd":self.passwd}
    out_params = ["MnyOrdAbleAmt", "BalEvalAmt", "DpsastTotamt", "InvstOrgAmt", "InvstPlAmt", "Dps"]

    result = self._execute_query("CSPAQ12200",
                                "CSPAQ12200InBlock1",
                                "CSPAQ12200OutBlock2",
                                *out_params,
                                **in_params)
    return result

  #계좌의 보유 주식 종목을 조회하는 API
  def get_account_stock_info(self):
    """
    TR: CSPAQ12300 현물계좌 잔고내역 조회
    :return result:list 계좌 보유 종목 정보
    """
    in_params = {"RecCnt":1, "AcntNo":self.account, "Pwd":self.passwd, "BalCreTp":"0",
                "CmsnAppTpCode":"0", "D2balBaseQryTp":"0", "UprcTpCode":"0"}
    out_params = ["IsuNo", "IsuNm", "BalQty", "SellPrc", "BuyPrc", "NowPrc", "AvrUprc", "BalEvalAmt", "PrdayCprc"]

    result = self._execute_query("CSPAQ12300",
                                "CSPAQ12300InBlock1",
                                "CSPAQ12300OutBlock3",
                                *out_params,
                                **in_params)
    return result

  def order_stock(self, code, qty, price, bns_type, order_type):
    """
    TR:CSPAT00600 현물 정상 주문
    :param bns_type:str 매매타입, 1:매도, 2:매수
    :param order_type:str 호가유형,
    00:지정가, 03:시장가, 05:조건부지정가, 07:최우선지정가,
    61:장개시전시간외 종가, 81:시간외종가, 82:시간외단일가
    :return result:dict 주문 관련 정보
    """
    in_params = {"AcntNo":self.account, "InptPwd":self.passwd, "IsuNo":code, "OrdQty":qty,
                "OrdPrc":price, "BnsTpCode":bns_type, "OrdprcPtnCode":order_type, "MgntrnCode":"000", "LoanDt":"", "OrdCndiTpCode":"0"} 
    out_params = ["OrdNo", "OrdTime", "OrdMktCode", "OrdPtnCode", "ShtnIsuNo", "MgempNo",
                 "OrdAmt", "SpotOrdQty", "IsuNm"]

    result = self._execute_query("CSPAT00600",
                                "CSPAT00600InBlock1",
                                "CSPAT00600OutBlock2",
                                *out_params,
                                **in_params)

    return result

  def order_cancle(self, order_no, code, qty):
    """
    TR:CSPAT00800 현물 취소주문
    :param order_no:str 주문번호
    :param code:str 종목코드
    :param qty:str 취소 수량
    :return result:dict 취소 결과
    """
    in_params = {"OrgOrdNo":order_no, "AcntNo":self.account, "InptPwd":self.passwd,
                "IsuNo":code, "OrdQty":qty}
    out_arams = ["OrdNo", "PrntOrdNo", "Ordtime", "OrdPtncode", "IsuNm"]

    result = self._execute_qurey("CSPAT00800",
                                "CSPAT00800InBlock1",
                                "CSPAT00800OutBlock2",
                                *out_params,
                                **in_params)
    return result

  #주식 체결, 미체결 API
  def order_check(self, order_no):
    """
    TR:t0425 주식 체결/미체결
    :param code:str 종목코드
    :param order_no:str 주문번호
    :return result:dict 주문번호의 체결상태
    """
    
    in_params = {"accno":self.account, "passwd":self.passwd, "expcode":code, "chegb":"0","medosu":"0","sortgb":"1", "cts_ordno":" "}
    
    out_params = ["ordno", "expcode", "medosu", "qty", "price", "cheqty", "cheqty", "cheprice", "ordrem",
                 "cfmqty", "status", "status", "orgordno", "ordgb", "ordermtd", "sysprocseq", "hogagb", "price1", "orggb",
                 "singb", "loandt"]

    result_list = self._execute_query("t0425",
                                     "t0425InBlock",
                                     "t0425OutBlock1",
                                     *out_params,
                                     **in_params)
    result={}
    if order_no is not None:
      for item in result_list:
        if item["주문번호"] == order_no:
          result = item
      return result
    else:
      return result_list

  #주식 현재가 호가 조회의 API
  def get_current_call_price_by_code(self, code=None):
    """
    TR:t1101 주식 현재가 호가 조회
    :param code:str 종목코드
    """
    tr_code="t1101"
    in_params = {"shcode":code}
    out_params =["hname", "price", "sign", "change", "diff", "volume", 
            "jnilclose", "offerho1","bidho1", "offerrem1", "bidrem1",
            "offerho2","bidho2", "offerrem2", "bidrem2",
            "offerho3","bidho3", "offerrem3", "bidrem3",
            "offerho4","bidho4", "offerrem4", "bidrem4",
            "offerho5","bidho5", "offerrem5", "bidrem5",
            "offerho6","bidho6", "offerrem6", "bidrem6",
            "offerho7","bidho7", "offerrem7", "bidrem7",
            "offerho8","bidho8", "offerrem8", "bidrem8",
            "offerho9","bidho9", "offerrem9", "bidrem9",
            "offerho10","bidho10", "offerrem10", "bidrem10",
            "preoffercha10", "prebidcha10", "offer", "bid",
            "preoffercha", "prebidcha", "hotime", "yeprice", "yevolume",
            "yesign", "yechange", "yediff", "tmoffer", "tmbid", "ho_status",
            "shcode", "uplmtprice", "dnlmtprice", "open", "high", "low"]

    result = self._execute_query("t1101", 
                                "t1101InBlock", 
                                "t1101OutBlock",
                                *out_params,
                                **in_params)


    
    for item in result:
      item["code"] = code
    return result

  #호가 단위 조회 메서드 구현
  def get_tick_size(self, price):
    """
    호가 단위 조회 메서드
    :param price:int 가격
    :return 호가 단위
    """
    if price < 1000: return 1
    elif price >=1000 and price < 5000: return 5
    elif price >=5000 and price < 10000: return 5
    elif price >=10000 and price < 50000: return 5
    elif price >=50000 and price < 100000: return 5
    elif price >=100000 and price < 500000: return 5
    elif price >=500000: return 1000

  
  def login(self):
    self.xa_session_client.connectServer(self.host, self.port)
    self.xa_session_client.Login(self.user, self.passwd, self.cert_passwd, 0,0)
    while XASession.login_state == 0:  #로그인될 때까지 기다림
      pythoncom.PumpWaitingMessages()

  def logout(self):
    #result = self.xa_session_client.Logout()
    #if result:
    XASession.login_state = 0
    self.xa_session_client.DisconnectServer()

class XAQuery:
  RES_PATH = "C:\\eBest\\xingAPI\\Res\\"
  tr_run_state = 0
  #요청한 API에 대해 데이터를 수신했을 때 발생하는 이벤트
  def OnReceiveData(self,code):
    print("OnReceiveData",code)
    XAQurey.tr_run_state = 1
  #요청한 API에 대해 메시지(성공, 실패)를 받았을 때 발생하는 이벤트
  def OnReceiveMessage(self, error, code, message):
    print("OnReceiveMessage",error, code, message)



class Field:
  #t1101의 데이터 추가
  t1101 = {
        "t1101OutBlock":{
            "hname":"한글명",
            "price":"현재가",
            "sign":"전일대비구분",
            "change":"전일대비",
            "diff":"등락율",
            "volume":"누적거래량",
            "jnilclose":"전일종가",
            "offerho1":"매도호가1",
            "bidho1":"매수호가1",
            "offerrem1":"매도호가수량1",
            "bidrem1":"매수호가수량1",
            "preoffercha1":"직전매도대비수량1",
            "prebidcha1":"직전매수대비수량1",
            "offerho2":"매도호가2",
            "bidho2":"매수호가2",
            "offerrem2":"매도호가수량2",
            "bidrem2":"매수호가수량2",
            "preoffercha2":"직전매도대비수량2",
            "prebidcha2":"직전매수대비수량2",
            "offerho3":"매도호가3",
            "bidho3":"매수호가3",
            "offerrem3":"매도호가수량3",
            "bidrem3":"매수호가수량3",
            "preoffercha3":"직전매도대비수량3",
            "prebidcha3":"직전매수대비수량3",
            "offerho4":"매도호가4",
            "bidho4":"매수호가4",
            "offerrem4":"매도호가수량4",
            "bidrem4":"매수호가수량4",
            "preoffercha4":"직전매도대비수량4",
            "prebidcha4":"직전매수대비수량4",
            "offerho5":"매도호가5",
            "bidho5":"매수호가5",
            "offerrem5":"매도호가수량5",
            "bidrem5":"매수호가수량5",
            "preoffercha5":"직전매도대비수량5",
            "prebidcha5":"직전매수대비수량5",
            "offerho6":"매도호가6",
            "bidho6":"매수호가6",
            "offerrem6":"매도호가수량6",
            "bidrem6":"매수호가수량6",
            "preoffercha6":"직전매도대비수량6",
            "prebidcha6":"직전매수대비수량6",
            "offerho7":"매도호가7",
            "bidho7":"매수호가7",
            "offerrem7":"매도호가수량7",
            "bidrem7":"매수호가수량7",
            "preoffercha7":"직전매도대비수량7",
            "prebidcha7":"직전매수대비수량7",
            "offerho8":"매도호가8",
            "bidho8":"매수호가8",
            "offerrem8":"매도호가수량8",
            "bidrem8":"매수호가수량8",
            "preoffercha8":"직전매도대비수량8",
            "prebidcha8":"직전매수대비수량8",
            "offerho9":"매도호가9",
            "bidho9":"매수호가9",
            "offerrem9":"매도호가수량9",
            "bidrem9":"매수호가수량9",
            "preoffercha9":"직전매도대비수량9",
            "prebidcha9":"직전매수대비수량9",
            "offerho10":"매도호가10",
            "bidho10":"매수호가10",
            "offerrem10":"매도호가수량10",
            "bidrem10":"매수호가수량10",
            "preoffercha10":"직전매도대비수량10",
            "prebidcha10":"직전매수대비수량10",
            "offer":"매도호가수량합",
            "bid":"매수호가수량합",
            "preoffercha":"직전매도대비수량합",
            "prebidcha":"직전매수대비수량합",
            "hotime":"수신시간",
            "yeprice":"예상체결가격",
            "yevolume":"예상체결수량",
            "yesign":"예상체결전일구분",
            "yechange":"예상체결전일대비",
            "yediff":"예상체결등락율",
            "tmoffer":"시간외매도잔량",
            "tmbid":"시간외매수잔량",
            "ho_status":"동시구분",
            "shcode":"단축코드",
            "uplmtprice":"상한가",
            "dnlmtprice":"하한가",
            "open":"시가",
            "high":"고가",
            "low":"저가"
        }
    }

  CSPAQ12200 = {
    "CSPAQ12200OutBlock2":{
      "MnyOrdAbleAmt":"현금주문가능금액",
      "BalEvalAmt":"잔고평가금액",
      "InvstOrgAmt":"투자원금"
      "InvstPlAmt":"투자손익금액",
      "Dps":"예수금"
    }
  }

  CSPAT00600 = {
    "CSPAT00600OutBlock2":{
      "RecCnt":"레코드갯수",
      "OrdNo":"주문번호",
      "OrdTime":"주문시각",
      "OrdMktCode":"주문시장코드",
      "OrdPtnCode":"주문유형코드",
      "ShtnIsuNo":"단축종목번호",
      "MgempNo":"관리사원번호",
      "OrdAmt":"주문금액",
      "SpareOrdNo":"예비주문번호",
      "CvrgSeqno":"반대매매일련번호",
      "RsvOrdNo":"예약주문번호",
      "SpotOrdQty":"실물주문수량",
      "RuseOrdQty":"재사용주문수량",
      "MnyOrdAmt":"현금주문금액",
      "SubstOrdAmt":"대용주문금액",
      "RuseOrdAmt":"재사용주문금액",
      "AcntNm":"계좌명",
      "IsuNm":"종목명"
    }
  }

  CSPAT00800 = {
    "CSPAT00800OutBlock2":{
      "RecCnt":"레코드갯수",
      "OrdNo":"주문번호",
      "PrntOrdNo":"모주문번호",
      "OrdTime":"주문시각",
      "OrdMktCode":"주문시장코드",
      "OrdPtnCode":"주문유형코드",
      "ShtnIsuNo":"단축종목번호",
      "PrgmOrdprcPtnCode":"프로그램호가유형코드",
      "StslOrdprcTpCode":"공매도호가구분",
      "StslAbleYn":"공매도가능여부",
      "MgntrnCode":"신용거래코드",
      "LoanDt":"대출일",
      "CvrgOrdTp":"반대매매주문구분",
      "LpYn":"유동성공급자여부",
      "MgempNo":"관리사원번호",
      "BnsTpCode":"매매구분",
      "SpareOrdNo":"예비주문번호",
      "CvrgSeqno":"반대매매일련번호",
      "RsvOrdNo":"예약주문번호",
      "AcntNm":"계좌명",
      "IsuNm":"종목명"
    }
  }

  t0425 ={
    "t0425OutBlock1":{
      "ordno":"주문번호",
      "expcode":"종목번호",
      "medosu":"구분",
      "qty":"주문수량",
      "price":"주문가격",
      "cheqty":"체결수량",
      "cheprice":"체결가격",
      "ordrem":"미체결잔량",
      "cfmqty":"확인수량",
      "status":"상태",
      "orgordno":"원주문번",
      "ordgb":"유형",
      "ordtime":"주문시간",
      "ordermtd":"주문매체",
      "sysprocseq":"처리순번",
      "hogagb":"호가유형",
      "price1":"현재가",
      "orggb":"주문구분",
      "singb":"신용구분",
      "loandt":"대출일자"
    }
  }
  



"""
우리가 만들고 있는 프로그램은, 주식 거래 프로그램입니다.
즉 영용문을 만들고 있다고 생각하면 편할 것입니다.

주식 종목 조회, 기간별 주가, 신용 거래 동향, 외인 기관별 종목별 동향, 공매도 추이 등 몇가지 TR을 구현한다고 합니다.
"""



  
