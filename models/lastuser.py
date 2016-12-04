from database import BaseModel
from peewee import ForeignKeyField, CharField

from .user import User


class LastUser(BaseModel):
    user = ForeignKeyField(User, related_name="lastusers")
    lastfm_user = CharField()

    def __str__(self):
        return self.lastfm_user
