import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
DSN = 'postgresql://postgres:postgres@localhost:5432/nikolayshirokov'
engine = sq.create_engine(DSN)


class Users(Base):
    __tablename__ = 'users'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.String(length=20), unique=True, nullable=False)
    first_name = sq.Column(sq.String(length=20), unique=False, nullable=False)
    last_name = sq.Column(sq.String(length=20), unique=False, nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    sex = sq.Column(sq.String(length=7), nullable=False)
    city = sq.Column(sq.String(length=20), nullable=False)
    id_city = sq.Column(sq.Integer, nullable=False)


class Favorites(Base):
    __tablename__ = 'favorites'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.String(length=20), nullable=False)
    first_name = sq.Column(sq.String(length=20), unique=False, nullable=False)
    last_name = sq.Column(sq.String(length=20), unique=False, nullable=False)
    favorite_link_user = sq.Column(sq.String(length=50), unique=False, nullable=False)


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()