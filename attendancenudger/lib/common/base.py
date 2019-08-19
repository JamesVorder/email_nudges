from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml
import importlib.resources as pkg_resources
from attendancenudger import config

with pkg_resources.open_text(config, "config.yml") as ymlfile:
    conf = yaml.load(ymlfile, Loader=yaml.SafeLoader)

engine = create_engine(f'sqlite:///{conf["db"]["location"]}')
# use session_factory() to get a new Session
_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


def session_factory():
    Base.metadata.create_all(engine)
    return _SessionFactory()
