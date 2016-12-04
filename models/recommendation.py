from database import BaseModel
from peewee import ForeignKeyField, CharField, TextField, DateTimeField

from .user import User


class Recommendation(BaseModel):
    user = ForeignKeyField(User, related_name="recommendations")
    artist = CharField()
    album = CharField()
    url = TextField()
    time = DateTimeField()

    @property
    def full_recommendation(self):
        return "**{} - {}**\n\t({}) - _{}_".format(self.artist, self.album, self.url, self.user.first_name)

    def __str__(self):
        return self.full_recommendation

