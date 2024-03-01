import unittest, inspect
from stocklab.db_handler import MongoDBHandler
from pprint import pprint
import pymongo

class MongoDBHandlerTestCase(unittest.TestCase):
  def setUp(self):
    self.mongodb = MongoDBHandler()
    self.mongodb._client["stocklab_test"]["corp_info"].drop()
    docs = []

    self.mongodb._client["stocklab_test"]["corp_info"].insert_many(docs)

  def test_insert_item(self):
    print(inspect.stack()[0][3])
    doc={"item":"SamSung Card", "related":"SamSung", "qty":25,
        "tags":["green","red"], "accuont":[10, 11]}
    _id = self.mongodb.insert_item(doc, "stocklab_test", "corp_info")
    #assert 는 에러가 날 것 같은 곳에 작성하여 에러를 검출하는 코드입니다.
    assert _id
    print(_id)

  def test_insert_items(self):
    print(inspect.stack()[0][3])
    docs=[{"item":"SamSung Card", "related":"SamSung", "qty":25,
        "tags":["green","red"], "accuont":[10, 11]},
          {"item":"LG 화학", "related":"LG", "qty":25,
        "tags":["green","red"], "accuont":[10, 11]}]
    ids = self.mongodb.insert_items(docs, "stocklab_test", "corp_info")
    #assert 는 에러가 날 것 같은 곳에 작성하여 에러를 검출하는 코드입니다.
    assert ids
    print(ids)

  def test_find_item(self):
    print(inspect.stack()[0][3])
    doc = self.mongodb.find_item({"related":"LG"}, "stocklab_test", "corp_info")
    pprint(doc)
  def test_find_items(self):
    print(inspect.stack()[0][3])
    cursor = self.mongodb.find_items({"tags.1":"red"}, "stocklab_test", "corp_info")
    assert cursor
    for doc in cursor:
      pprint(doc)

  def test_delete_items(self):
    pprint(inspect.stack()[0][3])
    result = self.mongodb.delete_items({"related":"SamSung"}, "stocklab_test", "corp_info")
    assert result
    print(result.delete_count)
  
  def test_update_items(self):
    print(inspect.stack()[0][3])
    result = self.mongodb.update_items({"item":"LG Telecom"}, {"$set":{"qty":300}},"stocklab_test", "corp_info")
    assert result
    print("matched_count:" + str(result.match_count))
    print("modified_count:" + str(result.modified_count))

  def test_aggregate(test):
    print(inspect.stack()[0][3])
    pipeline = [
      {
        "$match":{
          "tags.1":"red"}
      },
      {
        "$group":{
          "_id":"$related",
        "sum_val":{"$sum":"$qty"}
        }
      }
      
    ]
    result = self.mongodb.aggregate(pipeline, "stocklab_test", "corp_info")
    assert result
    for item in result:
      pprint(item)
  
  def test_text_search(self):
    print(inspect.stack()[0][3])
    index_result = self.mongodb._client["stocklab_test"]["corp_info"].create_index([('item','text'), ('related', 'text'), ('tags', 'text')])
    print(index_result)
    assert result
    for item in result:
      pprint(item)
      
  def tearDown(self):
    pass


if __name__=="__main__":
  unittest_main()
