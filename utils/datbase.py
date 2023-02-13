from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

engine = create_engine('sqlite:///base.db')
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


def create_base():
    Base.metadata.create_all(engine)
