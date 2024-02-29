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
    return self._client[db_name][collection_name].insert_one(data).inserted_id
    

  def find_items(self, condition=None, db_name=None, collection_name=None):

  def find_item(self, condition=None, db_name=None, collection_name=None):

  def delete_items(self, condition=None, db_name=None, collection_name=None):

  def update_items(self, condition=None, update_value=None, db_name=None, collection_name=None):

  def update_item(self, condition=None, update_value=None, db_name=None, collection_name=None):

  def aggregate(self, pipeline=None, db_name=None, collection_name=None):

  def text_search(self, text=None, db_name=None, collection_name=None):

  
