import configparser
import win32com.client
import pythoncom

#이 객체는 사용자의 연결 상태정보를 관리하기 위한 객체입니다.
class XASession : 
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

    
