from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker, declarative_base


# engine = create_engine("sqlite://", echo=True)
engine = create_engine("sqlite:////Users/yileicao/Documents/email-extraction/email.db", echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import db_models
    Base.metadata.create_all(bind=engine)