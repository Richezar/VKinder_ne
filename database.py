import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.String(length=20), unique=True, nullable=False)
    first_name = sq.Column(sq.String(length=20), unique=False, nullable=False)
    last_name = sq.Column(sq.String(length=20), unique=False, nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    sex = sq.Column(sq.String(length=7), nullable=False)
    city = sq.Column(sq.String(length=20), nullable=False)

def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)