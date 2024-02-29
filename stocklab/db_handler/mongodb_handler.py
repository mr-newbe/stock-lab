from pymongo import MongoClient
from pymongo.cursor import CursorType
import configparser


class MongoDBHandler:
  def __init__(self):
    """
    Pymongo를 래핑(Wrapping)해서 사용하는 클래스
    """
    config = configparser.ConfigParser()
    config.read('conf/config.ini')
    host = config['MONGODB']['host']
    port = config['MONGODB']['port']

    self._client = MongoClient(host, int(port))

  def insert_item(self,data, db_name=None, collection_name=None):
    """
    MongoDB에 하나의 문서를 입력하기 위한 메서드
    :param datas:dict: 문서를 받는다.
    :param db_name:str: MongoDB 에서 데이터베이스에 해당하는 이름을 받는다
    :param collection_name:str: 데이터베이스에 속하는 컬렉션 이름을 받는다.
    :return inserted_id:str: 입력 완료된 문서의 ObjectID 를 반환
    :raises Exception: 매개변수 db_name과 collection_name이 없으면 예외 발생
    """
    if not isinstance(data, dict):
      raise Exception("data type should be dict")
    if db_name is None or collection_name is None:
      raise Exception("Need to param db_name, collection_name")
    #mongoDB의 모든 명령어는 self._client를 이용해서 수행함
    #insert_one은 MongoDB의 insertOne 명령어, inserted_id로 생생된 문서의 고유키(_id)가 반환됨
    return self._client[db_name][collection_name].insert_one(data).inserted_id

  def insert_items(self, datas, db_name=None, collection_name=None):
    """
    MongoDB에 여러개의 문서를 입력하기 위한 메서드이다.
    :parms datas:list 문서의 리스트를 받는다.
    :param db_names:str MongoDB에서 데이터베이스에 해당하는 이름을 받는다.
    :param collection_name:str 데이터베이스에 속하는 컬렉션 이름을 받는다.
    :return inserted_ids: 입력 완료된 문서의 ObjectId list 를 반환한다.
    :raise Exception: 매개변수 db_name과 collection_name 이없으면 예외 발생
    """
    if not isinstance(datas, list):
      raise Exception("data type should be list")
    if db_name is None or collection_name is None:
      raise Exception("Need to param db_name, collection_name")
    return self._client[db_name][collection_name].insert_many(datas).inserted_ids

  def find_item(self, condition=None, db_name=None, collection_name=None):
    """
    MongoDB에 하나의 문서를 검색하기 위한 메서드
    :param condition:dict: 검색 조건을 딕셔너리 형태로 받는다.
    :param db_name:str: MongoDB에서 데이터베이스에 해당하는 이름을 받는다.
    :param collection_name:str 데이터베이스에 속하는 컬렉션 이름을 받는다
    :return document:dict: 검색된 문서가 있으면 문서의 내용을 반환한다
    :raise Exception:  매개변수 db_name과 collection_name이 없으면 예외를 발생
    """
    if condition is None or not isinstance(condition, dict):
      condition={}
    if db_name is None or collection_name is None:
      raise Exception("Need to param db_name, collection_name")
    return self._client[db_name][collection_name].find_one(condition)
    
    

  def find_items(self, condition=None, db_name=None, collection_name=None):
    """
    MongoDB에 여러개의 문서를 검색하기 위한 메서드
    :param condition:dict: 검색 조건을 딕셔너리 형태로 받는다.
    :param db_name:str: MongoDB에서 데이터베이스에 해당하는 이름을 받는다.
    :param collection_name:str 데이터베이스에 속하는 컬렉션 이름을 받는다
    :return Cursor :  커서를 반환한다.
    :raise Exception:  매개변수 db_name과 collection_name이 없으면 예외를 발생
    """
    if condition is None or not isinstance(condition, dict):
      condition={}
    if db_name is None or collection_name is None:
      raise Exception("Need to param db_name, collection_name")
    return self._client[db_name][collection_name].find(condition,no_cursor_timeout=True,cursor_type=CursorType.EXHAUST)
    
  def delete_items(self, condition=None, db_name=None, collection_name=None):
    """
    MongoDB에 여러개의 문서를 삭제하기 위한 메서드
    :param condition:dict: 삭제 조건을 딕셔너리 형태로 받음
    :param db_name:str: Mongodb에서 데이터베이스에 해당하는 이름을 받음
    :param collection_name:str 데이터베이스에 속하는 컬렉션 이름 확인
    :return DeleteResult:obj PyMongo의 문서 삭제 결과 객체인 DeleteResult가 반환됨
    :raises Exception: 매개변수 db_name과 collection_name이 없으면 예외 발생
    """
    if condition is None or not isinstance(condition, dict):
      raise Exception("Need to condition")
    if db_name is None or collection_name is None:
      raise Exception("Need to param db_name, collection_name")
    return self._client[db_name][collection_name].delete_many(condition)

  def update_item(self, condition=None, update_value=None, db_name=None, collection_name=None, upsert=True):
    """
    MongoDB에 하나의 문서를 갱신하기 위한 메서드
    :param condition:dict: 갱신 조건을 딕셔너리 형태로 받는다.
    :param update_value:dict: 갱신하고자 한느 값을 딕셔너리 형태로 받는다.
    :param db_naem:str: MongoDB에서 데이터베이스에 해당하는 이름을 받는다.
    :param collection_name:str: 데이터베이스에 속하는 컬렉션 이름을 받는다.
    :return UpdateResult:obj  PyMongo의 문서 갱신 결과 UpdateResult 가 반환됩
    :raise Exception: 매개변수 db_name과 collection_name이 없으면 예외를 발생시킴
    """

    if condition is None or not isinstance(condition, dict):
      raise Exception("need to condition")
    if update_value is None:
      raise Exception("Need to update value")
    if db_name is None or collection_name is None:
      raise Exception("Need to param db_name, collection_name")
    return self._client[db_name][collection_name].update_one(filter=condition, update=update_value, upsert=True)
    

  def update_items(self, condition=None, update_value=None, db_name=None, collection_name=None):
    """
    MongoDB에 여러개의 문서를 갱신하기 위한 메서드
    :param condition:dict: 갱신 조건을 딕셔너리 형태로 받는다.
    :param update_value:dict: 갱신하고자 한느 값을 딕셔너리 형태로 받는다.
    :param db_naem:str: MongoDB에서 데이터베이스에 해당하는 이름을 받는다.
    :param collection_name:str: 데이터베이스에 속하는 컬렉션 이름을 받는다.
    :return UpdateResult:obj  PyMongo의 문서 갱신 결과 UpdateResult 가 반환됩
    :raise Exception: 매개변수 db_name과 collection_name이 없으면 예외를 발생시킴
    """

    if condition is None or not isinstance(condition, dict):
      raise Exception("need to condition")
    if update_value is None:
      raise Exception("Need to update value")
    if db_name is None or collection_name is None:
      raise Exception("Need to param db_name, collection_name")
    return self._client[db_name][collection_name].update.many(filter=condition, update=update_value)
    

  def aggregate(self, pipeline=None, db_name=None, collection_name=None):
    """
    MongoDB 의 aggregate 작업을 위한 메서드
    :param pipeline:list: 갱신 조건을 딕셔너리의 리스트 형태로 받는다
    :param db_name:str: MongoDB에서 데이터베이스에 해당하는 이름을 받음
    :param collection_name:str 데이터베이스에 속하는 컬렉션 이름을 반환
    :return CommandCursor:obj: PyMongo 의 ComandCursor가 반환됨
    :raise Exception: 매개변수 db_name과 collection_name이 없으면 예외를 발생시킴
    """
    if pipiline is None or not isinstance(pipeline, list):
      raise Exception("need to pipeline")
    if db_name is None or collection_name is None:
      raise Exception("Need to param db_name, collection_name")
    return self._client[db_name][collection_name].aggregate(pipeline)

  #$text, $search연산자로 매개변수를 전달받은 text를 찾아 커서를 반환
  def text_search(self, text=None, db_name=None, collection_name=None):
    if text is None or not isinstance(text, str):
      raise Exception("Need to text")
    if db_name is None or collection_name is None:
      raise Exception("Need to param db_name, collection_name")
    return self._client[db_name][collection_name].find({"$text":{"$search":text}})

  
