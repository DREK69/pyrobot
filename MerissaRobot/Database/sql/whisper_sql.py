from sqlalchemy import JSON, BigInteger, Column, String

from MerissaRobot.Database.sql import BASE, SESSION


class Whispers(BASE):
    __tablename__ = "whispers"
    __table_args__ = {"extend_existing": True}
    specific = Column(String, primary_key=True)  # inline_message_id
    message = Column(String)

    def __init__(self, specific, message):
        self.specific = specific
        self.message = message

    def __repr__(self):
        return "<Whispers {} ({})>".format(self.message, self.specific)


Whispers.__table__.create(checkfirst=True)


def num_whispers():
    try:
        return SESSION.query(Whispers).count()
    finally:
        SESSION.close()


class Users(BASE):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    user_id = Column(BigInteger, primary_key=True)
    target_user = Column(JSON)

    def __init__(self, user_id, target_user=None):
        self.user_id = user_id
        self.target_user = target_user

    def __repr__(self):
        return "<User {} ({})>".format(self.target_user, self.user_id)


Users.__table__.create(checkfirst=True)


def num_users():
    try:
        return SESSION.query(Users).count()
    finally:
        SESSION.close()
