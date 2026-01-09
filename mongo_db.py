from pymongo import MongoClient

client = MongoClient('mongodb+srv://AMV:AMV@outlook.itqomxm.mongodb.net/?appName=outlook')
db = client['EduGlobe']

users = db.users

def add_user(email: str, password: str, full_name: str) -> None:
    users.insert_one({
        'email': email,
        'password': password,
        'full_name': full_name
    })


def get_full_name(email: str) -> str | None:
    x = users.find_one({'email': email})
    if x:
        return x['full_name']


def validate_password(email: str, password: str) -> bool:
    x = users.find_one({'email': email})
    if x:
        if x['password'] == password:
            return True
    return False