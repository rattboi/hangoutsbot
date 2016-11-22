from database import BaseModel
from peewee import ForeignKeyField, TextField, CharField

from .user import User


class Recommendation(BaseModel):
    id = CharField(primary_key=True)
    user = ForeignKeyField(User, related_name="recommendations")
    url = TextField()

    def __str__(self):
        return self.url

