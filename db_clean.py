# client
from pymongo import MongoClient

# var init
connection = MongoClient()
db = connection["img_forensic"]


# delete collection
def del_colection(collection_about):
    collection = db[collection_about]
    cursor = db.collection
    result = cursor.delete_many({})
    return result


# collection1 - imginfo : 이미지 정보 저장
collection_about = "imginfo"
result = del_colection(collection_about)
print(f"Document Count: {result.deleted_count}")
