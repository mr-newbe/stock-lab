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


  def _execute_query(self, res, in_block_name, out_block_name, *out_fields, **set_fields):
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
    while len(self.query_cnt) >= EBest.QUERY_LIMIT_10MIN:
      time.sleep(1)
      print("waiting for execute query... current query cnt:", len(self.query_cnt))
      self.query_cnt = list(filter(lambda x:(datetime.today() - x).total_seconds() < EBest.LIMIT_SECONDS, self.query_cnt))

    xa_query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQuery)
    xa_query.LoadFromResFile(XAQuery.RES_PATH + res + ".res")

    #in_block_name 세팅
    for key, value in set_fields.items():
      xa_query.SetFieldData(in_block_name, key, 0, value)
    errorCode = xa_query.Request(0)

    waiting_cnt = 0
    while xa_query.tr_tun_state == 0:
      waiting_cnt += 1
      if waiting_cnt % 100000 == 0:
        print("Waiting....", self.xa_session_client.GetLastError())
      pythoncom.PumpWaitingMessage()
    
    #결과 블록
    result= []
    count = xa_query.GetBlockCount(out_block_name)

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
    for item in result:
      for field in list(item.keys())
        if getattr(Field, res, None):
          res_field = getattr(Field, res, None)
          if out_block_name in res_field:
            field_hname = res_field[out_block_name]

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

  
