from pymongo import MongoClient

db = ''


def connect():
    global db
    client = MongoClient()
    db = client['stocktwits']

connect()
print("Connected")