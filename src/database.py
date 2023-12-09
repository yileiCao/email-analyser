from sqlalchemy import create_engine
from src.config import DbConfig
from src.db_models import Base

engine = create_engine(url=DbConfig.url, echo=DbConfig.echo)
Base.metadata.create_all(bind=engine)
