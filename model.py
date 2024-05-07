from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Base = declarative_base()

# ----------------------------------------------------------
                    # User model schema
# ----------------------------------------------------------
class User(Base):
    __tablename__ = "users"
    id = Column("id", Integer, primary_key=True)
    username = Column("username", CHAR(32), unique=True)
    words = relationship("WordsCount", backref="user")

    def __init__(self,id, username):
        self.id = id
        self.username = username

# ----------------------------------------------------------
                    # Words model schema
# ----------------------------------------------------------
class WordsCount(Base):
    __tablename__ = "words"
    id = Column("id", Integer, autoincrement=True, primary_key=True)
    word = Column("word", CHAR(64))
    count = Column("count", Integer, default=0)
    user_id = Column("user", Integer, ForeignKey("users.id"))


engine = create_engine("sqlite:///mydb.db", echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

