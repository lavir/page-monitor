__author__ = 'ned'

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///crawls.db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Url(Base):
  __tablename__ = 'urls'
  id = Column(Integer, primary_key=True, nullable=False, unique=True)
  url = Column(String, nullable=False, unique=True)

  pages = relationship("Page", backref="page_result")

class Page(Base):
  __tablename__ = 'pages'
  id = Column(Integer, primary_key=True, nullable=False, unique=True)
  timestamp = Column(DateTime, default=datetime.utcnow)
  page_md5 = Column(String, nullable=False)
  filename = Column(String, nullable=False)

  url_id = Column(Integer, ForeignKey('urls.id'), nullable=False)

Base.metadata.create_all(engine)