class XASession : 
  #로그인 상태를 확인하기 위함
  login_state = 0

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


