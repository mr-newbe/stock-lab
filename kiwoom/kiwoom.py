from PyQt5.QAxContainer import *
from PyQt5.QtCore import *


class Kiwoom(QAxWidget):
  def __init__(self):
    super().__init__()
    print("Kiwoom() class start")


    self.get_ocx_instance() # ocx 방식을 파이썬에서 사용할 수 있게 반환
    self.event_slots() # 키움과 연결하기 위한 시그널/슬롯 모음
    self.signal_login_commConnect() # 로그인 요청 함수 포함
    self.login_event_loop = QEventLoop() # 로그인 요청용 이벤트 루프



  def get_ocx_instance(self):
    self.setControl("KHOPENAPI.KHOpenAPICtrl.1") # 레지스터리의 모듈 불러오기


  def event_slots(self): # 로그인 관련 이벤트
    self.OnEventConnect.connect(self.login_slot)


  def login_slot(self, err_code): 
    print(errors(err_code)[1])


    # 로그인 처리 완료 시 이벤트 루프 종료
    self.login_event_loop.exit() 

  


