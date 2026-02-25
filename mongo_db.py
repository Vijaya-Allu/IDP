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


def get_completed_topics(email: str) -> list[str]:
    x = users.find_one({'email': email}, {'_id': 0, 'completed_topics': 1})
    if not x:
        return []
    completed_topics = x.get('completed_topics', [])
    if isinstance(completed_topics, list):
        return completed_topics
    return []


def set_topic_completion(email: str, topic_id: str, completed: bool) -> None:
    if completed:
        users.update_one(
            {'email': email},
            {'$addToSet': {'completed_topics': topic_id}}
        )
    else:
        users.update_one(
            {'email': email},
            {'$pull': {'completed_topics': topic_id}}
        )
