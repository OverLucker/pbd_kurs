import enum
from datetime import datetime

from bson import ObjectId

from globals import get_db


class ActiveRecord(object):
    collection = None
    id = None
    fields = ()

    def __init__(self, *args, **kwargs):
        self._id = None
        for name, val in kwargs.items():
            setattr(self, name, val)

    @classmethod
    def get(cls, object_id):
        db = get_db()
        return db[cls.collection].find_one({
            '_id': ObjectId(object_id)
        })

    @classmethod
    def all(cls, filters=None, limit=None):
        db = get_db()

        query = db[cls.collection]
        if filters is None:
            query = query.find({})
        else:
            query = query.find(filters)

        if limit is not None:
            query = query.limit(limit)

        return query

    def save(self):
        db = get_db()
        return db[self.collection].insert_one(self.to_json())

    def to_json(self):
        data = {
            field: getattr(self, field) for field in self.fields
        }
        if self._id:
            return dict({
                '_id': self._id,
                **data
            })

        return dict(data)

    @classmethod
    def from_json(cls, data):
        return cls(**data)


class User(ActiveRecord):
    collection = 'users'
    fields = (
        'first_name', 'last_name', 'middle_name',
        'username', 'password', 'phone', 'email'
    )

    first_name = None
    last_name = None
    middle_name = None

    username = None
    password = None

    phone = None
    email = None

    @classmethod
    def get_by_username(cls, username):
        db = get_db()
        return cls.from_json(
            db[cls.collection].find_one({
                'username': username
            })
        )

    @classmethod
    def login(cls, username, password):
        user = cls.get_by_username(username)
        if user and user.password == password:
            return user
        return None

    def logout(self):
        return None


class Event(ActiveRecord):
    collection = 'events'
    fields = (
        'sender', 'comment', 'type', 'date_send', 'date_register'
    )

    class EventType:
        LOGIN = 'заступил на пост'
        LOGOUT = 'сдал пост'

    class Type(enum.Enum):
        POLICE_CALL = 'вызвал полицию'
        RAIL_TROUBLES = 'угроза на рельсах'
        NUCLEAR_ALERT = 'ядерная угроза'

    sender = None
    comment = None
    type = None
    date_send = None
    date_register = None

    def __init__(self, *args, **kwargs):
        self.date_send = datetime.now()
        super().__init__(*args, **kwargs)

