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

  
